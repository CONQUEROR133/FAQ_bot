@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion
title FAQ Bot - Clear Statistics

echo 🧹 Clearing FAQ Bot Statistics...
echo.

cd /d "%~dp0"

:: Check if logs directory exists
if not exist logs (
    echo ❌ Error: logs directory not found!
    echo Please make sure the bot has been run at least once.
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 1
)

:: Check if Python is available
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Error: Python not found!
    echo Please install Python 3.8+ and add it to your PATH.
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 1
)

:: Ask for confirmation
echo ⚠️  This will archive all log files and start fresh statistics.
echo.
set /p CONFIRM=Are you sure you want to clear statistics? [y/N]: 

if /i "!CONFIRM!" NEQ "y" if /i "!CONFIRM!" NEQ "yes" (
    echo.
    echo ❌ Statistics clearing cancelled.
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 0
)

:: Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    echo.
    echo 🔧 Activating virtual environment...
    call venv\Scripts\activate.bat >nul 2>&1
    if !ERRORLEVEL! NEQ 0 (
        echo ⚠️  Warning: Could not activate virtual environment
    ) else (
        echo ✅ Virtual environment activated
    )
)

:: Run the stats clearing command
echo.
echo 🔄 Clearing statistics...
python tools\aggregate_stats.py --clear-stats

if !ERRORLEVEL! EQU 0 (
    echo.
    echo ✅ Statistics cleared successfully!
) else (
    echo.
    echo ❌ Error clearing statistics!
    echo Please check the logs for more information.
)

echo.
echo Press any key to exit...
pause >nul
endlocal