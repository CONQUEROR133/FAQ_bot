@echo off
chcp 65001 >nul
cls

echo.
echo ================================================================
echo    Универсальный загрузчик FAQ - Поддерживает ВСЕ файлы
echo    Universal FAQ Loader - Supports ALL file types
echo ================================================================
echo.

REM Set working directory to script location
cd /d "%~dp0"

REM Check Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python не найден. Установите Python 3.7 или выше.
    echo ❌ Python not found. Please install Python 3.7 or higher.
    echo.
    echo Скачать Python / Download Python: https://python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo ✅ Python найден / Python found
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo 📦 Создаем виртуальное окружение...
    echo 📦 Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ❌ Ошибка создания виртуального окружения
        echo ❌ Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo 🔧 Активируем виртуальное окружение...
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Check and install basic dependencies
echo 📋 Проверяем зависимости...
echo 📋 Checking dependencies...
python -c "import tkinter" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Tkinter не доступен. Установите Python с Tkinter.
    echo ❌ Tkinter not available. Install Python with Tkinter.
    pause
    exit /b 1
)

REM Install requirements if file exists
if exist "requirements.txt" (
    echo 📦 Устанавливаем зависимости из requirements.txt...
    echo 📦 Installing dependencies from requirements.txt...
    pip install -r requirements.txt --quiet
)

REM Install basic required packages
echo 📦 Устанавливаем базовые пакеты...
echo 📦 Installing basic packages...
pip install pandas openpyxl --quiet

REM Check if universal loader exists
if not exist "universal_loader\universal_faq_gui.py" (
    echo ❌ Файл universal_faq_gui.py не найден в папке universal_loader
    echo ❌ universal_faq_gui.py not found in universal_loader folder
    echo.
    echo Убедитесь, что все файлы на месте.
    echo Make sure all files are in place.
    pause
    exit /b 1
)

echo.
echo 🚀 Запускаем Универсальный загрузчик FAQ...
echo 🚀 Starting Universal FAQ Loader...
echo.
echo Поддерживаемые типы файлов:
echo Supported file types:
echo   📷 Изображения/Images: JPG, PNG, GIF, BMP, TIFF, WEBP
echo   📄 Документы/Documents: PDF, DOC, DOCX, RTF, ODT
echo   📊 Таблицы/Spreadsheets: CSV, XLSX, XLS, ODS, TSV
echo   📝 Текст/Text: TXT, MD, RST, LOG, CFG, INI
echo   📦 Архивы/Archives: ZIP, RAR, 7Z, TAR, GZ
echo   💻 Код/Code: PY, JS, HTML, CSS, SQL, PHP, JAVA
echo   🌟 И любые другие файлы! / And any other files!
echo.
echo ================================================================
echo.

REM Launch the GUI
python universal_loader\universal_faq_gui.py

REM Check exit code
if %errorlevel% neq 0 (
    echo.
    echo ❌ Ошибка запуска программы
    echo ❌ Error starting the program
    echo.
    echo Код ошибки / Error code: %errorlevel%
    echo.
    echo Попробуйте:
    echo Try:
    echo 1. Перезапустить как администратор
    echo    Restart as administrator
    echo 2. Проверить путь к файлам
    echo    Check file paths
    echo 3. Переустановить зависимости
    echo    Reinstall dependencies
    echo.
    pause
) else (
    echo.
    echo ✅ Программа завершена успешно
    echo ✅ Program completed successfully
    echo.
)

REM Deactivate virtual environment
deactivate

echo Нажмите любую клавишу для выхода...
echo Press any key to exit...
pause >nul