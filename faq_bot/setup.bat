@echo off
title FAQ Bot - Setup...

echo ================================
echo   FAQ Bot - Setup Utility
echo ================================
echo.

echo 🔧 Setting up FAQ Bot environment...
echo This script will:
echo  - Install dependencies
echo  - Create necessary directories
echo  - Set up environment configuration
echo.

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
    if %errorlevel% neq 0 (
        echo Failed to activate virtual environment.
        pause
        exit /b 1
    )
    echo Virtual environment activated.
    echo.
) else (
    echo No virtual environment found. Using system Python.
    echo.
)

REM Install dependencies
if exist "requirements.txt" (
    echo Installing dependencies from requirements.txt...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo Failed to install dependencies.
        pause
        exit /b 1
    )
    echo Dependencies installed successfully.
    echo.
) else (
    echo requirements.txt not found. Installing key packages directly...
    pip install aiogram==3.3.0 sentence-transformers==2.2.2 faiss-cpu==1.7.4 python-dotenv==1.1.1 psutil==7.0.0 pytest==8.4.2
    if %errorlevel% neq 0 (
        echo Failed to install packages.
        pause
        exit /b 1
    )
    echo Packages installed successfully.
    echo.
)

REM Create directories
echo Creating necessary directories...
mkdir cache 2>nul
mkdir data 2>nul
mkdir logs 2>nul
echo Directories created.
echo.

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo Creating .env template...
    (
        echo # Telegram Bot Configuration
        echo BOT_TOKEN=your_telegram_bot_token_here
        echo ADMIN_ID=your_telegram_user_id_here
        echo ACCESS_PASSWORD=your_access_password_here
        echo.
        echo # ML Model Configuration
        echo MODEL_NAME=ai-forever/ru-en-RoSBERTa
        echo SIMILARITY_THRESHOLD=0.75
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
    echo .env template created. Please edit it with your configuration.
    echo.
) else (
    echo .env file already exists.
    echo.
)

echo.
echo 🎉 Setup completed successfully!
echo.
pause