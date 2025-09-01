@echo off
echo ===============================
echo    FAQ Bot Setup Script
echo ===============================
echo.

REM Navigate to project root
cd /d "%~dp0"

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ and add it to PATH
    pause
    exit /b 1
)

echo ✅ Python found
python --version

REM Check if pip is available
pip --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ❌ pip is not available
    echo Please ensure pip is installed with Python
    pause
    exit /b 1
)

echo ✅ pip found

REM Install/upgrade pip
echo.
echo 📦 Upgrading pip...
python -m pip install --upgrade pip

REM Install all dependencies from requirements.txt
echo.
echo 📦 Installing dependencies from requirements.txt...
pip install -r requirements.txt

if %ERRORLEVEL% neq 0 (
    echo.
    echo ❌ Failed to install some dependencies
    echo Please check the error messages above
    pause
    exit /b 1
)

echo.
echo ✅ All dependencies installed successfully

REM Verify critical imports
echo.
echo 🔍 Verifying critical dependencies...

python -c "import psutil; print('✅ psutil:', psutil.__version__)" 2>nul || echo "❌ psutil import failed"
python -c "import aiogram; print('✅ aiogram:', aiogram.__version__)" 2>nul || echo "❌ aiogram import failed"
python -c "import sentence_transformers; print('✅ sentence-transformers available')" 2>nul || echo "❌ sentence-transformers import failed"
python -c "import faiss; print('✅ faiss-cpu available')" 2>nul || echo "❌ faiss-cpu import failed"
python -c "import numpy; print('✅ numpy:', numpy.__version__)" 2>nul || echo "❌ numpy import failed"

REM Check configuration
echo.
echo ⚙️ Checking configuration...

if exist .env (
    echo ✅ .env file found
) else (
    echo ❌ .env file not found
    echo Please create .env file with BOT_TOKEN, ADMIN_ID, and ACCESS_PASSWORD
)

REM Create necessary directories
echo.
echo 📁 Creating necessary directories...

if not exist "logs\" mkdir logs
if not exist "cache\" mkdir cache
if not exist "data\" mkdir data
if not exist "files\" mkdir files

echo ✅ Directory structure verified

REM Test basic bot configuration
echo.
echo 🧪 Testing bot configuration...
python -c "
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
try:
    from config import config
    print('✅ Configuration loaded successfully')
    print('   BOT_TOKEN:', 'SET' if config.BOT_TOKEN else 'NOT SET')
    print('   ADMIN_ID:', config.ADMIN_ID if hasattr(config, 'ADMIN_ID') else 'NOT SET')
except Exception as e:
    print('❌ Configuration error:', e)
"

echo.
echo ===============================
echo    Setup Complete!
echo ===============================
echo.
echo You can now start the bot using:
echo   • python run_bot.py
echo   • Or double-click start.bat
echo   • Or use restart_bot_clean.py for clean restart
echo.
pause