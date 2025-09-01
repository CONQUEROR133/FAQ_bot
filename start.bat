@echo off
chcp 65001 > nul
title FAQ Bot - Starting
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                    🤖 FAQ Bot - Launcher                     ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

:: Navigate to project root
cd /d "%~dp0"

echo 🔄 Подготовка к запуску...
echo.

:: Check if virtual environment exists
if exist venv\Scripts\activate.bat (
    echo 💾 Активация виртуального окружения...
    call venv\Scripts\activate.bat
    if %ERRORLEVEL% NEQ 0 (
        echo ⚠️ Не удалось активировать виртуальное окружение
        echo 💡 Попробуйте запустить: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
        echo.
    ) else (
        echo ✅ Виртуальное окружение активировано
    )
) else (
    echo ⚠️ Виртуальное окружение не найдено, используем системный Python
    echo 💡 Рекомендуется запустить setup.bat для создания виртуального окружения
)

echo.

:: Check if main bot file exists
if not exist run_bot.py (
    echo ❌ Ошибка: Файл run_bot.py не найден!
    echo 💡 Убедитесь, что вы находитесь в корневой папке проекта
    echo.
    echo Нажмите любую клавишу для выхода...
    pause >nul
    exit /b 1
)

:: Check Python availability
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Python не найден в системе!
    echo 💡 Установите Python 3.8+ и добавьте его в PATH
    echo.
    echo Нажмите любую клавишу для выхода...
    pause >nul
    exit /b 1
)

echo 🐍 Python версия:
python --version

:: Check if .env file exists
if not exist .env (
    echo ⚠️ Файл .env не найден!
    if exist .env.development (
        echo 💡 Найден .env.development, копируем как .env...
        copy .env.development .env >nul
        echo ✅ Файл .env создан из .env.development
    ) else (
        echo ❌ Не найден файл конфигурации!
        echo 💡 Создайте файл .env с настройками бота
        echo.
        pause
        exit /b 1
    )
)

echo.
echo ▶️ Запуск FAQ бота...
echo 📁 Рабочая директория: %CD%
echo.
echo ═══════════════════════════════════════════════════════════════
echo.

:: Start the bot
python run_bot.py

echo.
echo ═══════════════════════════════════════════════════════════════
echo.

:: Check exit status
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Бот остановлен с ошибкой (Exit Code: %ERRORLEVEL%)
    echo.
    echo 💡 Возможные решения:
    echo    1. Проверьте .env файл с настройками
    echo    2. Убедитесь, что все зависимости установлены
    echo    3. Запустите Clean.bat для очистки кэша
    echo    4. Проверьте интернет-соединение
    echo    5. Убедитесь, что BOT_TOKEN корректный
) else (
    echo ✅ Бот остановлен корректно
)

echo.
echo 🔄 Опции после остановки:
echo    [1] Перезапустить бота
echo    [2] Очистить кэш и перезапустить  
echo    [3] Открыть FAQ загрузчик
echo    [4] Выйти
echo.

set /p restart_choice="Выберите опцию (1-4): "

if "%restart_choice%"=="1" (
    echo.
    echo 🔄 Перезапуск...
    timeout /t 2 > nul
    goto start_bot
)

if "%restart_choice%"=="2" (
    echo.
    echo 🧹 Очистка кэша...
    call Clean.bat
    echo.
    echo 🔄 Перезапуск после очистки...
    timeout /t 3 > nul
    goto start_bot
)

if "%restart_choice%"=="3" (
    echo.
    echo 📚 Открытие FAQ загрузчика...
    call FAQ_downloader.bat
    goto end
)

:end
echo.
echo 👋 До свидания!
timeout /t 2 > nul
exit /b 0

:start_bot
:: Jump back to start the bot again
python run_bot.py
goto end