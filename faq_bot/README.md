# 🤖 FAQ Bot

Telegram FAQ bot with semantic search capabilities using Sentence-BERT and FAISS.

## 📚 Documentation

For comprehensive documentation, see [CONSOLIDATED_DOCUMENTATION.md](CONSOLIDATED_DOCUMENTATION.md)

## 🚀 Quick Start

### Simplified Setup (Recommended)
```cmd
# Launch the console setup tool
setup.bat

# Start the bot
start.bat
```

### Manual Setup (Alternative)
If you prefer the traditional approach:
```cmd
# Initial setup (run once)
0_Setup.bat

# Start the bot
1_Start_Bot.bat

# Stop the bot
2_Stop_bot.bat
```

### For PowerShell
```powershell
# Initial setup (run once)
.\0_Setup.bat

# Start the bot
.\start.ps1

# Stop the bot
.\2_Stop_bot.bat
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
- `venv/` - Python virtual environment
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

### Using Setup Tool (Recommended)
Run `setup.bat` and select option 2 to train the model.

### Manual Method
Run `4_Train_Model.bat` to retrain the semantic search model with your FAQ data.

## 🛠 Scripts

### New Simplified Scripts
- `setup.bat` - Launch console setup tool (Setup, Train, Start options)
- `start.bat` - Start bot directly without PowerShell

### Traditional Scripts
- `0_Setup.bat` - Initial setup
- `1_Start_Bot.bat` - Start bot (for cmd)
- `start.ps1` - Start bot (for PowerShell)
- `2_Stop_bot.bat` - Stop bot
- `3_Clean_All.bat` - Clean cache and logs
- `4_Train_Model.bat` - Train semantic search model
- `5_Check_Status.bat` - Check system status

## 📋 Requirements

- Python 3.8-3.12
- Windows or Linux OS
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

For issues, check the logs in `logs/bot.log` or run `5_Check_Status.bat`.

## 📊 Log Analysis

The bot now logs all user requests in JSON format. You can analyze these logs using the provided utility:

```cmd
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

## 📄 FAQ Data Format

The bot uses a JSON file (`data/faq.json`) to store FAQ entries. Here's an example format:

```json
[
  {
    "query": "How to reset password",
    "variations": [
      "reset password",
      "forgot password",
      "password reset"
    ],
    "response": "To reset your password, follow these steps:",
    "resources": [
      {
        "title": "Password Reset Guide",
        "type": "file",
        "files": ["files/password_reset.pdf"]
      },
      {
        "title": "Video Tutorial",
        "type": "link",
        "link": "https://example.com/reset-password-video"
      }
    ],
    "metadata": {
      "source_type": "manual",
      "confidence": 0.95,
      "processed_at": "2025-01-01T10:00:00.000000",
      "hash": "reset_password"
    }
  }
]
```

## 🧹 Maintenance

### Log Rotation
Logs are automatically rotated when they reach 10MB, with up to 5 backup files retained.

### Cleaning Cache
Run `3_Clean_All.bat` to remove cache files while preserving the trained model.