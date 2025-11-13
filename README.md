# AutoSaveWithAI - Sublime Text Plugin

A Sublime Text plugin that automatically saves unsaved files with AI-generated filenames using any OpenAI-compatible API endpoint.

## Features

- **OpenAI-Compatible API Support**: Works with any provider supporting Chat Completions or Responses API
- **Pure Python Stdlib**: No external dependencies required - uses only Python's built-in http.client
- **Smart Filename Generation**: Analyzes file content and suggests appropriate filenames with correct extensions
- **Extension Detection**: Automatically detects content type (JSON, Markdown, Python, etc.) and adds appropriate extensions
- **Multiple Trigger Options**:
  - Keyboard shortcut (Ctrl+I / Cmd+I) or Command Palette
  - Auto-save on timer (configurable seconds of inactivity)
  - Intercept default save action (Ctrl+S/Cmd+S) for unsaved files
- **Dual API Support**: Choose between Chat Completions (/v1/chat/completions) or Responses API (/v1/responses)
- **Flexible Authentication**: Support for both OpenAI-style (Authorization: Bearer) and Azure-style (api-key) auth
- **Fallback Mechanism**: Uses timestamp-based naming when API is unavailable
- **Flexible Configuration**: Customize save directory, model, API endpoint, and behavior

## Requirements

