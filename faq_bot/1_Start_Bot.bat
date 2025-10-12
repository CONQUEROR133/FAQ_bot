@echo off
chcp 65001 > nul
title FAQ Bot - Running
echo 🤖 Starting FAQ Bot...
echo.

:: Navigate to the project parent directory
cd /d "%~dp0"

:: Check for required files
echo 🔍 Checking required files...

if not exist run_bot.py (
    echo ❌ Error: run_bot.py not found!
    echo Press any key to exit...
    timeout /t 5 /nobreak >nul
    exit /b 1
)
echo ✅ run_bot.py found

if not exist src\main.py (
    echo ❌ Error: src\main.py not found!
    echo Press any key to exit...
    timeout /t 5 /nobreak >nul
    exit /b 1
)
echo ✅ src\main.py found

if not exist .env (
    echo ⚠️  .env file not found
    echo Please create .env file or run 0_Setup.bat
    echo Press any key to exit...
    timeout /t 5 /nobreak >nul
    exit /b 1
)
echo ✅ .env file found

:: Check if .env has required variables
echo 🔍 Checking .env configuration...
findstr /C:"BOT_TOKEN=" .env >nul
if errorlevel 1 (
    echo ⚠️  BOT_TOKEN not found in .env
    echo Please add BOT_TOKEN to your .env file
    echo Press any key to exit...
    timeout /t 5 /nobreak >nul
    exit /b 1
)
echo ✅ BOT_TOKEN found in .env

if not exist data\faq.json (
    echo ⚠️  data\faq.json not found
    echo Please add data to faq.json or run 0_Setup.bat
    echo Press any key to exit...
    timeout /t 5 /nobreak >nul
    exit /b 1
)
echo ✅ data\faq.json found

:: Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    echo 💾 Activating virtual environment...
    call venv\Scripts\activate.bat
    echo ✅ Virtual environment activated
)

:: Check if required Python packages are installed
echo 🔍 Checking Python dependencies...
python -c "import aiogram" 2>nul
if errorlevel 1 (
    echo ⚠️  aiogram not installed
    echo Please run 0_Setup.bat to install dependencies
    echo Press any key to exit...
    timeout /t 5 /nobreak >nul
    exit /b 1
)
echo ✅ aiogram installed

python -c "import sentence_transformers" 2>nul
if errorlevel 1 (
    echo ⚠️  sentence_transformers not installed
    echo Please run 0_Setup.bat to install dependencies
    echo Press any key to exit...
    timeout /t 5 /nobreak >nul
    exit /b 1
)
echo ✅ sentence_transformers installed

:: Start the bot
echo.
echo ▶️  Starting bot...
echo.
echo 📋 Logs will be written to cache\bot.log
echo 🛑 Press Ctrl+C to stop the bot
echo.

timeout /t 3 /nobreak >nul

echo Starting bot...
python run_bot.py
set EXIT_CODE=%ERRORLEVEL%

echo.
if "%EXIT_CODE%"=="0" (
    echo ✅ Bot stopped normally
) else (
    echo ❌ Bot stopped with error (Error Level: %EXIT_CODE%)
    
    :: Check for logs
    if exist cache\bot.log (
        echo 📋 Last log lines:
        powershell -Command "Get-Content cache\bot.log -Tail 20"
        echo.
        echo 💾 Full log saved in cache\bot.log
    )
)

echo.
echo 📊 Execution statistics:
echo    Start time: %date% %time%

if "%EXIT_CODE%"=="0" (
    echo    Status: Success
) else (
    echo    Status: Error (%EXIT_CODE%)
)

echo.
echo Press any key to exit...
timeout /t 15 /nobreak >nul