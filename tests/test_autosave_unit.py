# ABOUTME: Unit tests for AutoSaveWithAI plugin with mocked Ollama API
# ABOUTME: Tests core functionality without requiring running Ollama instance

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
import json

# Add parent directory to path to import the plugin
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock sublime and sublime_plugin modules before importing
sys.modules['sublime'] = MagicMock()
sys.modules['sublime_plugin'] = MagicMock()

# Import the functions we want to test
from AutoSaveWithAI import (
    extract_first_words,
    sanitize_filename,
    get_timestamp_filename,
    OllamaClient
)


class TestExtractFirstWords(unittest.TestCase):
    """Test the extract_first_words function"""

    def test_extract_less_than_limit(self):
        """Test extraction when text has fewer words than limit"""
        text = "Hello world this is a test"
        result = extract_first_words(text, 10)
        self.assertEqual(result, "Hello world this is a test")

    def test_extract_exactly_limit(self):
        """Test extraction when text has exactly the limit"""
        text = " ".join([f"word{i}" for i in range(250)])
        result = extract_first_words(text, 250)
        self.assertEqual(len(result.split()), 250)

    def test_extract_more_than_limit(self):
        """Test extraction when text exceeds limit"""
        text = " ".join([f"word{i}" for i in range(300)])
        result = extract_first_words(text, 250)
        self.assertEqual(len(result.split()), 250)

    def test_empty_string(self):
        """Test extraction with empty string"""
        result = extract_first_words("", 250)
        self.assertEqual(result, "")

    def test_whitespace_only(self):
        """Test extraction with only whitespace"""
        result = extract_first_words("   \n  \t  ", 250)
        self.assertEqual(result, "")


class TestSanitizeFilename(unittest.TestCase):
    """Test the sanitize_filename function"""

    def test_valid_filename(self):
        """Test already valid filename"""
        result = sanitize_filename("notes.txt")
        self.assertEqual(result, "notes.txt")

    def test_remove_path_separators(self):
        """Test removal of path separators"""
        result = sanitize_filename("path/to/file.txt")
        self.assertEqual(result, "path_to_file.txt")

        result = sanitize_filename("path\\to\\file.txt")
        self.assertEqual(result, "path_to_file.txt")

    def test_remove_invalid_characters(self):
        """Test removal of invalid filesystem characters"""
        result = sanitize_filename("file<name>:test|?.txt")
        self.assertEqual(result, "filenametest.txt")

    def test_add_extension_if_missing(self):
        """Test adding .txt extension if none exists"""
        result = sanitize_filename("filename")
        self.assertEqual(result, "filename.txt")

    def test_strip_leading_trailing(self):
        """Test stripping leading/trailing whitespace and dots"""
        result = sanitize_filename("  ...filename.txt...  ")
        self.assertEqual(result, "filename.txt")

    def test_empty_filename_fallback(self):
        """Test fallback for completely invalid filename"""
        result = sanitize_filename("///:::|||")
        self.assertEqual(result, "untitled.txt")

    def test_preserve_valid_extensions(self):
        """Test that valid extensions are preserved"""
        test_cases = [
            ("notes.md", "notes.md"),
            ("data.json", "data.json"),
            ("script.py", "script.py"),
        ]
        for input_name, expected in test_cases:
            result = sanitize_filename(input_name)
            self.assertEqual(result, expected)


class TestGetTimestampFilename(unittest.TestCase):
    """Test the get_timestamp_filename function"""

    def test_format(self):
        """Test that timestamp filename has correct format"""
        result = get_timestamp_filename("llama2")
        self.assertTrue(result.startswith("auto-notes-llama2-"))
        self.assertTrue(result.endswith(".txt"))

    def test_different_models(self):
        """Test with different model names"""
        models = ["llama2", "mistral", "codellama"]
        for model in models:
            result = get_timestamp_filename(model)
            self.assertIn(model, result)


class TestOllamaClient(unittest.TestCase):
    """Test the OllamaClient class"""

    def setUp(self):
        """Set up test client"""
        self.client = OllamaClient("http://localhost:11434", "llama2")

    @patch('urllib.request.urlopen')
    def test_successful_generation(self, mock_urlopen):
        """Test successful filename generation"""
        # Mock successful API response
        mock_response = Mock()
        mock_response.read.return_value = json.dumps({
            "response": "meeting-notes.md"
        }).encode('utf-8')
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)
        mock_urlopen.return_value = mock_response

        result = self.client.generate_filename(
            "This is a test",
            "Generate filename: {content}"
        )

        self.assertEqual(result, "meeting-notes.md")

    @patch('urllib.request.urlopen')
    def test_api_timeout(self, mock_urlopen):
        """Test handling of API timeout"""
        mock_urlopen.side_effect = TimeoutError("Connection timeout")

        result = self.client.generate_filename(
            "This is a test",
            "Generate filename: {content}"
        )

        self.assertIsNone(result)

    @patch('urllib.request.urlopen')
    def test_api_connection_error(self, mock_urlopen):
        """Test handling of connection error"""
        import urllib.error
        mock_urlopen.side_effect = urllib.error.URLError("Connection refused")

        result = self.client.generate_filename(
            "This is a test",
            "Generate filename: {content}"
        )

        self.assertIsNone(result)

    @patch('urllib.request.urlopen')
    def test_api_http_error(self, mock_urlopen):
        """Test handling of HTTP error"""
        import urllib.error
        mock_urlopen.side_effect = urllib.error.HTTPError(
            "http://localhost:11434/api/generate",
            500,
            "Internal Server Error",
            {},
            None
        )

        result = self.client.generate_filename(
            "This is a test",
            "Generate filename: {content}"
        )

        self.assertIsNone(result)

    @patch('urllib.request.urlopen')
    def test_malformed_json_response(self, mock_urlopen):
        """Test handling of malformed JSON response"""
        mock_response = Mock()
        mock_response.read.return_value = b"not valid json"
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)
        mock_urlopen.return_value = mock_response

        result = self.client.generate_filename(
            "This is a test",
            "Generate filename: {content}"
        )

        self.assertIsNone(result)

    @patch('urllib.request.urlopen')
    def test_prompt_template_formatting(self, mock_urlopen):
        """Test that prompt template is correctly formatted"""
        mock_response = Mock()
        mock_response.read.return_value = json.dumps({
            "response": "test.txt"
        }).encode('utf-8')
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)
        mock_urlopen.return_value = mock_response

        content = "Sample content"
        template = "Content: {content}"

        self.client.generate_filename(content, template)

        # Verify the request was made
        self.assertTrue(mock_urlopen.called)

        # Get the request object that was passed
        request = mock_urlopen.call_args[0][0]
        request_data = json.loads(request.data.decode('utf-8'))

        self.assertIn("prompt", request_data)
        self.assertEqual(request_data["prompt"], f"Content: {content}")


if __name__ == '__main__':
    unittest.main()
