@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion
title FAQ Bot - Stopping
echo 🛑 Остановка FAQ бота...
echo.

:: Проверка наличия активных процессов бота
echo 🔍 Поиск активных процессов бота...

:: Поиск процессов по заголовку окна
for /f "tokens=2 delims=," %%i in ('tasklist /v /fo csv ^| findstr /i "FAQ Bot - Running"') do (
    set BOT_PROCESS_FOUND=1
    echo ✅ Найден процесс бота: %%i
)

if not defined BOT_PROCESS_FOUND (
    :: Поиск процессов Python, если поиск по заголовку не дал результатов
    for /f "tokens=2 delims=," %%i in ('tasklist /v /fo csv ^| findstr /i python ^| findstr /i "run_bot.py"') do (
        set PYTHON_PROCESS_FOUND=1
        echo ✅ Найден Python процесс бота: %%i
    )
)

if not defined BOT_PROCESS_FOUND if not defined PYTHON_PROCESS_FOUND (
    echo ⚠️ Активные процессы бота не найдены
    echo Нажмите любую клавишу для выхода...
    pause >nul
    exit /b 0
)

:: Останавливаем все Python процессы с FAQ Bot - Running
echo 🛑 Остановка процессов бота...
set PROCESS_KILLED=0

:: Остановка по заголовку окна
if defined BOT_PROCESS_FOUND (
    taskkill /f /im python.exe /fi "WINDOWTITLE eq FAQ Bot - Running" >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        set PROCESS_KILLED=1
        echo ✅ Процессы остановлены по заголовку окна
    )
)

:: Остановка по имени процесса, если предыдущий способ не сработал
if not defined PROCESS_KILLED (
    if defined PYTHON_PROCESS_FOUND (
        taskkill /f /im python.exe /fi "WINDOWTITLE eq run_bot.py" >nul 2>&1
        if !ERRORLEVEL! EQU 0 (
            set PROCESS_KILLED=1
            echo ✅ Процессы остановлены по имени файла
        )
    )
)

:: Принудительная остановка всех Python процессов (как крайняя мера)
if not defined PROCESS_KILLED (
    echo ⚠️ Использование принудительной остановки всех Python процессов...
    echo    Это может повлиять на другие Python приложения!
    echo    Продолжить? (y/n)
    set /p FORCE_KILL=
    if /i "!FORCE_KILL!"=="y" (
        taskkill /f /im python.exe >nul 2>&1
        if !ERRORLEVEL! EQU 0 (
            echo ✅ Все Python процессы остановлены
        ) else (
            echo ⚠️ Не удалось остановить процессы
        )
    ) else (
        echo ⚠️ Остановка отменена пользователем
    )
)

:: Ждем немного для корректного завершения
echo 🕐 Ожидание завершения процессов...
timeout /t 3 /nobreak >nul

echo ✅ Бот остановлен
echo.
echo 📊 Статистика остановки:
echo    Время остановки: %date% %time%
if defined BOT_PROCESS_FOUND (
    echo    Способ остановки: По заголовку окна
)
if defined PYTHON_PROCESS_FOUND (
    echo    Способ остановки: По имени процесса
)
if not defined BOT_PROCESS_FOUND if not defined PYTHON_PROCESS_FOUND (
    echo    Способ остановки: Принудительный
)

echo.
echo Нажмите любую клавишу для выхода...
pause >nul
endlocal