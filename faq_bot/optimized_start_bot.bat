@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion
title Telegram FAQ Bot - Running
echo ====================================================
echo           Starting Telegram FAQ Bot
echo ====================================================
echo.

:: Check if running from the correct directory
if not exist "run_bot.py" (
    echo ❌ Error: Please run this script from the project root directory
    echo    Current directory: %CD%
    echo    Make sure run_bot.py exists in this directory
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 1
)

:: Check required files
echo 🔍 Checking required files...
set MISSING_FILES=0

if not exist "src\main.py" (
    echo ❌ Error: src\main.py not found
    set MISSING_FILES=1
)

if not exist ".env" (
    echo ❌ Error: .env file not found
    echo    Please run setup.bat first or create .env manually
    set MISSING_FILES=1
)

if not exist "data\faq.json" (
    echo ❌ Error: data\faq.json not found
    echo    Please create FAQ data or run setup.bat
    set MISSING_FILES=1
)

if !MISSING_FILES! EQU 1 (
    echo.
    echo Please fix the missing files and try again
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 1
)

echo ✅ All required files found

:: Activate virtual environment if it exists
echo.
echo 💾 Checking virtual environment...
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat >nul 2>&1
    if !ERRORLEVEL! NEQ 0 (
        echo ⚠️  Warning: Failed to activate virtual environment
        echo    Continuing with system Python...
    ) else (
        echo ✅ Virtual environment activated
    )
) else (
    echo ⚠️  Virtual environment not found
    echo    Using system Python...
)

:: Check if required Python packages are installed
echo.
echo 🔍 Checking required packages...
python -c "import aiogram" >nul 2>&1
if !ERRORLEVEL! NEQ 0 (
    echo ❌ Error: aiogram package not installed
    echo    Please run setup.bat to install dependencies
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 1
)

python -c "import sentence_transformers" >nul 2>&1
if !ERRORLEVEL! NEQ 0 (
    echo ❌ Error: sentence-transformers package not installed
    echo    Please run setup.bat to install dependencies
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 1
)

echo ✅ All required packages are installed

:: Start the bot
echo.
echo ▶️  Starting Telegram FAQ Bot...
echo.
echo 📋 Logs will be written to logs/bot.log
echo 🛑 Press Ctrl+C to stop the bot
echo.
echo Starting in 3 seconds...
timeout /t 3 /nobreak >nul

echo ====================================================
python run_bot.py
set EXIT_CODE=%ERRORLEVEL%

echo.
echo ====================================================
if "%EXIT_CODE%"=="0" (
    echo ✅ Bot stopped normally
) else (
    echo ❌ Bot stopped with error (Exit Code: %EXIT_CODE%)
    
    :: Check for log file and display last few lines
    if exist "logs\bot.log" (
        echo.
        echo 📋 Last 10 lines from bot.log:
        powershell -Command "Get-Content logs\bot.log -Tail 10"
    )
)

echo.
echo Press any key to exit...
pause >nul
endlocal