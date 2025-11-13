# AutoSaveWithAI - Sublime Text Plugin

A Sublime Text plugin that automatically saves unsaved files with AI-generated filenames using Ollama.

## Features

- **AI-Powered Filename Generation**: Uses local Ollama to analyze file content and suggest appropriate filenames
- **Smart Extension Detection**: Automatically detects content type (JSON, Markdown, Python, etc.) and adds appropriate extensions
- **Multiple Trigger Options**:
  - Manual command via Command Palette
  - Auto-save on timer (configurable seconds of inactivity)
  - Intercept default save action (Ctrl+S/Cmd+S) for unsaved files
- **Fallback Mechanism**: Uses timestamp-based naming when Ollama is unavailable
- **Configurable**: Customize save directory, Ollama model, prompts, and behavior

## Requirements

- Sublime Text 4 (Python 3.8+)
- [Ollama](https://ollama.ai/) installed and running locally
- An Ollama model downloaded (e.g., `llama2`, `mistral`, `codellama`)

## Installation

### Option 1: Manual Installation

1. Clone or download this repository
2. Copy the plugin files to your Sublime Text Packages directory:
   - **macOS**: `~/Library/Application Support/Sublime Text/Packages/AutoSaveWithAI/`
   - **Linux**: `~/.config/sublime-text/Packages/AutoSaveWithAI/`
   - **Windows**: `%APPDATA%\Sublime Text\Packages\AutoSaveWithAI\`

3. Restart Sublime Text

### Option 2: Symlink (for development)

```bash
# macOS/Linux
ln -s /path/to/sublime-autosave-with-ai ~/Library/Application\ Support/Sublime\ Text/Packages/AutoSaveWithAI

# Windows (run as Administrator)
mklink /D "%APPDATA%\Sublime Text\Packages\AutoSaveWithAI" "C:\path\to\sublime-autosave-with-ai"
```

## Ollama Setup

1. Install Ollama from [ollama.ai](https://ollama.ai/)
2. Download a model:
   ```bash
   ollama pull llama2
   ```
3. Verify Ollama is running:
   ```bash
   ollama list
   ```

## Configuration

Open Sublime Text settings: `Preferences > Package Settings > AutoSaveWithAI > Settings`

### Default Settings

```json
{
    "save_directory": "~/Documents/auto-notes",
    "ollama_url": "http://localhost:11434",
    "ollama_model": "llama2",
    "overwrite_default_save": false,
    "auto_save_timer": 0,
    "prompt_template": "Based on the following text, suggest a short, descriptive filename. Include an appropriate file extension (.txt, .md, .json, .py, etc.) based on the content type. Respond with ONLY the filename, nothing else.\n\nText: {content}"
}
```

### Configuration Options

- **`save_directory`**: Directory where files will be saved (supports `~/` for home directory)
- **`ollama_url`**: Ollama API endpoint (default: `http://localhost:11434`)
- **`ollama_model`**: Model to use for generation (e.g., `llama2`, `mistral`, `codellama`)
- **`overwrite_default_save`**: If `true`, intercepts Ctrl+S/Cmd+S on unsaved files
- **`auto_save_timer`**: Seconds of inactivity before auto-save (0 = disabled)
- **`prompt_template`**: Template for AI prompt (`{content}` is replaced with file content)

## Usage

### Method 1: Command Palette

1. Create or open an unsaved file
2. Open Command Palette (Ctrl+Shift+P / Cmd+Shift+P)
3. Run "Auto Save with AI Name"

### Method 2: Auto-Save Timer

Set `auto_save_timer` to a number of seconds (e.g., `30`):

```json
{
    "auto_save_timer": 30
}
```

Files will automatically save after 30 seconds of inactivity.

### Method 3: Override Default Save

Enable in settings:

```json
{
    "overwrite_default_save": true
}
```

Now pressing Ctrl+S/Cmd+S on an unsaved file will trigger AI naming.

## Filename Format

Generated filenames follow this pattern:

```
auto-notes-{model}-{ai-generated-name}.{extension}
```

Examples:
- `auto-notes-llama2-meeting-notes.md`
- `auto-notes-llama2-fibonacci-calculator.py`
- `auto-notes-llama2-user-data.json`

If Ollama is unavailable, fallback format:
```
auto-notes-{model}-{timestamp}.txt
```

Example: `auto-notes-llama2-20250113-143022.txt`

## How It Works

1. Plugin extracts first 250 words from unsaved file
2. Sends content to Ollama with prompt asking for filename suggestion
3. Ollama analyzes content and suggests filename with appropriate extension
4. Plugin sanitizes filename and adds prefix
5. File is saved to configured directory

## Testing

### Run Unit Tests (no Ollama required)

```bash
cd /path/to/sublime-autosave-with-ai
python -m pytest tests/test_autosave_unit.py -v
```

Or with unittest:
```bash
python tests/test_autosave_unit.py
```

### Run Integration Tests (requires Ollama)

Make sure Ollama is running first:

```bash
ollama serve
```

Then run tests:
```bash
python -m pytest tests/test_autosave_integration.py -v
```

Or with unittest:
```bash
python tests/test_autosave_integration.py
```

### Run All Tests

```bash
python -m pytest tests/ -v
```

## Troubleshooting

### Plugin Not Working

1. Check Sublime Text console: `View > Show Console`
2. Look for error messages starting with "AutoSaveWithAI:"

### Ollama Connection Errors

1. Verify Ollama is running:
   ```bash
   curl http://localhost:11434/api/tags
   ```

2. Check the model is downloaded:
   ```bash
   ollama list
   ```

3. Test manual generation:
   ```bash
   ollama run llama2 "Suggest a filename for: meeting notes"
   ```

### Files Not Saving

1. Check `save_directory` exists and is writable
2. Verify path in settings (use absolute path or `~/`)
3. Check console for permission errors

### Timer Not Working

- Timer only triggers on unsaved files (no file path)
- Timer resets on each modification
- Check `auto_save_timer` is greater than 0

## Development

### Project Structure

```
sublime-autosave-with-ai/
├── AutoSaveWithAI.py              # Main plugin code
├── AutoSaveWithAI.sublime-settings # Default settings
├── Default.sublime-commands        # Command palette entries
├── tests/
│   ├── test_autosave_unit.py      # Unit tests
│   └── test_autosave_integration.py # Integration tests
├── .gitignore
└── README.md
```

### Key Classes

- **`OllamaClient`**: Handles API communication with Ollama
- **`AutoSaveWithAiCommand`**: Command for manual trigger via Command Palette
- **`AutoSaveEventListener`**: Handles save events and timer-based auto-save

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and add tests
4. Run tests to ensure they pass
5. Submit a pull request

## License

MIT License - feel free to use and modify as needed.

## Credits

Built with:
- [Sublime Text](https://www.sublimetext.com/) - The text editor
- [Ollama](https://ollama.ai/) - Local LLM runtime

## Support

For issues, questions, or suggestions, please open an issue on the GitHub repository.
