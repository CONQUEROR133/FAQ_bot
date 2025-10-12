@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion
title Telegram FAQ Bot - Model Training
echo ====================================================
echo        Telegram FAQ Bot - Model Training
echo ====================================================
echo.

:: Check if running from the correct directory
if not exist "data\faq.json" (
    echo ❌ Error: Please run this script from the project root directory
    echo    Current directory: %CD%
    echo    Make sure data\faq.json exists in this directory
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 1
)

:: Activate virtual environment if it exists
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
python -c "import sentence_transformers" >nul 2>&1
if !ERRORLEVEL! NEQ 0 (
    echo ❌ Error: sentence-transformers package not installed
    echo    Please run setup.bat to install dependencies
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 1
)

python -c "import faiss" >nul 2>&1
if !ERRORLEVEL! NEQ 0 (
    echo ❌ Error: faiss package not installed
    echo    Please run setup.bat to install dependencies
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 1
)

echo ✅ All required packages are installed

:: Check if FAQ data exists
echo.
echo 🔍 Checking FAQ data...
if not exist "data\faq.json" (
    echo ❌ Error: data\faq.json not found
    echo    Please add FAQ data before training the model
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 1
)

:: Check file size
for %%A in (data\faq.json) do (
    set FAQ_SIZE=%%~zA
)
if !FAQ_SIZE! EQU 0 (
    echo ❌ Error: data\faq.json is empty
    echo    Please add FAQ entries before training the model
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 1
)

echo ✅ FAQ data found (!FAQ_SIZE! bytes)

:: Create cache directory if it doesn't exist
echo.
echo 📁 Checking cache directory...
if not exist "cache" (
    echo Creating cache directory...
    mkdir cache >nul 2>&1
    if !ERRORLEVEL! NEQ 0 (
        echo ❌ Error: Failed to create cache directory
        echo.
        echo Press any key to exit...
        pause >nul
        exit /b 1
    )
    echo ✅ Cache directory created
) else (
    echo ✅ Cache directory exists
)

:: Confirmation prompt
echo.
echo ⚠️  WARNING: Model training will:
echo    - Rebuild all embeddings from FAQ data
echo    - Overwrite existing model files
echo    - Take several minutes depending on data size
echo.
echo Continue with model training? (y/N)
set /p CONFIRM_TRAIN=
if /i not "%CONFIRM_TRAIN%"=="y" (
    echo ❌ Model training cancelled
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 0
)

:: Start training
echo.
echo ▶️  Starting model training...
echo.
echo This may take several minutes. Please wait...
echo.

:: Use the existing train_model.py script if it exists, otherwise use src/train_model.py
if exist "train_model.py" (
    set TRAIN_SCRIPT=train_model.py
    echo Using train_model.py
) else if exist "src\train_model.py" (
    set TRAIN_SCRIPT=src\train_model.py
    echo Using src\train_model.py
) else (
    echo ❌ Error: Training script not found
    echo    Please ensure train_model.py or src/train_model.py exists
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 1
)

echo ====================================================
python !TRAIN_SCRIPT!
set EXIT_CODE=%ERRORLEVEL%

echo.
echo ====================================================
if %EXIT_CODE% EQU 0 (
    echo ✅ Model training completed successfully!
    
    :: Show resulting files
    echo.
    echo 📁 Training results:
    if exist "cache\faq_embeddings.pkl" (
        for %%A in (cache\faq_embeddings.pkl) do (
            echo    faq_embeddings.pkl: %%~zA bytes
        )
    )
    if exist "cache\faq_index.faiss" (
        for %%A in (cache\faq_index.faiss) do (
            echo    faq_index.faiss: %%~zA bytes
        )
    )
) else (
    echo ❌ Model training failed (Exit Code: %EXIT_CODE%)
    
    :: Check for log file and display last few lines
    if exist "logs\training.log" (
        echo.
        echo 📋 Last 10 lines from training.log:
        powershell -Command "Get-Content logs\training.log -Tail 10"
    ) else if exist "training.log" (
        echo.
        echo 📋 Last 10 lines from training.log:
        powershell -Command "Get-Content training.log -Tail 10"
    )
)

echo.
echo Press any key to exit...
pause >nul
endlocal