# 📋 Batch Scripts Documentation

This document describes all batch scripts available in the FAQ Bot project.

## 📁 Available Scripts

### New Simplified Scripts

### setup.bat
Launches the console setup tool with options for:
- Setting up the bot environment
- Training the ML model
- Starting the bot
- Cleaning cache
- Checking system status

### start.bat
Starts the FAQ bot directly without PowerShell dependencies:
- Validates required files
- Activates virtual environment
- Starts the bot with error handling
- Shows logs and statistics

### Traditional Scripts

### 0_Setup.bat
Initial setup script that:
- Creates Python virtual environment
- Installs all dependencies
- Creates necessary directories
- Sets up initial configuration files

### 1_Start_Bot.bat
Starts the FAQ bot with full environment checking:
- Validates required files
- Activates virtual environment
- Checks dependencies
- Starts the bot with error handling
- Shows logs and statistics

### start.ps1
PowerShell script for starting the bot in PowerShell environments:
- Simple script that checks required files
- Activates virtual environment
- Starts the bot
- Compatible with PowerShell terminals

### 2_Stop_bot.bat
Stops all running bot processes:
- Finds and terminates bot processes
- Cleans up any hanging processes

### 3_Clean_All.bat
Complete cleanup script:
- Removes cache files
- Deletes logs
- Cleans Python cache directories
- Removes temporary files

### 4_Train_Model.bat
Trains the ML model:
- Creates FAQ embeddings
- Builds FAISS index
- Saves model files to cache

### 5_Check_Status.bat
System status checker:
- Verifies all components
- Checks dependencies
- Validates configuration
- Shows system information

## 🛠 Usage Instructions

### Simplified Setup (Recommended)
```cmd
# Launch console setup tool
setup.bat

# Start bot
start.bat
```

### For Command Prompt (cmd)
```cmd
# Setup (run once)
0_Setup.bat

# Start bot
1_Start_Bot.bat

# Stop bot
2_Stop_bot.bat
```

### For PowerShell
```powershell
# Setup (run once)
.\0_Setup.bat

# Start bot
.\start.ps1

# Stop bot
.\2_Stop_bot.bat
```

## ⚠️ Troubleshooting

If you encounter issues:
1. Make sure you're using the correct script for your terminal (cmd vs PowerShell)
2. Check that all dependencies are installed (run 0_Setup.bat)
3. Verify .env file contains your BOT_TOKEN
4. Ensure data/faq.json exists with valid FAQ data

## 📝 Notes

- All scripts should be run from the project root directory
- Virtual environment is automatically managed
- Logs are saved to cache/bot.log
- Model files are saved to cache/ directory