# AutoSaveWithAI - Sublime Text Plugin

A Sublime Text plugin that automatically saves unsaved files with AI-generated filenames using LiteLLM to support multiple AI providers.

## Features

- **Multi-Provider AI Support**: Works with OpenAI, Anthropic Claude, local Ollama, and 80+ other providers via LiteLLM
- **Smart Filename Generation**: Analyzes file content and suggests appropriate filenames with correct extensions
- **Extension Detection**: Automatically detects content type (JSON, Markdown, Python, etc.) and adds appropriate extensions
- **Multiple Trigger Options**:
  - Manual command via Command Palette
  - Auto-save on timer (configurable seconds of inactivity)
  - Intercept default save action (Ctrl+S/Cmd+S) for unsaved files
- **Fallback Mechanism**: Uses timestamp-based naming when LLM is unavailable
- **Flexible Configuration**: Customize save directory, model, API keys, and behavior

## Requirements

- Sublime Text 4 (Python 3.8+)
- Python package: `litellm` (see Installation)
- API access to at least one LLM provider:
  - **OpenAI**: API key from [platform.openai.com](https://platform.openai.com)
  - **Anthropic**: API key from [console.anthropic.com](https://console.anthropic.com)
  - **Ollama**: Local installation from [ollama.ai](https://ollama.ai/) (free)

## Installation

### Step 1: Install LiteLLM

LiteLLM must be installed in the Python environment used by Sublime Text:

```bash
# Install litellm
pip install litellm

# Or if Sublime Text uses a specific Python:
/path/to/sublime/python -m pip install litellm
```

### Step 2: Install Plugin

#### Option A: Manual Installation

1. Clone or download this repository
2. Copy the plugin files to your Sublime Text Packages directory:
   - **macOS**: `~/Library/Application Support/Sublime Text/Packages/AutoSaveWithAI/`
   - **Linux**: `~/.config/sublime-text/Packages/AutoSaveWithAI/`
   - **Windows**: `%APPDATA%\Sublime Text\Packages\AutoSaveWithAI\`

3. Restart Sublime Text

#### Option B: Symlink (for development)

```bash
# macOS/Linux
ln -s /path/to/sublime-autosave-with-ai ~/Library/Application\ Support/Sublime\ Text/Packages/AutoSaveWithAI

# Windows (run as Administrator)
mklink /D "%APPDATA%\Sublime Text\Packages\AutoSaveWithAI" "C:\path\to\sublime-autosave-with-ai"
```

## Configuration

Open Sublime Text settings: `Preferences > Package Settings > AutoSaveWithAI > Settings`

### Example Configurations

#### OpenAI (GPT-4)

```json
{
    "save_directory": "~/Documents/auto-notes",
    "llm_model": "gpt-4o",
    "openai_api_key": "sk-...",
    "anthropic_api_key": "",
    "api_base": null,
    "overwrite_default_save": false,
    "auto_save_timer": 0
}
```

#### Anthropic Claude

```json
{
    "save_directory": "~/Documents/auto-notes",
    "llm_model": "anthropic/claude-3-5-sonnet-20240620",
    "openai_api_key": "",
    "anthropic_api_key": "sk-ant-...",
    "api_base": null,
    "overwrite_default_save": false,
    "auto_save_timer": 0
}
```

#### Local Ollama (Free)

```json
{
    "save_directory": "~/Documents/auto-notes",
    "llm_model": "ollama_chat/llama3.2",
    "openai_api_key": "",
    "anthropic_api_key": "",
    "api_base": "http://localhost:11434",
    "overwrite_default_save": false,
    "auto_save_timer": 30
}
```

### Configuration Options

- **`save_directory`**: Directory where files will be saved (supports `~/` for home directory)
- **`llm_model`**: Model identifier
  - OpenAI: `gpt-4o`, `gpt-4-turbo`, `gpt-3.5-turbo`
  - Anthropic: `anthropic/claude-3-5-sonnet-20240620`, `anthropic/claude-3-opus-20240229`
  - Ollama: `ollama/llama3.2`, `ollama_chat/llama3.2` (use `ollama_chat/` for better responses)
- **`openai_api_key`**: OpenAI API key (leave empty if not using)
- **`anthropic_api_key`**: Anthropic API key (leave empty if not using)
- **`api_base`**: Custom API endpoint (optional, for proxies or self-hosted)
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
auto-notes-{ai-generated-name}.{extension}
```

Examples:
- `auto-notes-meeting-notes.md`
- `auto-notes-fibonacci-calculator.py`
- `auto-notes-user-data.json`

If LLM is unavailable, fallback format:
```
auto-notes-{timestamp}.txt
```

Example: `auto-notes-20250113-143022.txt`

## How It Works

1. Plugin extracts first 250 words from unsaved file
2. Sends content to configured LLM via LiteLLM
3. LLM analyzes content and suggests filename with appropriate extension
4. Plugin sanitizes filename and adds prefix
5. File is saved to configured directory

## Setup for Different Providers

### OpenAI Setup

1. Get API key from [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Add to settings:
   ```json
   {
       "llm_model": "gpt-3.5-turbo",
       "openai_api_key": "sk-..."
   }
   ```

### Anthropic Claude Setup

1. Get API key from [console.anthropic.com](https://console.anthropic.com/)
2. Add to settings:
   ```json
   {
       "llm_model": "anthropic/claude-3-5-sonnet-20240620",
       "anthropic_api_key": "sk-ant-..."
   }
   ```

### Ollama Setup (Local, Free)

1. Install Ollama from [ollama.ai](https://ollama.ai/)
2. Download a model:
   ```bash
   ollama pull llama3.2
   ```
3. Verify Ollama is running:
   ```bash
   ollama list
   ```
4. Configure plugin:
   ```json
   {
       "llm_model": "ollama_chat/llama3.2",
       "api_base": "http://localhost:11434"
   }
   ```

## Testing

### Run Unit Tests (no LLM required)

```bash
python tests/test_autosave_unit.py -v
```

### Run Integration Tests (requires LLM access)

For Ollama:
```bash
# Make sure Ollama is running
ollama serve

# Run tests
python tests/test_autosave_integration.py -v
```

### Run All Tests

```bash
python -m pytest tests/ -v
```

## Troubleshooting

### Plugin Not Working

1. Check Sublime Text console: `View > Show Console`
2. Look for error messages starting with "AutoSaveWithAI:"

### LiteLLM Not Installed

If you see "litellm not installed", install it:
```bash
pip install litellm
```

### OpenAI/Anthropic API Errors

1. Verify API key is correct
2. Check API key has sufficient credits/quota
3. Check console for specific error messages

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
   ollama run llama3.2 "Suggest a filename for: meeting notes"
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
├── requirements.txt                # Python dependencies
├── tests/
│   ├── test_autosave_unit.py      # Unit tests
│   └── test_autosave_integration.py # Integration tests
├── .gitignore
└── README.md
```

### Key Classes

- **`LiteLLMClient`**: Handles API communication with LLM providers via LiteLLM
- **`AutoSaveWithAiCommand`**: Command for manual trigger via Command Palette
- **`AutoSaveEventListener`**: Handles save events and timer-based auto-save

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and add tests
4. Run tests to ensure they pass
5. Submit a pull request

## Supported Providers

Via LiteLLM, this plugin supports 80+ providers including:

- **Major AI APIs**: OpenAI, Anthropic, Google Vertex AI, AWS Bedrock, Azure OpenAI
- **Alternative APIs**: Mistral, Cohere, Groq, DeepSeek, Perplexity, Together AI
- **Local/Self-hosted**: Ollama, LM Studio, vLLM, HuggingFace
- **And many more**: See [LiteLLM providers](https://docs.litellm.ai/docs/providers)

## License

MIT License - feel free to use and modify as needed.

## Credits

Built with:
- [Sublime Text](https://www.sublimetext.com/) - The text editor
- [LiteLLM](https://github.com/BerriAI/litellm) - Unified LLM API interface
- [Ollama](https://ollama.ai/) - Local LLM runtime (optional)

## Support

For issues, questions, or suggestions, please open an issue on the GitHub repository.
