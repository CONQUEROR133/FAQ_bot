@echo off
chcp 65001 > nul
title FAQ Bot - Running
echo 🤖 Запуск FAQ бота...
echo.

:: Переходим в родительскую директорию проекта
cd /d "%~dp0"

:: Проверка наличия необходимых файлов
echo 🔍 Проверка необходимых файлов...

if not exist run_bot.py (
    echo ❌ Ошибка: Файл run_bot.py не найден!
    echo Нажмите любую клавишу для выхода...
    timeout /t 5 /nobreak >nul
    exit /b 1
)
echo ✅ run_bot.py найден

if not exist src\main.py (
    echo ❌ Ошибка: Файл src\main.py не найден!
    echo Нажмите любую клавишу для выхода...
    timeout /t 5 /nobreak >nul
    exit /b 1
)
echo ✅ src\main.py найден

if not exist .env (
    echo ⚠️ Файл .env не найден
    echo Пожалуйста, создайте .env файл или запустите 0_Setup.bat
    echo Нажмите любую клавишу для выхода...
    timeout /t 5 /nobreak >nul
    exit /b 1
)
echo ✅ .env файл найден

if not exist data\faq.json (
    echo ⚠️ Файл data\faq.json не найден
    echo Пожалуйста, добавьте данные в faq.json или запустите 0_Setup.bat
    echo Нажмите любую клавишу для выхода...
    timeout /t 5 /nobreak >nul
    exit /b 1
)
echo ✅ data\faq.json найден

:: Активация виртуального окружения если оно существует
if exist venv\Scripts\activate.bat (
    echo 💾 Активация виртуального окружения...
    call venv\Scripts\activate.bat
    echo ✅ Виртуальное окружение активировано
)

:: Запуск бота
echo.
echo ▶️ Запуск бота...
echo.
echo 📋 Логи будут записываться в cache\bot.log
echo 🛑 Нажмите Ctrl+C для остановки бота
echo.

timeout /t 3 /nobreak >nul

echo Запуск бота...
python run_bot.py
set EXIT_CODE=%ERRORLEVEL%

echo.
if "%EXIT_CODE%"=="0" (
    echo ✅ Бот остановлен нормально
) else (
    echo ❌ Бот остановлен с ошибкой (Error Level: %EXIT_CODE%)
    
    :: Проверка наличия логов
    if exist cache\bot.log (
        echo 📋 Последние строки лога:
        powershell -Command "Get-Content cache\bot.log -Tail 20"
        echo.
        echo 💾 Полный лог сохранен в cache\bot.log
    )
)

echo.
echo 📊 Статистика выполнения:
echo    Время запуска: %date% %time%

if "%EXIT_CODE%"=="0" (
    echo    Статус: Успешно
) else (
    echo    Статус: Ошибка (%EXIT_CODE%)
)

echo.
echo Нажмите любую клавишу для выхода...
timeout /t 15 /nobreak >nul