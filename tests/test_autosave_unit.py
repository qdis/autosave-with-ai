# ABOUTME: Unit tests for AutoSaveWithAI plugin with mocked HTTP client
# ABOUTME: Tests core functionality without requiring actual API calls

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
    AIClient
)
import ai_client


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


class TestAIClient(unittest.TestCase):
    """Test the AIClient class"""

    def setUp(self):
        """Set up test client"""
        self.client = AIClient(
            model="gpt-3.5-turbo",
            api_key="test-key",
            api_base="https://api.openai.com/v1",
            api_type="chat"
        )

    @patch('AutoSaveWithAI.AI_CLIENT_AVAILABLE', True)
    @patch('ai_client.chat_completion')
    def test_successful_generation_chat(self, mock_chat):
        """Test successful filename generation with Chat Completions API"""
        # Mock successful API response
        mock_chat.return_value = {
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
        # Verify chat_completion was called with correct arguments
        self.assertTrue(mock_chat.called)
        call_args = mock_chat.call_args[1]
        self.assertEqual(call_args['model'], 'gpt-3.5-turbo')
        self.assertEqual(len(call_args['messages']), 1)
        self.assertIn("Generate filename: This is a test", call_args['messages'][0]['content'])

    @patch('AutoSaveWithAI.AI_CLIENT_AVAILABLE', True)
    @patch('ai_client.responses_create')
    def test_successful_generation_responses(self, mock_responses):
        """Test successful filename generation with Responses API"""
        # Mock successful API response
        mock_responses.return_value = {
            'output_text': 'meeting-notes.md'
        }

        client = AIClient(
            model="gpt-4o",
            api_key="test-key",
            api_base="https://api.openai.com/v1",
            api_type="responses"
        )

        result = client.generate_filename(
            "This is a test",
            "Generate filename: {content}"
        )

        self.assertEqual(result, "meeting-notes.md")
        # Verify responses_create was called
        self.assertTrue(mock_responses.called)

    @patch('AutoSaveWithAI.AI_CLIENT_AVAILABLE', True)
    @patch('ai_client.chat_completion')
    def test_authentication_error(self, mock_chat):
        """Test handling of authentication error"""
        mock_chat.side_effect = ai_client.OpenAIHTTPError("HTTP 401: Unauthorized")

        result = self.client.generate_filename(
            "This is a test",
            "Generate filename: {content}"
        )

        self.assertIsNone(result)

    @patch('AutoSaveWithAI.AI_CLIENT_AVAILABLE', True)
    @patch('ai_client.chat_completion')
    def test_api_timeout(self, mock_chat):
        """Test handling of API timeout"""
        mock_chat.side_effect = Exception("Timeout")

        result = self.client.generate_filename(
            "This is a test",
            "Generate filename: {content}"
        )

        self.assertIsNone(result)

    @patch('AutoSaveWithAI.AI_CLIENT_AVAILABLE', True)
    @patch('ai_client.chat_completion')
    def test_api_connection_error(self, mock_chat):
        """Test handling of connection error"""
        mock_chat.side_effect = Exception("Connection refused")

        result = self.client.generate_filename(
            "This is a test",
            "Generate filename: {content}"
        )

        self.assertIsNone(result)

    @patch('AutoSaveWithAI.AI_CLIENT_AVAILABLE', False)
    def test_ai_client_not_available(self):
        """Test handling when ai_client module is not available"""
        result = self.client.generate_filename(
            "This is a test",
            "Generate filename: {content}"
        )

        self.assertIsNone(result)

    def test_no_api_key(self):
        """Test handling when no API key is provided"""
        client = AIClient(
            model="gpt-4",
            api_key=None,
            api_base="https://api.openai.com/v1"
        )
        result = client.generate_filename("Test", "Generate: {content}")

        self.assertIsNone(result)

    def test_no_api_base(self):
        """Test handling when no API base is provided"""
        client = AIClient(
            model="gpt-4",
            api_key="test-key",
            api_base=None
        )
        result = client.generate_filename("Test", "Generate: {content}")

        self.assertIsNone(result)

    @patch('AutoSaveWithAI.AI_CLIENT_AVAILABLE', True)
    @patch('ai_client.chat_completion')
    def test_with_custom_auth(self, mock_chat):
        """Test that custom auth headers are passed correctly"""
        mock_chat.return_value = {
            'choices': [{
                'message': {
                    'content': 'test.txt'
                }
            }]
        }

        client = AIClient(
            model="gpt-4",
            api_key="azure-key",
            api_base="https://azure.openai.com/v1",
            api_type="chat",
            auth_header_name="api-key",
            auth_header_prefix=""
        )
        result = client.generate_filename("Test", "Generate: {content}")

        self.assertEqual(result, "test.txt")
        call_args = mock_chat.call_args[1]
        self.assertEqual(call_args['auth_header_name'], "api-key")
        self.assertEqual(call_args['auth_header_prefix'], "")


if __name__ == '__main__':
    unittest.main()
