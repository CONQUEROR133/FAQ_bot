# 🤖 FAQ Bot

Telegram FAQ bot with semantic search capabilities using Sentence-BERT and FAISS.

## 📚 Documentation

For comprehensive documentation, see [CONSOLIDATED_DOCUMENTATION.md](CONSOLIDATED_DOCUMENTATION.md)

## 🚀 Quick Start (Cross-Platform)

### Using the Run Script (Recommended)
```bash
# Setup the bot (install dependencies, create directories, etc.)
python run.py setup

# Train the semantic search model with your FAQ data
python run.py train

# Start the bot
python run.py start

# Run tests
python run.py test

# Check system status
python run.py status

# Clean cache files
python run.py clean
```

### Interactive Setup Tool
```bash
# Launch the interactive setup tool
python setup.py
```

### Docker Setup (Recommended for Production)
```bash
# Build and start the bot with Docker
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the bot
docker-compose down
```

## 📁 Project Structure

- `src/` - Source code
- `data/` - FAQ data and database
- `cache/` - Model embeddings and cache files
- `files/` - Media files
- `logs/` - Log files (JSON format)
- `tools/` - Utility tools
- `tests/` - Test files

## ⚙️ Configuration

1. Create a bot with [@BotFather](https://t.me/BotFather) on Telegram
2. Copy your bot token to `.env` file:
   ```
   BOT_TOKEN=your_bot_token_here
   ADMIN_ID=your_telegram_id
   ACCESS_PASSWORD=your_password
   ```

## 🧠 Training the Model

### Using Run Script (Recommended)
```bash
python run.py train
```

### Using Interactive Setup Tool
Run `python setup.py` and select option 2 to train the model.

## 🛠 Commands

### Run Script Commands
- `python run.py setup` - Setup bot (install dependencies, create directories)
- `python run.py train` - Train semantic search model
- `python run.py start` - Start the bot
- `python run.py test` - Run test suite
- `python run.py status` - Check system status
- `python run.py clean` - Clean cache files

### Interactive Setup Tool
- `python setup.py` - Launch interactive setup tool with menu options

### Docker Setup (Production Recommended)
```bash
# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 📋 Requirements

- Python 3.8-3.12
- Cross-platform (Windows, Linux, macOS)
- Telegram bot token

## 🛠 Setup and Installation

### Virtual Environment Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
venv\Scripts\activate

# Activate virtual environment (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Docker Setup (Production Recommended)

```bash
# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 📞 Support

For issues, check the logs in `logs/bot.log`.

## 📊 Log Analysis

The bot now logs all user requests in JSON format. You can analyze these logs using the provided utility:

```bash
python tools/aggregate_stats.py
```

This will show:
- Total requests
- Top 20 queries by count
- Option to export to CSV

Example JSON log entry:
```json
{
  "ts": "2025-09-30 12:00:00,123",
  "level": "INFO",
  "logger": "root",
  "message": "User message received: How do I reset?",
  "user_id": 12345,
  "chat_id": 67890,
  "message_id": 111,
  "handler": "message_handler"
}
```

## 🧪 Testing the Bot

After starting the bot:

1. Open Telegram and search for your bot
2. Send the `/start` command
3. Enter the access password when prompted
4. Ask a question to test the FAQ functionality

## 📊 Statistics and Analytics

The bot tracks usage statistics in JSON log format. You can analyze these logs using the provided utility:

```bash
python tools/aggregate_stats.py
```

This will show:
- Total requests
- Top 20 queries by count
- Option to export to CSV

## 🧹 Cleanup

To remove unnecessary files and create a minimal version:

```bash
python cleanup.py
```

This will remove:
- Windows-specific batch files
- Redundant documentation files
- Cache directories
- Backup files

## 🌐 Cross-Platform Compatibility

This bot is designed to work on:
- Windows (cmd, PowerShell)
- Linux (bash, sh)
- macOS (bash, zsh)

All scripts use Python for cross-platform compatibility rather than OS-specific batch files.