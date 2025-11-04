@echo off
title FAQ Bot Launcher
setlocal enabledelayedexpansion

echo ========================================
echo   FAQ Bot - Telegram FAQ Service Bot   
echo ========================================
echo.
echo [INFO] Starting FAQ Bot Launcher...

:: Check if we're in the correct directory
if not exist "src\main.py" (
    echo [ERROR] Error: Cannot find bot files.
    echo Please run this script from the project root directory.
    echo.
    pause
    exit /b 1
)

:: Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Error: Python is not installed or not in PATH.
    echo Please install Python 3.8 or higher.
    echo.
    pause
    exit /b 1
)

:: Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo [INFO] Activating virtual environment...
    call venv\Scripts\activate.bat
    if !errorlevel! neq 0 (
        echo [ERROR] Failed to activate virtual environment.
        echo.
        pause
        exit /b 1
    )
    echo [SUCCESS] Virtual environment activated.
    echo.
)

:: Check if required packages are installed
echo [INFO] Checking dependencies...
python -c "import aiogram" >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARN] Warning: Required packages not found.
    echo Installing dependencies...
    pip install -r requirements.txt
    if !errorlevel! neq 0 (
        echo [ERROR] Failed to install dependencies.
        echo.
        pause
        exit /b 1
    )
    echo [SUCCESS] Dependencies installed.
    echo.
)

:: Display configuration info
for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo [CONFIG] Configuration:
echo    - Python: %PYTHON_VERSION%
echo    - Working Dir: %CD%
echo    - Bot Token: [Protected]
echo.

:: Start the bot
echo [START] Starting FAQ Bot...
echo Press Ctrl+C to stop the bot.
echo.
python src/main.py

if %errorlevel% equ 0 (
    echo [SUCCESS] Bot stopped successfully.
) else (
    echo [ERROR] Bot stopped with error code: %errorlevel%
)

echo.
pause