- Sublime Text 4 (Python 3.3+)
- No external Python packages required (uses only stdlib)
- API access to any OpenAI-compatible provider:
  - **OpenAI**: API key from [platform.openai.com](https://platform.openai.com)
  - **Azure OpenAI**: API key from Azure portal
  - **Any OpenAI-compatible endpoint**: Custom API key and base URL

## Installation

### Install Plugin

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

#### OpenAI (Default)

```json
{
    "save_directory": "~/Documents/auto-notes",
    "llm_model": "gpt-4o",
    "api_base": "https://api.openai.com/v1",
    "api_type": "chat",
    "openai_api_key": "sk-...",
    "auth_header_name": "Authorization",
    "auth_header_prefix": "Bearer ",
    "overwrite_default_save": false,
    "auto_save_timer": 0
}
```

#### Azure OpenAI

```json
{
    "save_directory": "~/Documents/auto-notes",
    "llm_model": "gpt-4o",
    "api_base": "https://YOUR-RESOURCE.openai.azure.com/openai/v1",
    "api_type": "chat",
    "openai_api_key": "your-azure-key",
    "auth_header_name": "api-key",
    "auth_header_prefix": "",
    "overwrite_default_save": false,
    "auto_save_timer": 0
}
```

#### Any OpenAI-Compatible Endpoint

```json
{
    "save_directory": "~/Documents/auto-notes",
    "llm_model": "model-name",
    "api_base": "https://your-endpoint.com/v1",
    "api_type": "chat",
    "api_key": "your-api-key",
    "auth_header_name": "Authorization",
    "auth_header_prefix": "Bearer ",
    "overwrite_default_save": false,
    "auto_save_timer": 30
}
```

### Configuration Options

- **`save_directory`**: Directory where files will be saved (supports `~/` for home directory)
- **`llm_model`**: Model identifier as specified by your provider (e.g., `gpt-4o`, `gpt-3.5-turbo`, `gpt-4.1-mini`)
- **`api_base`**: Base URL for API endpoint (default: `https://api.openai.com/v1`)
- **`api_type`**: API type to use - `"chat"` for Chat Completions or `"responses"` for Responses API (default: `"chat"`)
- **`openai_api_key`**: OpenAI API key (used when model starts with `gpt-` or `openai/`)
- **`anthropic_api_key`**: Anthropic API key (used when model starts with `anthropic/`)
- **`api_key`**: Generic API key (used for other providers)
- **`auth_header_name`**: Header name for authentication (default: `"Authorization"`, Azure uses `"api-key"`)
- **`auth_header_prefix`**: Prefix for auth header value (default: `"Bearer "`, Azure uses `""`)
- **`overwrite_default_save`**: If `true`, intercepts Ctrl+S/Cmd+S on unsaved files
- **`auto_save_timer`**: Seconds of inactivity before auto-save (0 = disabled)
- **`prompt_template`**: Template for AI prompt (`{content}` is replaced with file content)

## Usage

### Method 1: Manual Trigger

#### Option A: Keyboard Shortcut (Recommended)

1. Create or open an unsaved file
2. Press **Ctrl+I** (Windows/Linux) or **Cmd+I** (Mac)

#### Option B: Command Palette

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
2. Sends content to configured OpenAI-compatible API endpoint via stdlib HTTP client
3. LLM analyzes content and suggests filename with appropriate extension
4. Plugin sanitizes filename and adds prefix
5. File is saved to configured directory

## Setup for Different Providers

### OpenAI Setup

1. Get API key from [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Add to settings:
   ```json
   {
       "llm_model": "gpt-4o",
       "api_base": "https://api.openai.com/v1",
       "api_type": "chat",
       "openai_api_key": "sk-..."
   }
   ```

### Azure OpenAI Setup

1. Get API key and resource name from Azure portal
2. Add to settings:
   ```json
   {
       "llm_model": "gpt-4o",
       "api_base": "https://YOUR-RESOURCE.openai.azure.com/openai/v1",
       "api_type": "chat",
       "openai_api_key": "your-azure-key",
       "auth_header_name": "api-key",
       "auth_header_prefix": ""
   }
   ```

### Custom OpenAI-Compatible Endpoint

1. Obtain API key and base URL from your provider
2. Add to settings:
   ```json
   {
       "llm_model": "model-name",
       "api_base": "https://your-endpoint.com/v1",
       "api_type": "chat",
       "api_key": "your-api-key"
   }
   ```

## Testing

### Run Unit Tests (no API required)

```bash
python tests/test_autosave_unit.py -v
```

### Run Integration Tests (requires API access)

```bash
# Configure your API key in environment or settings
python tests/test_autosave_integration.py -v
```

### Run All Tests

```bash
python -m unittest discover tests/ -v
```

## Troubleshooting

### Plugin Not Working

1. Check Sublime Text console: `View > Show Console`
2. Look for error messages starting with "AutoSaveWithAI:"
3. Verify Python version compatibility (3.3+ required)

### API Connection Errors

1. Verify API key is correct in settings
2. Check API base URL is correct (e.g., `https://api.openai.com/v1`)
3. Verify API endpoint supports Chat Completions or Responses API
4. Check console for specific HTTP error codes (401, 403, 404, etc.)
5. Test API connection manually:
   ```bash
   curl -X POST https://api.openai.com/v1/chat/completions \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"model":"gpt-3.5-turbo","messages":[{"role":"user","content":"test"}]}'
   ```

### Authentication Errors (401/403)

1. For OpenAI: Verify `auth_header_name="Authorization"` and `auth_header_prefix="Bearer "`
2. For Azure: Verify `auth_header_name="api-key"` and `auth_header_prefix=""`
3. Check API key has sufficient credits/quota

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
├── ai_client.py                   # HTTP client for OpenAI-compatible APIs
├── AutoSaveWithAI.sublime-settings # Default settings
├── Default.sublime-commands        # Command palette entries
├── tests/
│   ├── test_autosave_unit.py      # Unit tests
│   └── test_autosave_integration.py # Integration tests
├── .gitignore
└── README.md
```

### Key Classes

- **`AIClient`**: Handles API communication with OpenAI-compatible endpoints via stdlib HTTP
- **`AutoSaveWithAiCommand`**: Command for manual trigger via Command Palette
- **`AutoSaveEventListener`**: Handles save events and timer-based auto-save

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and add tests
4. Run tests to ensure they pass
5. Submit a pull request

## Supported Providers

This plugin works with any provider that implements OpenAI-compatible APIs:

- **Chat Completions API** (`/v1/chat/completions`): Widely supported by most providers
- **Responses API** (`/v1/responses`): Newer API supported by OpenAI and some providers

Compatible providers include:

- **OpenAI**: Direct API access
- **Azure OpenAI**: Microsoft's hosted OpenAI service
- **OpenAI-compatible endpoints**: Any service implementing the Chat Completions or Responses API
  - Local services (Ollama, LM Studio, vLLM, LocalAI)
  - Cloud providers with OpenAI-compatible endpoints
  - Custom proxies and gateways

## License

MIT License - feel free to use and modify as needed.

## Credits

Built with:
- [Sublime Text](https://www.sublimetext.com/) - The text editor
- Python standard library - For HTTP client implementation (no external dependencies)

## Support

For issues, questions, or suggestions, please open an issue on the GitHub repository.
