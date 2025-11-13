# ABOUTME: Integration tests for AutoSaveWithAI plugin requiring real API access
# ABOUTME: Tests actual API calls and end-to-end filename generation with OpenAI-compatible endpoints

import unittest
import sys
import os
from unittest.mock import MagicMock

# Add parent directory to path to import the plugin
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock sublime and sublime_plugin modules before importing
sys.modules['sublime'] = MagicMock()
sys.modules['sublime_plugin'] = MagicMock()

from AutoSaveWithAI import AIClient, extract_first_words, AI_CLIENT_AVAILABLE


def get_test_config():
    """Get test configuration from environment variables or use defaults"""
    return {
        'model': os.environ.get('TEST_MODEL', 'gpt-3.5-turbo'),
        'api_key': os.environ.get('TEST_API_KEY', ''),
        'api_base': os.environ.get('TEST_API_BASE', 'https://api.openai.com/v1'),
        'api_type': os.environ.get('TEST_API_TYPE', 'chat'),
    }


@unittest.skipUnless(AI_CLIENT_AVAILABLE, "ai_client module is not available")
@unittest.skipUnless(get_test_config()['api_key'], "TEST_API_KEY environment variable not set")
class TestAIClientIntegration(unittest.TestCase):
    """Integration tests that require actual API access"""

    def setUp(self):
        """Set up test client"""
        config = get_test_config()
        self.client = AIClient(
            model=config['model'],
            api_key=config['api_key'],
            api_base=config['api_base'],
            api_type=config['api_type']
        )

    def test_generate_filename_for_meeting_notes(self):
        """Test filename generation for meeting notes content"""
        content = """
        Team meeting on January 15th.
        Discussed project timeline and deliverables.
        Action items: Update documentation, schedule follow-up meeting.
        """

        prompt = ("Based on the following text, suggest a short, descriptive filename. "
                 "Include an appropriate file extension (.txt, .md, .json, .py, etc.) "
                 "based on the content type. Respond with ONLY the filename, nothing else.\n\n"
                 "Text: {content}")

        result = self.client.generate_filename(content, prompt)

        self.assertIsNotNone(result)
        self.assertGreater(len(result), 0)
        # Should have some kind of extension
        self.assertIn('.', result)
        print("Generated filename for meeting notes: {}".format(result))

    def test_generate_filename_for_code(self):
        """Test filename generation for code content"""
        content = """
        def calculate_fibonacci(n):
            if n <= 1:
                return n
            return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)
        """

        prompt = ("Based on the following text, suggest a short, descriptive filename. "
                 "Include an appropriate file extension (.txt, .md, .json, .py, etc.) "
                 "based on the content type. Respond with ONLY the filename, nothing else.\n\n"
                 "Text: {content}")

        result = self.client.generate_filename(content, prompt)

        self.assertIsNotNone(result)
        self.assertGreater(len(result), 0)
        print("Generated filename for code: {}".format(result))
        # Should recognize it's code
        self.assertIn('.', result)

    def test_generate_filename_for_json(self):
        """Test filename generation for JSON content"""
        content = """
        {
            "name": "John Doe",
            "age": 30,
            "city": "New York",
            "interests": ["programming", "music", "hiking"]
        }
        """

        prompt = ("Based on the following text, suggest a short, descriptive filename. "
                 "Include an appropriate file extension (.txt, .md, .json, .py, etc.) "
                 "based on the content type. Respond with ONLY the filename, nothing else.\n\n"
                 "Text: {content}")

        result = self.client.generate_filename(content, prompt)

        self.assertIsNotNone(result)
        self.assertGreater(len(result), 0)
        print("Generated filename for JSON: {}".format(result))
        # Should recognize JSON format
        self.assertIn('.', result)

    def test_generate_filename_for_markdown(self):
        """Test filename generation for markdown content"""
        content = """
        # Project Documentation

        ## Overview
        This project provides a simple API for data processing.

        ## Features
        - Fast processing
        - Easy to use
        - Well documented
        """

        prompt = ("Based on the following text, suggest a short, descriptive filename. "
                 "Include an appropriate file extension (.txt, .md, .json, .py, etc.) "
                 "based on the content type. Respond with ONLY the filename, nothing else.\n\n"
                 "Text: {content}")

        result = self.client.generate_filename(content, prompt)

        self.assertIsNotNone(result)
        self.assertGreater(len(result), 0)
        print("Generated filename for markdown: {}".format(result))
        self.assertIn('.', result)

    def test_with_long_content(self):
        """Test filename generation with content that needs truncation"""
        # Create content longer than 250 words
        words = ["word"] * 500
        content = " ".join(words)

        # Truncate to first 250 words
        excerpt = extract_first_words(content, 250)

        prompt = ("Based on the following text, suggest a short, descriptive filename. "
                 "Include an appropriate file extension (.txt, .md, .json, .py, etc.) "
                 "based on the content type. Respond with ONLY the filename, nothing else.\n\n"
                 "Text: {content}")

        result = self.client.generate_filename(excerpt, prompt)

        self.assertIsNotNone(result)
        self.assertGreater(len(result), 0)
        print("Generated filename for long content: {}".format(result))


@unittest.skipUnless(AI_CLIENT_AVAILABLE, "ai_client module is not available")
class TestAPIUnavailable(unittest.TestCase):
    """Test behavior when API service is not available"""

    def test_graceful_failure_with_invalid_api_base(self):
        """Test that client returns None when API is not accessible"""
        client = AIClient(
            model="gpt-3.5-turbo",
            api_key="fake-key",
            api_base="http://localhost:99999",  # Invalid port
            api_type="chat"
        )

        result = client.generate_filename(
            "Test content",
            "Generate filename: {content}"
        )

        self.assertIsNone(result)
        print("Correctly returned None when API not accessible")


if __name__ == '__main__':
    # Run with verbose output to see generated filenames
    unittest.main(verbosity=2)
