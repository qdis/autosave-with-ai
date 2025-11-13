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
# Mock litellm and openai modules
sys.modules['litellm'] = MagicMock()
sys.modules['openai'] = MagicMock()

# Import the functions we want to test
from AutoSaveWithAI import (
    extract_first_words,
    sanitize_filename,
    get_timestamp_filename,
    LiteLLMClient
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
        result = get_timestamp_filename()
        self.assertTrue(result.startswith("auto-notes-"))
        self.assertTrue(result.endswith(".txt"))
        # Should contain timestamp pattern YYYYMMDD-HHMMSS
        self.assertRegex(result, r'auto-notes-\d{8}-\d{6}\.txt')


class TestLiteLLMClient(unittest.TestCase):
    """Test the LiteLLMClient class"""

    def setUp(self):
        """Set up test client"""
        self.client = LiteLLMClient("gpt-3.5-turbo")

    @patch('AutoSaveWithAI.LITELLM_AVAILABLE', True)
    @patch('AutoSaveWithAI.completion')
    def test_successful_generation(self, mock_completion):
        """Test successful filename generation"""
        # Mock successful API response
        mock_completion.return_value = {
            'choices': [{
                'message': {
                    'content': 'meeting-notes.md'
                }
            }]
        }

        result = self.client.generate_filename(
            "This is a test",
            "Generate filename: {content}"
        )

        self.assertEqual(result, "meeting-notes.md")
        # Verify completion was called with correct arguments
        self.assertTrue(mock_completion.called)
        call_args = mock_completion.call_args[1]
        self.assertEqual(call_args['model'], 'gpt-3.5-turbo')
        self.assertEqual(len(call_args['messages']), 1)
        self.assertIn("Generate filename: This is a test", call_args['messages'][0]['content'])

    @patch('AutoSaveWithAI.LITELLM_AVAILABLE', True)
    @patch('AutoSaveWithAI.completion')
    def test_authentication_error(self, mock_completion):
        """Test handling of authentication error"""
        # Create a mock AuthenticationError
        mock_completion.side_effect = Exception("Invalid API key")

        result = self.client.generate_filename(
            "This is a test",
            "Generate filename: {content}"
        )

        self.assertIsNone(result)

    @patch('AutoSaveWithAI.LITELLM_AVAILABLE', True)
    @patch('AutoSaveWithAI.completion')
    def test_api_timeout(self, mock_completion):
        """Test handling of API timeout"""
        mock_completion.side_effect = Exception("Timeout")

        result = self.client.generate_filename(
            "This is a test",
            "Generate filename: {content}"
        )

        self.assertIsNone(result)

    @patch('AutoSaveWithAI.LITELLM_AVAILABLE', True)
    @patch('AutoSaveWithAI.completion')
    def test_api_connection_error(self, mock_completion):
        """Test handling of connection error"""
        mock_completion.side_effect = Exception("Connection refused")

        result = self.client.generate_filename(
            "This is a test",
            "Generate filename: {content}"
        )

        self.assertIsNone(result)

    @patch('AutoSaveWithAI.LITELLM_AVAILABLE', False)
    def test_litellm_not_available(self):
        """Test handling when litellm is not installed"""
        result = self.client.generate_filename(
            "This is a test",
            "Generate filename: {content}"
        )

        self.assertIsNone(result)

    @patch('AutoSaveWithAI.LITELLM_AVAILABLE', True)
    @patch('AutoSaveWithAI.completion')
    def test_with_api_key(self, mock_completion):
        """Test that API key is passed correctly"""
        mock_completion.return_value = {
            'choices': [{
                'message': {
                    'content': 'test.txt'
                }
            }]
        }

        client = LiteLLMClient("gpt-4", api_key="test-key-123")
        result = client.generate_filename("Test", "Generate: {content}")

        self.assertEqual(result, "test.txt")
        call_args = mock_completion.call_args[1]
        self.assertEqual(call_args['api_key'], "test-key-123")

    @patch('AutoSaveWithAI.LITELLM_AVAILABLE', True)
    @patch('AutoSaveWithAI.completion')
    def test_with_api_base(self, mock_completion):
        """Test that API base is passed correctly"""
        mock_completion.return_value = {
            'choices': [{
                'message': {
                    'content': 'test.txt'
                }
            }]
        }

        client = LiteLLMClient("gpt-4", api_base="http://localhost:8000")
        result = client.generate_filename("Test", "Generate: {content}")

        self.assertEqual(result, "test.txt")
        call_args = mock_completion.call_args[1]
        self.assertEqual(call_args['api_base'], "http://localhost:8000")


if __name__ == '__main__':
    unittest.main()
