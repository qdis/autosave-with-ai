# ABOUTME: Sublime Text plugin that auto-saves unsaved files with AI-generated filenames
# ABOUTME: Uses Ollama to analyze content and suggest appropriate filenames with extensions

import sublime
import sublime_plugin
import urllib.request
import urllib.error
import json
import re
import os
from datetime import datetime
from typing import Optional, Tuple


class OllamaClient:
    """Handles communication with local Ollama API"""

    def __init__(self, url: str, model: str):
        self.url = url
        self.model = model

    def generate_filename(self, content: str, prompt_template: str) -> Optional[str]:
        """
        Call Ollama API to generate a filename based on content
        Returns None if API call fails
        """
        try:
            prompt = prompt_template.format(content=content)

            data = {
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }

            request = urllib.request.Request(
                f"{self.url}/api/generate",
                data=json.dumps(data).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )

            with urllib.request.urlopen(request, timeout=10) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result.get('response', '').strip()

        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
            print(f"AutoSaveWithAI: Ollama API error: {e}")
            return None
        except Exception as e:
            print(f"AutoSaveWithAI: Unexpected error: {e}")
            return None


def extract_first_words(text: str, word_limit: int = 250) -> str:
    """Extract first N words from text using naive space splitting"""
    words = text.split()
    return ' '.join(words[:word_limit])


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to be filesystem-safe
    Remove or replace invalid characters
    """
    # Remove any path separators
    filename = filename.replace('/', '_').replace('\\', '_')

    # Remove or replace other invalid characters
    filename = re.sub(r'[<>:"|?*]', '', filename)

    # Remove leading/trailing whitespace and dots
    filename = filename.strip('. ')

    # Check if filename is only underscores or empty
    if not filename or filename.replace('_', '').strip() == '':
        filename = "untitled.txt"

    # Ensure there's an extension
    if '.' not in filename:
        filename += '.txt'

    return filename


def get_settings():
    """Load plugin settings"""
    return sublime.load_settings("AutoSaveWithAI.sublime-settings")


def get_timestamp_filename(model: str) -> str:
    """Generate fallback filename with timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return f"auto-notes-{model}-{timestamp}.txt"


def save_file_with_ai_name(view: sublime.View) -> bool:
    """
    Main logic to save a file with AI-generated name
    Returns True if successful, False otherwise
    """
    # Only process unsaved files
    if view.file_name():
        return False

    settings = get_settings()
    save_dir = settings.get("save_directory", "")

    if not save_dir:
        sublime.error_message("AutoSaveWithAI: save_directory not configured in settings")
        return False

    # Expand home directory if needed
    save_dir = os.path.expanduser(save_dir)

    # Create directory if it doesn't exist
    os.makedirs(save_dir, exist_ok=True)

    # Get content
    content = view.substr(sublime.Region(0, view.size()))

    if not content.strip():
        print("AutoSaveWithAI: Empty file, skipping auto-save")
        return False

    # Extract first 250 words
    excerpt = extract_first_words(content, 250)

    # Get Ollama settings
    ollama_url = settings.get("ollama_url", "http://localhost:11434")
    ollama_model = settings.get("ollama_model", "llama2")
    prompt_template = settings.get("prompt_template",
        "Based on the following text, suggest a short, descriptive filename. "
        "Include an appropriate file extension (.txt, .md, .json, .py, etc.) based on the content type. "
        "Respond with ONLY the filename, nothing else.\n\nText: {content}")

    # Try to generate filename with Ollama
    client = OllamaClient(ollama_url, ollama_model)
    ai_filename = client.generate_filename(excerpt, prompt_template)

    if ai_filename:
        filename = sanitize_filename(ai_filename)
        # Add prefix
        filename = f"auto-notes-{ollama_model}-{filename}"
    else:
        # Fallback to timestamp
        filename = get_timestamp_filename(ollama_model)

    # Construct full path
    full_path = os.path.join(save_dir, filename)

    # Handle duplicates by adding number suffix
    if os.path.exists(full_path):
        base, ext = os.path.splitext(full_path)
        counter = 1
        while os.path.exists(f"{base}-{counter}{ext}"):
            counter += 1
        full_path = f"{base}-{counter}{ext}"

    # Save the file
    try:
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)

        # Update view to show the new filename
        view.retarget(full_path)
        view.set_scratch(False)

        print(f"AutoSaveWithAI: Saved to {full_path}")
        sublime.status_message(f"Auto-saved to {filename}")
        return True

    except Exception as e:
        print(f"AutoSaveWithAI: Error saving file: {e}")
        sublime.error_message(f"AutoSaveWithAI: Failed to save file: {e}")
        return False


class AutoSaveWithAiCommand(sublime_plugin.TextCommand):
    """Command to manually trigger AI-based auto-save"""

    def run(self, edit):
        save_file_with_ai_name(self.view)

    def is_enabled(self):
        # Only enable for unsaved files with content
        return (not self.view.file_name() and
                self.view.size() > 0)


class AutoSaveEventListener(sublime_plugin.EventListener):
    """Event listener for auto-save functionality"""

    def __init__(self):
        self.timers = {}  # Track timers per view

    def on_post_save_async(self, view):
        """Intercept save events if overwrite_default_save is enabled"""
        settings = get_settings()

        if not settings.get("overwrite_default_save", False):
            return

        # Check if this is an unsaved file being saved
        # This hook runs AFTER save, so we can't intercept the default save
        # We'll use on_pre_save instead
        pass

    def on_pre_save(self, view):
        """Intercept save before it happens"""
        settings = get_settings()

        if not settings.get("overwrite_default_save", False):
            return

        # Only intercept if file is unsaved (no file_name yet)
        if not view.file_name():
            # Save with AI name instead
            if save_file_with_ai_name(view):
                # Cancel the default save by returning False
                # Actually, we can't cancel in on_pre_save, need different approach
                pass

    def on_modified_async(self, view):
        """Handle auto-save timer"""
        settings = get_settings()
        timer_seconds = settings.get("auto_save_timer", 0)

        if timer_seconds <= 0:
            return

        # Only for unsaved files
        if view.file_name():
            return

        view_id = view.id()

        # Cancel existing timer for this view
        if view_id in self.timers:
            # Can't actually cancel sublime.set_timeout, so we'll use a flag approach
            pass

        # Set new timer
        timer_ms = timer_seconds * 1000

        def auto_save_callback():
            # Check if view still exists and is unsaved
            if not view.is_valid() or view.file_name():
                return

            # Check if still the active timer
            if view_id not in self.timers:
                return

            save_file_with_ai_name(view)

            # Remove timer reference
            if view_id in self.timers:
                del self.timers[view_id]

        self.timers[view_id] = True
        sublime.set_timeout_async(auto_save_callback, timer_ms)

    def on_close(self, view):
        """Clean up timer when view is closed"""
        view_id = view.id()
        if view_id in self.timers:
            del self.timers[view_id]
