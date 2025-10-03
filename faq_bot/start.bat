@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion
title FAQ Bot - Running

echo 🤖 Starting FAQ Bot...
echo.

:: Check if virtual environment exists
if exist venv\Scripts\python.exe (
    echo 💾 Using virtual environment...
    set PYTHON=venv\Scripts\python.exe
) else (
    echo ⚠️ No virtual environment found, using system Python
    set PYTHON=python
)

:: Check if Python is available
!PYTHON! --version >nul 2>&1
if !ERRORLEVEL! NEQ 0 (
    echo ❌ Python not found! Please install Python 3.8+ and add it to PATH
    echo Press any key to exit...
    pause >nul
    exit /b 1
)

:: Check required files
echo 🔍 Checking required files...

if not exist run_bot.py (
    echo ❌ Error: run_bot.py not found!
    echo Press any key to exit...
    pause >nul
    exit /b 1
)

if not exist src\main.py (
    echo ❌ Error: src\main.py not found!
    echo Press any key to exit...
    pause >nul
    exit /b 1
)

if not exist .env (
    echo ⚠️ .env file not found
    echo Please create .env file or run setup first
    echo Press any key to exit...
    pause >nul
    exit /b 1
)

if not exist data\faq.json (
    echo ⚠️ data\faq.json not found
    echo Please add FAQ data or run setup first
    echo Press any key to exit...
    pause >nul
    exit /b 1
)

:: Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    echo 💾 Activating virtual environment...
    call venv\Scripts\activate.bat
)

:: Run the bot directly
echo ▶️ Starting bot...
echo 📋 Logs will be written to cache/bot.log
echo 🛑 Press Ctrl+C to stop the bot
echo.

timeout /t 2 /nobreak >nul

!PYTHON! run_bot.py

set EXIT_CODE=%ERRORLEVEL%

echo.
if "%EXIT_CODE%"=="0" (
    echo ✅ Bot stopped normally
) else (
    echo ❌ Bot stopped with error (Error Level: %EXIT_CODE%)
)

echo.
echo Press any key to exit...
pause >nul
endlocal