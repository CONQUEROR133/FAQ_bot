@echo off
chcp 65001 > nul
title FAQ Bot - Stopping
echo 🛑 Остановка FAQ бота...
echo.

:: Останавливаем все Python процессы с FAQ Bot - Running
echo 🛑 Остановка процессов бота...
taskkill /f /im python.exe /fi "WINDOWTITLE eq FAQ Bot - Running" >nul 2>&1

:: Ждем немного для корректного завершения
timeout /t 3 /nobreak >nul

echo ✅ Бот остановлен
echo Нажмите любую клавишу для выхода...
pause >nul