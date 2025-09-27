# 🤖 FAQ Bot

Telegram FAQ bot with semantic search capabilities using Sentence-BERT and FAISS.

## 🚀 Quick Start

### For Command Prompt (cmd)
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

## 📁 Project Structure

- `src/` - Source code
- `data/` - FAQ data and database
- `cache/` - Model embeddings and cache files
- `files/` - Media files
- `venv/` - Python virtual environment

## ⚙️ Configuration

1. Create a bot with [@BotFather](https://t.me/BotFather) on Telegram
2. Copy your bot token to `.env` file:
   ```
   BOT_TOKEN=your_bot_token_here
   ADMIN_ID=your_telegram_id
   ACCESS_PASSWORD=your_password
   ```

## 🧠 Training the Model

Run `4_Train_Model.bat` to retrain the semantic search model with your FAQ data.

## 🛠 Scripts

- `0_Setup.bat` - Initial setup
- `1_Start_Bot.bat` - Start bot (for cmd)
- `start.ps1` - Start bot (for PowerShell)
- `2_Stop_bot.bat` - Stop bot
- `3_Clean_All.bat` - Clean cache and logs
- `4_Train_Model.bat` - Train semantic search model
- `5_Check_Status.bat` - Check system status

## 📋 Requirements

- Python 3.8+
- Windows OS
- Telegram bot token

## 📞 Support

For issues, check the logs in `cache/bot.log` or run `5_Check_Status.bat`.