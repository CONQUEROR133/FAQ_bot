@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion
title FAQ Bot - Setup & Installation
echo 🔧 Setting up FAQ Bot...
echo.

:: Check Python
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Python not found! Please install Python 3.8+ and add it to PATH
    echo Press any key to exit...
    pause >nul
    exit /b 1
)

:: Get Python version
for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo ✅ %PYTHON_VERSION%

:: Check pip
pip --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ pip not found! Please check Python installation
    echo Press any key to exit...
    pause >nul
    exit /b 1
)

:: Get pip version
for /f "tokens=*" %%i in ('pip --version') do set PIP_VERSION=%%i
echo ✅ %PIP_VERSION%

:: Create virtual environment if it doesn't exist
echo.
echo 📦 Setting up virtual environment...
if exist venv (
    echo ⚠️ Virtual environment already exists
    echo Delete existing virtual environment? (y/n)
    set /p DELETE_VENV=
    if /i "!DELETE_VENV!"=="y" (
        echo 🗑️ Deleting existing virtual environment...
        rd /s /q venv
        if !ERRORLEVEL! NEQ 0 (
            echo ❌ Error deleting virtual environment
            pause >nul
            exit /b 1
        )
        echo ✅ Existing virtual environment deleted
    )
)

:: Create new virtual environment
if not exist venv (
    echo 🛠️ Creating new virtual environment...
    python -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        echo ❌ Error creating virtual environment
        pause >nul
        exit /b 1
    )
    echo ✅ Virtual environment created
)

:: Activate virtual environment
echo 📋 Activating virtual environment...
call venv\Scripts\activate.bat
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Error activating virtual environment
    pause >nul
    exit /b 1
)

echo ✅ Virtual environment activated

:: Upgrade pip to latest version
echo 🔄 Upgrading pip...
python -m pip install --upgrade pip >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ⚠️ Failed to upgrade pip (continuing with current version)
) else (
    echo ✅ pip upgraded
)

:: Install dependencies
echo.
echo 📦 Installing dependencies...
if exist pyproject.toml (
    echo 🛠️ Installing dependencies from pyproject.toml...
    pip install -e .
    if !ERRORLEVEL! NEQ 0 (
        echo ❌ Error installing dependencies from pyproject.toml
        echo Try installing dependencies from requirements.txt?
        echo (y/n)
        set /p TRY_REQUIREMENTS=
        if /i "!TRY_REQUIREMENTS!"=="y" (
            if exist requirements.txt (
                echo 🛠️ Installing dependencies from requirements.txt...
                pip install -r requirements.txt
                if !ERRORLEVEL! NEQ 0 (
                    echo ❌ Error installing dependencies from requirements.txt
                    pause >nul
                    exit /b 1
                )
                echo ✅ Dependencies from requirements.txt installed
            ) else (
                echo ❌ requirements.txt not found
                pause >nul
                exit /b 1
            )
        ) else (
            pause >nul
            exit /b 1
        )
    ) else (
        echo ✅ Dependencies from pyproject.toml installed
    )
) else if exist requirements.txt (
    echo 🛠️ Installing dependencies from requirements.txt...
    pip install -r requirements.txt
    if !ERRORLEVEL! NEQ 0 (
        echo ❌ Error installing dependencies from requirements.txt
        pause >nul
        exit /b 1
    )
    echo ✅ Dependencies from requirements.txt installed
) else (
    echo ⚠️ Dependency files not found (pyproject.toml or requirements.txt)
    echo Installing minimal dependencies...
    pip install aiogram sentence-transformers python-dotenv faiss-cpu psutil
    if !ERRORLEVEL! NEQ 0 (
        echo ❌ Error installing minimal dependencies
        pause >nul
        exit /b 1
    )
    echo ✅ Minimal dependencies installed
)

:: Check configuration
echo.
echo 🔍 Checking configuration...

if not exist .env (
    echo ⚠️ .env file not found
    echo Creating .env template...
    (
        echo # Telegram Bot Configuration
        echo BOT_TOKEN=your_telegram_bot_token_here
        echo ADMIN_ID=your_telegram_user_id_here
        echo ACCESS_PASSWORD=your_access_password_here
        echo.
        echo # ML Model Configuration (optimized for i5-4570, 16GB RAM)
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
    echo ✅ .env template created. Please edit it with your data.
) else (
    echo ✅ .env file found
)

:: Check if ACCESS_PASSWORD is secure
echo 🔍 Checking password security...
findstr /C:"ACCESS_PASSWORD=" .env > temp_pass.txt
set /p PASSWORD_LINE=<temp_pass.txt
del temp_pass.txt
for /f "tokens=2 delims==" %%a in ("%PASSWORD_LINE%") do set ACCESS_PASSWORD=%%a

:: Check password strength
if "!ACCESS_PASSWORD!"=="your_access_password_here" (
    echo ⚠️ Default password detected!
    echo For security reasons, please change the default password in .env
    echo Recommended: Use a strong password with at least 8 characters including letters, numbers, and symbols
) else if "!ACCESS_PASSWORD!"=="" (
    echo ⚠️ No password found in .env
    echo Please set a strong ACCESS_PASSWORD in .env
) else (
    echo ✅ Password found in .env
    echo 🔐 For production use, ensure your password is strong and secure
)

if not exist data (
    echo 📁 Creating data directory...
    mkdir data
    echo ✅ Data directory created
)

if not exist data\faq.json (
    echo ⚠️ faq.json file not found
    echo Creating faq.json template...
    (
        echo []
    ) > data\faq.json
    echo ✅ faq.json template created
) else (
    echo ✅ faq.json file found
)

if not exist cache (
    echo 📁 Creating cache directory...
    mkdir cache
    echo ✅ Cache directory created
)

if not exist files (
    echo 📁 Creating files directory...
    mkdir files
    echo ✅ Files directory created
)

echo.
echo 📊 Installing development tools (optional)...
echo Install development tools? (y/n)
set /p INSTALL_DEV=
if /i "!INSTALL_DEV!"=="y" (
    echo 🛠️ Installing development tools...
    pip install black flake8 mypy pytest pytest-cov pytest-asyncio
    if !ERRORLEVEL! EQU 0 (
        echo ✅ Development tools installed
    ) else (
        echo ⚠️ Error installing development tools
    )
)

echo.
echo 🎉 Setup completed!
echo.
echo Next steps:
echo 1. Edit the .env file with your data
echo 2. Add data to data\faq.json
echo 3. Use 1_Start_Bot.bat to start the bot

echo.
echo Press any key to exit...
pause >nul
endlocal