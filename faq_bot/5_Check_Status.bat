@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion
title FAQ Bot - Status Check
echo 🔍 Проверка состояния FAQ бота...
echo.

cd /d "%~dp0"

:: Проверка Python
echo 🔧 Проверка Python...
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Python не найден
    echo Установите Python 3.8+ и добавьте в PATH
) else (
    for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
    echo ✅ %PYTHON_VERSION% найден
)

:: Проверка pip
echo.
echo 🔧 Проверка pip...
pip --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ pip не найден
    echo Установите Python с pip или установите pip отдельно
) else (
    for /f "tokens=*" %%i in ('pip --version') do set PIP_VERSION=%%i
    echo ✅ %PIP_VERSION% найден
)

:: Проверка виртуального окружения
echo.
echo 🔧 Проверка виртуального окружения...
if exist venv\Scripts\activate.bat (
    echo ✅ Виртуальное окружение найдено
    call venv\Scripts\activate.bat >nul 2>&1
    if !ERRORLEVEL! NEQ 0 (
        echo ⚠️ Ошибка активации виртуального окружения
    ) else (
        echo ✅ Виртуальное окружение активировано
    )
) else (
    echo ⚠️ Виртуальное окружение не найдено
    echo Запустите 0_Setup.bat для создания
)

:: Проверка необходимых пакетов
echo.
echo 🔧 Проверка необходимых пакетов...
set REQUIRED_PACKAGES=aiogram sentence-transformers python-dotenv faiss-cpu psutil
set MISSING_PACKAGES=

for %%p in (%REQUIRED_PACKAGES%) do (
    pip show %%p >nul 2>&1
    if !ERRORLEVEL! NEQ 0 (
        set MISSING_PACKAGES=!MISSING_PACKAGES! %%p
        echo ❌ %%p не установлен
    ) else (
        echo ✅ %%p установлен
    )
)

if defined MISSING_PACKAGES (
    echo.
    echo ⚠️ Некоторые пакеты отсутствуют: !MISSING_PACKAGES!
    echo Запустите 0_Setup.bat для установки зависимостей
)

:: Проверка конфигурационных файлов
echo.
echo 🔧 Проверка конфигурационных файлов...

if exist .env (
    echo ✅ Файл .env найден
) else (
    echo ⚠️ Файл .env не найден
    echo Создайте .env файл или запустите 0_Setup.bat
)

if exist data\faq.json (
    echo ✅ Файл data\faq.json найден
) else (
    echo ⚠️ Файл data\faq.json не найден
    echo Добавьте данные в faq.json
)

if exist cache (
    echo ✅ Директория cache найдена
) else (
    echo ⚠️ Директория cache не найдена
    echo Создайте директорию cache или запустите 0_Setup.bat
)

:: Проверка скриптов
echo.
echo 🔧 Проверка скриптов...

if exist run_bot.py (
    echo ✅ run_bot.py найден
) else (
    echo ❌ run_bot.py не найден
)

if exist src\main.py (
    echo ✅ src\main.py найден
) else (
    echo ❌ src\main.py не найден
)

:: Проверка модели (опционально)
echo.
echo 🔧 Проверка модели...

if exist cache\faq_embeddings.pkl (
    echo ✅ Эмбеддинги модели найдены
) else (
    echo ⚠️ Эмбеддинги модели не найдены
    echo Запустите 4_Train_Model.bat для создания
)

if exist cache\faq_index.faiss (
    echo ✅ Индекс модели найден
) else (
    echo ⚠️ Индекс модели не найден
    echo Запустите 4_Train_Model.bat для создания
)

:: Проверка файлов FAQ
echo.
echo 🔧 Проверка файлов FAQ...

if exist files (
    echo ✅ Директория files найдена
    
    :: Подсчет файлов
    set FILE_COUNT=0
    for /f "tokens=*" %%i in ('dir files /b /a-d ^| find /c /v ""') do set FILE_COUNT=%%i
    echo Файлов в директории files: !FILE_COUNT!
) else (
    echo ⚠️ Директория files не найдена
)

:: Проверка соответствия файлов faq.json
echo.
echo 🔧 Проверка соответствия файлов в faq.json...

python -c "import sys; sys.path.insert(0, 'src'); from utils import validate_faq_files; missing, valid = validate_faq_files('data/faq.json'); print(f'Valid files: {len(valid)}'); print(f'Missing files: {len(missing)}'); sys.exit(1 if missing else 0)" >nul 2>&1
if !ERRORLEVEL! NEQ 0 (
    echo ⚠️ Найдены отсутствующие файлы в faq.json
    echo Запустите python tests/test_file_validation.py для получения деталей
) else (
    echo ✅ Все файлы из faq.json найдены
)

:: Проверка логов
echo.
echo 🔧 Проверка логов...

if exist logs (
    echo ✅ Директория logs найдена
    
    :: Проверка основного лог-файла
    if exist logs\bot.log (
        for /f "tokens=*" %%i in ('dir logs\bot.log /a-d ^| findstr /r /c:"^[0-9]"') do set LOG_SIZE=%%i
        echo Основной лог-файл: !LOG_SIZE! байт
    ) else (
        echo Основной лог-файл: не найден
    )
    
    :: Подсчет архивных логов
    set ARCHIVE_COUNT=0
    if exist logs\archive (
        for /f "tokens=*" %%i in ('dir logs\archive /b /a-d ^| find /c /v ""') do set ARCHIVE_COUNT=%%i
        echo Архивные логи: !ARCHIVE_COUNT! директорий
    ) else (
        echo Архивные логи: нет
    )
) else (
    echo ⚠️ Директория logs не найдена
)

:: Информация о системе
echo.
echo 🔧 Информация о системе...
echo Система: %OS%
echo Архитектура: %PROCESSOR_ARCHITECTURE%
echo Каталог: %CD%

:: Статистика кэша
echo.
echo 📊 Статистика кэша...
if exist cache (
    for /f "tokens=*" %%i in ('dir cache /b /a-d ^| find /c /v ""') do set CACHE_FILES=%%i
    echo Файлов в кэше: !CACHE_FILES!
) else (
    echo Кэш не найден
)

echo.
echo 🎉 Проверка состояния завершена!
echo.
echo Нажмите любую клавишу для выхода...
pause >nul
endlocal