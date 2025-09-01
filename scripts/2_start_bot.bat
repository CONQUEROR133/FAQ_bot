@echo off
chcp 65001 > nul
title FAQ Bot - Running
echo 🤖 Запуск FAQ бота...
echo.

:: Переходим в родительскую директорию проекта
cd /d "%~dp0.."

:: Проверка наличия виртуального окружения
if exist venv\Scripts\activate.bat (
    echo 💾 Активация виртуального окружения...
    call venv\Scripts\activate.bat
) else (
    echo ⚠️ Виртуальное окружение не найдено, используем системный Python
)

:: Проверка наличия run_bot.py
if not exist run_bot.py (
    echo ❌ Ошибка: Файл run_bot.py не найден!
    echo Нажмите любую клавишу для выхода...
    pause >nul
    exit /b 1
)

echo ▶️ Запуск бота...
echo.
python run_bot.py

echo.
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Бот остановлен с ошибкой (Error Level: %ERRORLEVEL%)
) else (
    echo ✅ Бот остановлен нормально
)
echo Нажмите любую клавишу для выхода...
pause >nul