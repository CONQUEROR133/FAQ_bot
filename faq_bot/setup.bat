@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion
title FAQ Bot - Setup

echo 🛠️ FAQ Bot Setup
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

:: Run the console setup tool
echo ▶️ Launching setup tool...
echo.

!PYTHON! setup.py

echo.
echo ✅ Setup tool finished
echo Press any key to exit...
pause >nul
endlocal