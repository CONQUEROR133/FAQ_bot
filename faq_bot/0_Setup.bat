@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion
title FAQ Bot - Setup & Installation
echo 🔧 Настройка FAQ бота...
echo.

:: Проверка Python
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Python не найден! Установите Python 3.8+ и добавьте в PATH
    echo Нажмите любую клавишу для выхода...
    pause >nul
    exit /b 1
)

:: Получаем версию Python
for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo ✅ %PYTHON_VERSION%

:: Проверка pip
pip --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ pip не найден! Проверьте установку Python
    echo Нажмите любую клавишу для выхода...
    pause >nul
    exit /b 1
)

:: Получаем версию pip
for /f "tokens=*" %%i in ('pip --version') do set PIP_VERSION=%%i
echo ✅ %PIP_VERSION%

:: Создание виртуального окружения если не существует
echo.
echo 📦 Настройка виртуального окружения...
if exist venv (
    echo ⚠️ Виртуальное окружение уже существует
    echo Удалить существующее виртуальное окружение? (y/n)
    set /p DELETE_VENV=
    if /i "!DELETE_VENV!"=="y" (
        echo 🗑️ Удаление существующего виртуального окружения...
        rd /s /q venv
        if !ERRORLEVEL! NEQ 0 (
            echo ❌ Ошибка удаления виртуального окружения
            pause >nul
            exit /b 1
        )
        echo ✅ Существующее виртуальное окружение удалено
    )
)

:: Создание нового виртуального окружения
if not exist venv (
    echo 🛠️ Создание нового виртуального окружения...
    python -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        echo ❌ Ошибка создания виртуального окружения
        pause >nul
        exit /b 1
    )
    echo ✅ Виртуальное окружение создано
)

:: Активация виртуального окружения
echo 📋 Активация виртуального окружения...
call venv\Scripts\activate.bat
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Ошибка активации виртуального окружения
    pause >nul
    exit /b 1
)

echo ✅ Виртуальное окружение активировано

:: Обновление pip до последней версии
echo 🔄 Обновление pip...
python -m pip install --upgrade pip >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ⚠️ Не удалось обновить pip (продолжаем с текущей версией)
) else (
    echo ✅ pip обновлен
)

:: Установка зависимостей
echo.
echo 📦 Установка зависимостей...
if exist pyproject.toml (
    echo 🛠️ Установка зависимостей из pyproject.toml...
    pip install -e .
    if !ERRORLEVEL! NEQ 0 (
        echo ❌ Ошибка установки зависимостей из pyproject.toml
        echo Попробовать установить зависимости из requirements.txt?
        echo (y/n)
        set /p TRY_REQUIREMENTS=
        if /i "!TRY_REQUIREMENTS!"=="y" (
            if exist requirements.txt (
                echo 🛠️ Установка зависимостей из requirements.txt...
                pip install -r requirements.txt
                if !ERRORLEVEL! NEQ 0 (
                    echo ❌ Ошибка установки зависимостей из requirements.txt
                    pause >nul
                    exit /b 1
                )
                echo ✅ Зависимости из requirements.txt установлены
            ) else (
                echo ❌ requirements.txt не найден
                pause >nul
                exit /b 1
            )
        ) else (
            pause >nul
            exit /b 1
        )
    ) else (
        echo ✅ Зависимости из pyproject.toml установлены
    )
) else if exist requirements.txt (
    echo 🛠️ Установка зависимостей из requirements.txt...
    pip install -r requirements.txt
    if !ERRORLEVEL! NEQ 0 (
        echo ❌ Ошибка установки зависимостей из requirements.txt
        pause >nul
        exit /b 1
    )
    echo ✅ Зависимости из requirements.txt установлены
) else (
    echo ⚠️ Файлы зависимостей не найдены (pyproject.toml или requirements.txt)
    echo Установка минимальных зависимостей...
    pip install aiogram sentence-transformers python-dotenv faiss-cpu psutil
    if !ERRORLEVEL! NEQ 0 (
        echo ❌ Ошибка установки минимальных зависимостей
        pause >nul
        exit /b 1
    )
    echo ✅ Минимальные зависимости установлены
)

:: Проверка конфигурации
echo.
echo 🔍 Проверка конфигурации...

if not exist .env (
    echo ⚠️ Файл .env не найден
    echo Создание шаблона .env файла...
    (
        echo # Telegram Bot Configuration
        echo BOT_TOKEN=your_telegram_bot_token_here
        echo ADMIN_ID=your_telegram_user_id_here
        echo ACCESS_PASSWORD=your_access_password_here
        echo.
        echo # ML Model Configuration (оптимизировано для i5-4570, 16GB RAM)
        echo MODEL_NAME=ai-forever/ru-en-RoSBERTa
        echo SIMILARITY_THRESHOLD=0.73
        echo BATCH_SIZE=16
        echo CACHE_SIZE=500
        echo EMBEDDING_CACHE_SIZE=1000
        echo.
        echo # Network Configuration
        echo REQUEST_TIMEOUT=30
        echo CONNECT_TIMEOUT=30
        echo READ_TIMEOUT=30
        echo MAX_RETRIES=3
        echo RETRY_DELAY=1
    ) > .env
    echo ✅ Шаблон .env создан. Пожалуйста, отредактируйте его с вашими данными.
) else (
    echo ✅ Файл .env найден
)

if not exist data (
    echo 📁 Создание директории data...
    mkdir data
    echo ✅ Директория data создана
)

if not exist data\faq.json (
    echo ⚠️ Файл faq.json не найден
    echo Создание шаблона faq.json...
    (
        echo []
    ) > data\faq.json
    echo ✅ Шаблон faq.json создан
) else (
    echo ✅ Файл faq.json найден
)

if not exist cache (
    echo 📁 Создание директории cache...
    mkdir cache
    echo ✅ Директория cache создана
)

if not exist files (
    echo 📁 Создание директории files...
    mkdir files
    echo ✅ Директория files создана
)

echo.
echo 📊 Установка дополнительных инструментов разработки (опционально)...
echo Установить инструменты разработки? (y/n)
set /p INSTALL_DEV=
if /i "!INSTALL_DEV!"=="y" (
    echo 🛠️ Установка инструментов разработки...
    pip install black flake8 mypy pytest pytest-cov pytest-asyncio
    if !ERRORLEVEL! EQU 0 (
        echo ✅ Инструменты разработки установлены
    ) else (
        echo ⚠️ Ошибка установки инструментов разработки
    )
)

echo.
echo 🎉 Настройка завершена!
echo.
echo Следующие шаги:
echo 1. Отредактируйте файл .env с вашими данными
echo 2. Добавьте данные в файл data\faq.json
echo 3. Используйте 1_Start_Bot.bat для запуска бота

echo.
echo Нажмите любую клавишу для выхода...
pause >nul
endlocal