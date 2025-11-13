# ABOUTME: Integration tests for AutoSaveWithAI plugin requiring running Ollama
# ABOUTME: Tests actual API calls and end-to-end filename generation

import unittest
import sys
import os
import urllib.request
import urllib.error
import json
from unittest.mock import MagicMock

# Add parent directory to path to import the plugin
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock sublime and sublime_plugin modules before importing
sys.modules['sublime'] = MagicMock()
sys.modules['sublime_plugin'] = MagicMock()

from AutoSaveWithAI import OllamaClient, extract_first_words


def is_ollama_running(url="http://localhost:11434"):
    """Check if Ollama is running and accessible"""
    try:
        request = urllib.request.Request(f"{url}/api/tags")
        with urllib.request.urlopen(request, timeout=2) as response:
            return response.status == 200
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError):
        return False


@unittest.skipUnless(is_ollama_running(), "Ollama is not running")
class TestOllamaIntegration(unittest.TestCase):
    """Integration tests that require Ollama to be running"""

    def setUp(self):
        """Set up test client"""
        self.url = "http://localhost:11434"
        self.model = "llama2"  # Use a common model
        self.client = OllamaClient(self.url, self.model)

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
                 f"Text: {content}")

        result = self.client.generate_filename(content, prompt)

        self.assertIsNotNone(result)
        self.assertGreater(len(result), 0)
        # Should have some kind of extension
        self.assertIn('.', result)
        print(f"Generated filename for meeting notes: {result}")

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
                 f"Text: {content}")

        result = self.client.generate_filename(content, prompt)

        self.assertIsNotNone(result)
        self.assertGreater(len(result), 0)
        print(f"Generated filename for code: {result}")
        # Ideally should suggest .py, but we can't guarantee AI behavior
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
                 f"Text: {content}")

        result = self.client.generate_filename(content, prompt)

        self.assertIsNotNone(result)
        self.assertGreater(len(result), 0)
        print(f"Generated filename for JSON: {result}")
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
                 f"Text: {content}")

        result = self.client.generate_filename(content, prompt)

        self.assertIsNotNone(result)
        self.assertGreater(len(result), 0)
        print(f"Generated filename for markdown: {result}")
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
                 f"Text: {excerpt}")

        result = self.client.generate_filename(excerpt, prompt)

        self.assertIsNotNone(result)
        self.assertGreater(len(result), 0)
        print(f"Generated filename for long content: {result}")

    def test_empty_content_handling(self):
        """Test how Ollama handles empty or minimal content"""
        content = "."

        prompt = ("Based on the following text, suggest a short, descriptive filename. "
                 "Include an appropriate file extension (.txt, .md, .json, .py, etc.) "
                 "based on the content type. Respond with ONLY the filename, nothing else.\n\n"
                 f"Text: {content}")

        result = self.client.generate_filename(content, prompt)

        # Should still return something
        self.assertIsNotNone(result)
        print(f"Generated filename for minimal content: {result}")


class TestOllamaNotRunning(unittest.TestCase):
    """Test behavior when Ollama is not running"""

    @unittest.skipIf(is_ollama_running(), "Skip when Ollama is running")
    def test_graceful_failure_when_ollama_down(self):
        """Test that client returns None when Ollama is not accessible"""
        client = OllamaClient("http://localhost:11434", "llama2")

        result = client.generate_filename(
            "Test content",
            "Generate filename: {content}"
        )

        self.assertIsNone(result)
        print("Correctly returned None when Ollama not running")


if __name__ == '__main__':
    # Run with verbose output to see generated filenames
    unittest.main(verbosity=2)
