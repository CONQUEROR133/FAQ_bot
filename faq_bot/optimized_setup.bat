@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion
title FAQ Bot - Setup & Installation
echo ====================================================
echo           Telegram FAQ Bot - Setup
echo ====================================================
echo.

:: Check if running from the correct directory
if not exist "requirements.txt" (
    echo ❌ Error: Please run this script from the project root directory
    echo    Current directory: %CD%
    echo    Make sure requirements.txt exists in this directory
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 1
)

:: Check Python installation
echo 🔍 Checking Python installation...
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Python not found! Please install Python 3.8+ and add it to PATH
    echo    Download from: https://www.python.org/downloads/
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 1
)

:: Get Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python !PYTHON_VERSION! found

:: Check if Python version is compatible (3.8+)
for /f "tokens=1,2 delims=." %%a in ("!PYTHON_VERSION!") do (
    set PYTHON_MAJOR=%%a
    set PYTHON_MINOR=%%b
)

if !PYTHON_MAJOR! LSS 3 (
    echo ❌ Python version too old. Please install Python 3.8 or newer
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 1
)

if !PYTHON_MAJOR! EQU 3 if !PYTHON_MINOR! LSS 8 (
    echo ❌ Python version too old. Please install Python 3.8 or newer
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 1
)

echo ✅ Python version is compatible (3.8+)

:: Check pip installation
echo.
echo 🔍 Checking pip installation...
pip --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ⚠️  pip not found! Attempting to install...
    python -m ensurepip --upgrade >nul 2>&1
    if !ERRORLEVEL! NEQ 0 (
        echo ❌ Failed to install pip
        echo.
        echo Press any key to exit...
        pause >nul
        exit /b 1
    )
)
echo ✅ pip is available

:: Create virtual environment if it doesn't exist
echo.
echo 📦 Setting up virtual environment...
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv >nul 2>&1
    if !ERRORLEVEL! NEQ 0 (
        echo ❌ Failed to create virtual environment
        echo.
        echo Press any key to exit...
        pause >nul
        exit /b 1
    )
    echo ✅ Virtual environment created
) else (
    echo ✅ Virtual environment already exists
)

:: Activate virtual environment
echo.
echo 💾 Activating virtual environment...
call venv\Scripts\activate.bat >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Failed to activate virtual environment
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 1
)
echo ✅ Virtual environment activated

:: Upgrade pip to latest version
echo.
echo 🔄 Upgrading pip...
python -m pip install --upgrade pip >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ⚠️  Failed to upgrade pip (continuing with current version)
) else (
    echo ✅ pip upgraded successfully
)

:: Install dependencies
echo.
echo 📦 Installing dependencies from requirements.txt...
pip install -r requirements.txt >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Failed to install dependencies from requirements.txt
    echo    Please check if requirements.txt exists and is properly formatted
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 1
)
echo ✅ Dependencies installed successfully

:: Create required directories
echo.
echo 📁 Creating required directories...
if not exist "data" (
    mkdir data >nul 2>&1
    echo ✅ Created data directory
) else (
    echo ✅ Data directory already exists
)

if not exist "cache" (
    mkdir cache >nul 2>&1
    echo ✅ Created cache directory
) else (
    echo ✅ Cache directory already exists
)

if not exist "files" (
    mkdir files >nul 2>&1
    echo ✅ Created files directory
) else (
    echo ✅ Files directory already exists
)

if not exist "logs" (
    mkdir logs >nul 2>&1
    echo ✅ Created logs directory
) else (
    echo ✅ Logs directory already exists
)

:: Create .env file if it doesn't exist
echo.
echo 🔧 Checking configuration file...
if not exist ".env" (
    echo Creating .env configuration file...
    (
        echo # Telegram Bot Configuration
        echo BOT_TOKEN=your_telegram_bot_token_here
        echo ADMIN_ID=your_telegram_user_id_here
        echo ACCESS_PASSWORD=your_access_password_here
        echo.
        echo # ML Model Configuration ^(optimized for i5-4570, 16GB RAM^)
        echo MODEL_NAME=ai-forever/ru-en-RoSBERTa
        echo SIMILARITY_THRESHOLD=0.73
        echo BATCH_SIZE=16
        echo CACHE_SIZE=500
        echo EMBEDDING_CACHE_SIZE=1000
        echo.
        echo # Network Configuration
        echo REQUEST_TIMEOUT=30
        echo CONNECT_TIMEOUT=30
        echo READ_TIMEOUT=30
        echo MAX_RETRIES=3
        echo RETRY_DELAY=1
    ) > .env
    echo ✅ .env file created
    echo ⚠️  Please edit .env with your actual configuration values
) else (
    echo ✅ .env file already exists
)

:: Create faq.json if it doesn't exist
echo.
echo 🔧 Checking FAQ data file...
if not exist "data\faq.json" (
    echo Creating faq.json data file...
    echo [] > data\faq.json
    echo ✅ faq.json created
    echo ⚠️  Please add your FAQ entries to data\faq.json
) else (
    echo ✅ faq.json already exists
)

echo.
echo ====================================================
echo           Setup Completed Successfully!
echo ====================================================
echo.
echo Next steps:
echo 1. Edit .env file with your bot configuration
echo 2. Add your FAQ entries to data\faq.json
echo 3. Run train_model.bat to train the semantic search model
echo 4. Run start_bot.bat to start the bot
echo.
echo Press any key to exit...
pause >nul
endlocal