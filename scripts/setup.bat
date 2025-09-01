@echo off
chcp 65001 > nul
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

echo ✅ Python найден:
python --version

:: Проверка pip
pip --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ pip не найден! Проверьте установку Python
    echo Нажмите любую клавишу для выхода...
    pause >nul
    exit /b 1
)

echo ✅ pip найден

:: Создание виртуального окружения если не существует
if not exist venv (
    echo 📦 Создание виртуального окружения...
    python -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        echo ❌ Ошибка создания виртуального окружения
        pause >nul
        exit /b 1
    )
    echo ✅ Виртуальное окружение создано
) else (
    echo ✅ Виртуальное окружение уже существует
)

:: Активация виртуального окружения
echo 📋 Активация виртуального окружения...
call venv\Scripts\activate.bat

:: Установка зависимостей
echo 📦 Установка зависимостей...
if exist requirements.txt (
    pip install -r requirements.txt
    if %ERRORLEVEL% NEQ 0 (
        echo ❌ Ошибка установки зависимостей из requirements.txt
        pause >nul
        exit /b 1
    )
    echo ✅ Зависимости из requirements.txt установлены
) else (
    echo 📦 requirements.txt не найден, устанавливаем базовые зависимости...
    pip install sentence-transformers aiogram python-dotenv faiss-cpu
    if %ERRORLEVEL% NEQ 0 (
        echo ❌ Ошибка установки базовых зависимостей
        pause >nul
        exit /b 1
    )
    echo ✅ Базовые зависимости установлены
)

:: Установка дополнительных зависимостей для bulk loading
echo 🔄 Установка дополнительных зависимостей для массовой загрузки...
pip install pandas openpyxl tkinterdnd2
if %ERRORLEVEL% NEQ 0 (
    echo ⚠️ Некоторые дополнительные зависимости не установлены (не критично)
) else (
    echo ✅ Дополнительные зависимости установлены
)

:: Проверка конфигурации
echo.
echo 🔍 Проверка конфигурации...

if not exist .env (
    echo ⚠️ Файл .env не найден
    echo Создайте файл .env с токеном бота:
    echo BOT_TOKEN=your_bot_token_here
)

if not exist faq.json (
    echo ⚠️ Файл faq.json не найден
    echo Убедитесь что файл faq.json существует
)

if not exist config.py (
    echo ⚠️ Файл config.py не найден
)

echo.
echo 🎉 Настройка завершена!
echo Используйте start_bot.bat для запуска бота
echo Нажмите любую клавишу для выхода...
pause >nul