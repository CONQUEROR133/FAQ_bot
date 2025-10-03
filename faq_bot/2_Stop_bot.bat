@echo off
chcp 65001 > nul
title FAQ Bot - Stop
echo 🛑 Остановка FAQ бота...
echo.

echo 🔍 Поиск запущенных процессов бота...

:: Проверяем запущенные Python процессы
tasklist /fi "imagename eq python.exe" /fo csv 2>nul | findstr /i "main.py" >nul
if %ERRORLEVEL% EQU 0 (
    echo ⚠️ Найдены запущенные процессы бота
    echo Остановка процессов...
    taskkill /f /im python.exe /fi "WINDOWTITLE eq FAQ Bot*"
    if %ERRORLEVEL% EQU 0 (
        echo ✅ Процессы бота остановлены
    ) else (
        echo ⚠️ Не удалось остановить все процессы
    )
) else (
    echo ✅ Нет запущенных процессов бота
)

:: Также проверяем PowerShell процессы
tasklist /fi "imagename eq powershell.exe" /fo csv 2>nul | findstr /i "run_bot.py" >nul
if %ERRORLEVEL% EQU 0 (
    echo ⚠️ Найдены запущенные PowerShell процессы бота
    echo Остановка процессов...
    taskkill /f /im powershell.exe /fi "WINDOWTITLE eq FAQ Bot*"
    if %ERRORLEVEL% EQU 0 (
        echo ✅ PowerShell процессы бота остановлены
    ) else (
        echo ⚠️ Не удалось остановить все PowerShell процессы
    )
)

echo.
echo 🧹 Очистка временных файлов...
if exist cache\bot.log.lock (
    del /f /q cache\bot.log.lock >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo ✅ Временные файлы очищены
    ) else (
        echo ⚠️ Не удалось очистить временные файлы
    )
) else (
    echo ✅ Нет временных файлов для очистки
)

echo.
echo 🎉 Остановка завершена!
echo.
echo Нажмите любую клавишу для выхода...
pause >nul
