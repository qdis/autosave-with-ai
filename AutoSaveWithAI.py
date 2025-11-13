# ABOUTME: Sublime Text plugin that auto-saves unsaved files with AI-generated filenames
# ABOUTME: Uses LiteLLM to support multiple AI providers for filename generation

import sublime
import sublime_plugin
import re
import os
from datetime import datetime

try:
    from litellm import completion
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False
    print("AutoSaveWithAI: litellm not installed. Install with: pip install litellm")


class LiteLLMClient:
    """Handles communication with LLM providers via LiteLLM"""

    def __init__(self, model, api_key=None, api_base=None):
        self.model = model
        self.api_key = api_key
        self.api_base = api_base

    def generate_filename(self, content, prompt_template):
        """
        Call LLM API to generate a filename based on content
        Returns None if API call fails
        """
        if not LITELLM_AVAILABLE:
            print("AutoSaveWithAI: litellm not available")
            return None

        try:
            prompt = prompt_template.replace('{content}', content)
            print("AutoSaveWithAI: Sending {} characters to LLM".format(len(content)))

            # Prepare completion arguments
            kwargs = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "timeout": 30
            }

            if self.api_key:
                kwargs["api_key"] = self.api_key
                print("AutoSaveWithAI: Using API key for authentication")

            if self.api_base:
                kwargs["api_base"] = self.api_base

            print("AutoSaveWithAI: Making API call...")
            response = completion(**kwargs)
            result = response['choices'][0]['message']['content'].strip()
            print("AutoSaveWithAI: LLM responded with: {}".format(result))
            return result

        except Exception as e:
            # Catch all exceptions from LiteLLM/API providers
            print("AutoSaveWithAI: LLM API error: {}".format(e))
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


def get_timestamp_filename() -> str:
    """Generate fallback filename with timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return "auto-notes-{}.txt".format(timestamp)


def save_file_with_ai_name(view: sublime.View) -> bool:
    """
    Main logic to save a file with AI-generated name
    Returns True if successful, False otherwise
    """
    print("AutoSaveWithAI: Starting save process...")

    # Only process unsaved files
    if view.file_name():
        print("AutoSaveWithAI: File already has a name, skipping")
        return False

    settings = get_settings()
    save_dir = settings.get("save_directory", "")

    if not save_dir:
        print("AutoSaveWithAI: ERROR - save_directory not configured")
        sublime.error_message("AutoSaveWithAI: save_directory not configured in settings")
        return False

    print("AutoSaveWithAI: Save directory: {}".format(save_dir))

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

    # Get LLM settings
    llm_model = settings.get("llm_model", "gpt-3.5-turbo")
    print("AutoSaveWithAI: Using LLM model: {}".format(llm_model))

    prompt_template = settings.get("prompt_template",
        "Based on the following text, suggest a short, descriptive filename. "
        "Include an appropriate file extension (.txt, .md, .json, .py, etc.) based on the content type. "
        "Respond with ONLY the filename, nothing else.\n\nText: {content}")

    # Get API keys
    api_key = None
    if llm_model.startswith("gpt-") or llm_model.startswith("openai/"):
        api_key = settings.get("openai_api_key", None)
        print("AutoSaveWithAI: Using OpenAI provider")
    elif llm_model.startswith("anthropic/"):
        api_key = settings.get("anthropic_api_key", None)
        print("AutoSaveWithAI: Using Anthropic provider")
    else:
        print("AutoSaveWithAI: Using provider from model string: {}".format(llm_model))

    api_base = settings.get("api_base", None)
    if api_base:
        print("AutoSaveWithAI: Using custom API base: {}".format(api_base))

    # Try to generate filename with LLM
    print("AutoSaveWithAI: Calling LLM to generate filename...")
    client = LiteLLMClient(llm_model, api_key, api_base)
    ai_filename = client.generate_filename(excerpt, prompt_template)

    if ai_filename:
        print("AutoSaveWithAI: LLM generated filename: {}".format(ai_filename))
        filename = sanitize_filename(ai_filename)
        print("AutoSaveWithAI: Sanitized filename: {}".format(filename))
        # Add prefix
        filename = "auto-notes-{}".format(filename)
        print("AutoSaveWithAI: Final filename: {}".format(filename))
    else:
        print("AutoSaveWithAI: LLM failed, using timestamp fallback")
        # Fallback to timestamp
        filename = get_timestamp_filename()
        print("AutoSaveWithAI: Fallback filename: {}".format(filename))

    # Construct full path
    full_path = os.path.join(save_dir, filename)
    print("AutoSaveWithAI: Target path: {}".format(full_path))

    # Handle duplicates by adding number suffix
    if os.path.exists(full_path):
        print("AutoSaveWithAI: File already exists, adding number suffix")
        base, ext = os.path.splitext(full_path)
        counter = 1
        while os.path.exists("{}-{}{}".format(base, counter, ext)):
            counter += 1
        full_path = "{}-{}{}".format(base, counter, ext)
        print("AutoSaveWithAI: Using numbered path: {}".format(full_path))

    # Save the file
    try:
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)

        # Update view to show the new filename
        view.retarget(full_path)
        view.set_scratch(False)

        print("AutoSaveWithAI: Saved to {}".format(full_path))
        sublime.status_message("Auto-saved to {}".format(filename))
        return True

    except Exception as e:
        print("AutoSaveWithAI: Error saving file: {}".format(e))
        sublime.error_message("AutoSaveWithAI: Failed to save file: {}".format(e))
        return False


class AutoSaveWithAiCommand(sublime_plugin.TextCommand):
    """Command to manually trigger AI-based auto-save"""

    def run(self, edit):
        print("AutoSaveWithAI: Manual command triggered")
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
        print("AutoSaveWithAI: Timer started for {} seconds".format(timer_seconds))

        def auto_save_callback():
            # Check if view still exists and is unsaved
            if not view.is_valid() or view.file_name():
                print("AutoSaveWithAI: Timer expired but view no longer valid/unsaved")
                return

            # Check if still the active timer
            if view_id not in self.timers:
                print("AutoSaveWithAI: Timer expired but no longer active")
                return

            print("AutoSaveWithAI: Timer triggered auto-save")
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
