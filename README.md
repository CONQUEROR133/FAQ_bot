# 🤖 FAQ Bot - Complete Documentation

Telegram FAQ bot with semantic search capabilities using Sentence-BERT and FAISS.

## 📋 Table of Contents
- [Project Overview](#-project-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Quick Start](#-quick-start)
- [Project Structure](#-project-structure)
- [Configuration](#️-configuration)
- [Training the Model](#-training-the-model)
- [Scripts Documentation](#-scripts-documentation)
- [Requirements](#-requirements)
- [Support](#-support)
- [Log Analysis](#-log-analysis)
- [Testing the Bot](#-testing-the-bot)
- [Maintenance](#-maintenance)
- [Project Optimization Summary](#-project-optimization-summary)

## 📖 Project Overview

This project contains a Telegram bot on Python for managing a Frequently Asked Questions (FAQ) system. It features intelligent search capabilities using machine learning algorithms to provide relevant answers to user queries.

## 🌟 Features

- Intelligent search answers using machine learning algorithms
- User authentication and access control
- Statistics tracking and analytics
- Support for various data formats (CSV, TXT, XLSX)
- Performance optimization with caching
- Semantic search capabilities using Sentence-BERT and FAISS

## 🏗️ Architecture

The project follows an architecture with components integrated into a unified system:
- **faq_bot** processes and provides FAQ data through Telegram

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

## 📁 Project Structure

- `src/` - Source code
- `data/` - FAQ data and database
- `cache/` - Model embeddings and cache files
- `files/` - Media files
- `logs/` - Log files (JSON format)
- `venv/` - Python virtual environment
- `tools/` - Utility tools

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

## 🛠 Scripts Documentation

### New Simplified Scripts

#### setup.bat
Launches the console setup tool with options for:
- Setting up the bot environment
- Training the ML model
- Starting the bot
- Cleaning cache
- Checking system status

#### setup.py
Python-based console application with menu options:
1. Setup Bot - Runs the original setup process
2. Train Bot - Trains the ML model
3. Start Bot - Starts the Telegram bot
4. Clean Cache - Removes cached files
5. Check Status - Verifies system requirements

#### start.bat
Starts the FAQ bot directly without PowerShell dependencies:
- Validates required files
- Activates virtual environment
- Starts the bot with error handling
- Shows logs and statistics

### Traditional Scripts

#### 0_Setup.bat
Initial setup script that:
- Creates Python virtual environment
- Installs all dependencies
- Creates necessary directories
- Sets up initial configuration files

#### 1_Start_Bot.bat
Starts the FAQ bot with full environment checking:
- Validates required files
- Activates virtual environment
- Checks dependencies
- Starts the bot with error handling
- Shows logs and statistics

#### start.ps1
PowerShell script for starting the bot in PowerShell environments:
- Simple script that checks required files
- Activates virtual environment
- Starts the bot
- Compatible with PowerShell terminals

#### 2_Stop_bot.bat
Stops all running bot processes:
- Finds and terminates bot processes
- Cleans up any hanging processes

#### 3_Clean_All.bat
Complete cleanup script:
- Removes cache files
- Deletes logs
- Cleans Python cache directories
- Removes temporary files

#### 4_Train_Model.bat
Trains the ML model:
- Creates FAQ embeddings
- Builds FAISS index
- Saves model files to cache

#### 5_Check_Status.bat
System status checker:
- Verifies all components
- Checks dependencies
- Validates configuration
- Shows system information

### Usage Instructions

#### Simplified Setup (Recommended)
```cmd
# Launch console setup tool
setup.bat

# Start bot
start.bat
```

#### For Command Prompt (cmd)
```cmd
# Setup (run once)
0_Setup.bat

# Start bot
1_Start_Bot.bat

# Stop bot
2_Stop_bot.bat
```

#### For PowerShell
```powershell
# Setup (run once)
.\0_Setup.bat

# Start bot
.\start.ps1

# Stop bot
.\2_Stop_bot.bat
```

### Troubleshooting

If you encounter issues:
1. Make sure you're using the correct script for your terminal (cmd vs PowerShell)
2. Check that all dependencies are installed (run 0_Setup.bat)
3. Verify .env file contains your BOT_TOKEN
4. Ensure data/faq.json exists with valid FAQ data

### Notes

- All scripts should be run from the project root directory
- Virtual environment is automatically managed
- Logs are saved to cache/bot.log
- Model files are saved to cache/ directory

## 📋 Requirements

- Python 3.8+
- Windows OS
- Telegram bot token

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

## 🧹 Maintenance

### Log Rotation
Logs are automatically rotated when they reach 10MB, with up to 5 backup files retained.

### Cleaning Cache
Run `3_Clean_All.bat` to remove cache files while preserving the trained model.

## 📈 Project Optimization Summary

### Objective
Optimize the FAQ Bot project setup to make it easily portable and runnable on different computers with a simplified user experience.

### Changes Made

#### 1. Created New Simplified Scripts

##### setup.bat
- Launches a console setup tool for easy configuration
- Provides menu-driven options for setup, training, and starting the bot
- Automatically detects and uses virtual environment
- User-friendly interface with clear instructions

##### setup.py
- Python-based console application with menu options
- Provides five main options:
  1. Setup Bot - Runs the original setup process
  2. Train Bot - Trains the ML model
  3. Start Bot - Starts the Telegram bot
  4. Clean Cache - Removes cached files
  5. Check Status - Verifies system requirements
- Clear output and progress indication during operations

##### start.bat
- Simplified script to start the bot directly
- No PowerShell dependencies
- Automatic virtual environment detection
- Clear error messages and status reporting
- Works in both Command Prompt and PowerShell

#### 2. Preserved Original Scripts
All original batch files were restored to maintain backward compatibility:
- `0_Setup.bat`
- `1_Start_Bot.bat`
- `2_Stop_bot.bat`
- `3_Clean_All.bat`
- `4_Train_Model.bat`
- `5_Check_Status.bat`

### Key Improvements

#### Portability
- Simplified setup process reduces configuration complexity
- Console interface makes the tool accessible on all Windows systems
- Consistent behavior across different Windows environments

#### User Experience
- Menu-driven interface with clear options
- Real-time feedback during operations
- Clear error messages and next steps
- Reduced dependency on specific terminal types

#### Maintenance
- Cleaner project structure with fewer complex scripts
- Better separation of concerns between setup, training, and execution
- Easier to update and maintain individual components

### Usage Instructions

#### For End Users (Recommended)
1. Run `setup.bat` to launch the console setup tool
2. Choose option 1 to setup the bot and install dependencies
3. Edit `.env` with your configuration
4. Add FAQ data to `data/faq.json`
5. Choose option 2 to train the model
6. Choose option 3 to start the Telegram bot

#### For Developers
1. Run `setup.bat` and choose option 1 for initial setup
2. Modify source code as needed
3. Run `start.bat` to test changes

#### For Automated Environments
1. Use the traditional batch files if needed
2. All original functionality preserved

### Testing
The new setup has been tested and verified to work correctly:
- Console setup tool launches successfully
- Menu options work as expected
- Bot starts and runs as expected
- All original functionality preserved

### Future Improvements
- Add more detailed status reporting
- Implement automatic dependency checking
- Add progress indicators for long-running operations
- Include more maintenance options in the setup tool

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Development

The project was developed with modern practices in mind:
- Clear separation of responsibilities between components
- Automated testing
- Code and API documentation