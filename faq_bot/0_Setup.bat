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
if exist pyproject.toml (
    pip install -e .
    if %ERRORLEVEL% NEQ 0 (
        echo ❌ Ошибка установки зависимостей из pyproject.toml
        pause >nul
        exit /b 1
    )
    echo ✅ Зависимости из pyproject.toml установлены
) else (
    echo 📦 pyproject.toml не найден, устанавливаем базовые зависимости...
    pip install sentence-transformers aiogram python-dotenv faiss-cpu
    if %ERRORLEVEL% NEQ 0 (
        echo ❌ Ошибка установки базовых зависимостей
        pause >nul
        exit /b 1
    )
    echo ✅ Базовые зависимости установлены
)

:: Проверка конфигурации
echo.
echo 🔍 Проверка конфигурации...

if not exist .env (
    echo ⚠️ Файл .env не найден
    echo Создайте файл .env с токеном бота:
    echo BOT_TOKEN=your_bot_token_here
)

if not exist data\faq.json (
    echo ⚠️ Файл faq.json не найден
    echo Убедитесь что файл faq.json существует в папке data\
)

echo.
echo 🎉 Настройка завершена!
echo Используйте 1_Start_Bot.bat для запуска бота
echo Нажмите любую клавишу для выхода...
pause >nul