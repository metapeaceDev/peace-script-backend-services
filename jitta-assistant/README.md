# Jitta Assistant

Jitta is a local-first assistant designed to help Peace Tech projects. It supports:
- Telegram chat as the main interface
- Automatic model switching (fast vs quality)
- RAG for continuously updated knowledge
- Local file and shell tools (guarded)
- Web fetch (guarded; paid actions require approval)

## Prerequisites

- Python 3.8+
- Virtual environment (recommended)

## Quick Start

1) Create a virtual environment

```bash
python -m venv .venv
# On Windows:
.\.venv\Scripts\Activate.ps1
# On Linux/Mac:
source .venv/bin/activate
```

2) Install dependencies

```bash
pip install -r requirements.txt
```

3) Configure environment

```bash
cp .env.example .env
# Edit .env with your settings
```

4) Set up LLM endpoints

You need to have OpenAI-compatible LLM servers running on:
- Fast model: http://127.0.0.1:8001/v1 (default)
- Quality model: http://127.0.0.1:8002/v1 (default)

Or update the URLs in `.env` file.

5) Start Telegram bot

```bash
python telegram_bot.py
```

6) Optional HTTP server

```bash
python server.py
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `APP_NAME` | Application name | Jitta |
| `JITTA_ROOT_DIR` | Root directory for file operations | . |
| `JITTA_DATA_DIR` | Data directory for RAG/Chroma | ./data |
| `JITTA_ALLOW_SHELL_COMMANDS` | Allow shell command execution | false |
| `JITTA_ALLOW_WEB_ACCESS` | Allow web access | true |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token | (required for bot) |
| `TELEGRAM_ADMIN_CHAT_ID` | Admin chat ID | (optional) |
| `FAST_LLM_BASE_URL` | Fast model endpoint | http://127.0.0.1:8001/v1 |
| `FAST_LLM_MODEL` | Fast model name | qwen3.5-14b-instruct |
| `QUALITY_LLM_BASE_URL` | Quality model endpoint | http://127.0.0.1:8002/v1 |
| `QUALITY_LLM_MODEL` | Quality model name | qwen3.5-32b-instruct |
| `RAG_EMBED_MODEL` | Embedding model | sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 |
| `RAG_EMBED_DEVICE` | Embedding device: auto/cpu/cuda/mps | auto |
| `RAG_TOP_K` | Number of RAG results | 4 |
| `MOCK_LLM` | Use mock responses (development) | false |

## Telegram Commands

- `/start` - Start the bot
- `/help` - Show help
- `/mode fast|quality|auto` - Set model mode
- `/status` - Show current status
- `/ingest <text>` - Add text to knowledge base
- `/ingest_dir <absolute path>` - Ingest directory files
- `/read <path>` - Read file content
- `/write <path>\n<content>` - Write to file
- `/list <path>` - List directory contents
- `/run <command>` - Run shell command (if enabled)

## Model Switching

- `fast`: Uses FAST_LLM_* settings for quick responses
- `quality`: Uses QUALITY_LLM_* settings for complex tasks
- `auto`: Automatic routing based on task type (code/peace-tech vs general)

## Safety Features

- Web access is allowed by default but can be disabled
- Actions that look like paid transactions require explicit approval
- Shell commands are blocked unless `JITTA_ALLOW_SHELL_COMMANDS=true`
- File operations are restricted to the configured root directory
- Dangerous shell commands are automatically blocked

## API Endpoints

### POST /chat
Chat with the assistant.

**Request:**
```json
{
  "text": "Hello, how are you?"
}
```

**Response:**
```json
{
  "reply": "I'm doing well, thank you!",
  "mode": "fast"
}
```

### POST /ingest
Add text to the knowledge base.

**Request:**
```json
{
  "text": "Some knowledge to add",
  "source": "api"
}
```

**Response:**
```json
{
  "status": "ok"
}
```

### GET /status/runtime
Check local runtime readiness for GPU and model endpoints.

Returns:
- Torch CUDA availability and detected GPU list
- Fast/Quality model endpoint health
- RAG embedding requested/resolved device

## Development

### Project Structure
```
jitta-assistant/
├── app/
│   ├── __init__.py
│   ├── config.py          # Configuration management
│   ├── orchestrator.py    # Main orchestration logic
│   ├── llm_client.py      # LLM API client
│   ├── rag.py            # RAG implementation
│   ├── safety.py         # Safety checks
│   ├── tools.py          # File/shell tools
│   └── logger.py         # Logging setup
├── data/                 # RAG data and Chroma DB
├── logs/                 # Application logs
├── server.py             # FastAPI server
├── telegram_bot.py       # Telegram bot
├── requirements.txt      # Python dependencies
├── .env.example          # Environment template
└── README.md            # This file
```

### Testing

Run the HTTP server for testing:
```bash
python server.py
```

Test with curl:
```bash
curl -X POST http://localhost:7071/chat -H "Content-Type: application/json" -d '{"text": "Hello"}'
```

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError**: Make sure you've activated the virtual environment and installed dependencies:
   ```bash
   .\venv\Scripts\Activate.ps1  # Windows
   pip install -r requirements.txt
   ```

2. **LLM Connection Failed**: Check that your LLM servers are running and accessible at the configured URLs.

3. **Telegram Bot Not Responding**: Verify your bot token and chat ID in the `.env` file.

4. **Permission Errors**: Make sure the application has write access to the data directory.

### Logs

Check the `logs/` directory for application logs. Logging level can be adjusted in the code.

## License

Peace Tech Internal Use Only
