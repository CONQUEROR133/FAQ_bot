@echo off
title FAQ Bot - Model Training...

echo ================================
echo   FAQ Bot - Model Training
echo ================================
echo.

REM Activate virtual environment if it exists
if exist "..\test_venv\Scripts\activate.bat" (
    echo 🔧 Activating virtual environment...
    call ..\test_venv\Scripts\activate.bat
    echo ✅ Virtual environment activated
    echo.
) else (
    echo ⚠️  No virtual environment found, using system Python
    echo.
)

echo 🧠 Training FAQ Bot model...
echo This may take several minutes depending on your dataset size
echo.

python run.py train

echo.
echo Training process completed
pause