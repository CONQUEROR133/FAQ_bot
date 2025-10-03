@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion
title FAQ Bot - Cleanup
echo 🗑️ Очистка FAQ бота...
echo.

echo ⚠️ ВНИМАНИЕ: Это удалит все кэшированные файлы и логи
echo Продолжить? (y/n)
set /p CONFIRM_CLEAN=
if /i not "%CONFIRM_CLEAN%"=="y" (
    echo ❌ Очистка отменена
    echo Нажмите любую клавишу для выхода...
    pause >nul
    exit /b 0
)

:: Очистка кэша
echo.
echo 📁 Очистка директории cache...
if exist cache (
    echo Удаление файлов кэша...
    del /f /q cache\*.* >nul 2>&1
    for /d %%i in (cache\*) do rd /s /q "%%i" >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        echo ✅ Директория cache очищена
    ) else (
        echo ⚠️ Ошибка очистки директории cache
    )
) else (
    echo ✅ Директория cache не существует
)

:: Очистка логов
echo.
echo 📋 Очистка логов...
if exist logs (
    echo Удаление файлов логов...
    del /f /q logs\*.* >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        echo ✅ Логи очищены
    ) else (
        echo ⚠️ Ошибка очистки логов
    )
) else (
    echo ✅ Директория logs не существует
)

:: Очистка Python кэша
echo.
echo 🐍 Очистка Python кэша...
for /d /r %%i in (__pycache__) do (
    if exist "%%i" (
        rd /s /q "%%i" >nul 2>&1
    )
)

for /d /r %%i in (*.pyc) do (
    if exist "%%i" (
        del /f /q "%%i" >nul 2>&1
    )
)

echo ✅ Python кэш очищен

:: Очистка временных файлов
echo.
echo 📄 Очистка временных файлов...
del /f /q *.log >nul 2>&1
del /f /q *.tmp >nul 2>&1
del /f /q *.bak >nul 2>&1
echo ✅ Временные файлы очищены

echo.
echo 🎉 Очистка завершена!
echo.
echo Нажмите любую клавишу для выхода...
pause >nul
endlocal