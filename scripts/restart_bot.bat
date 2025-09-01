@echo off
chcp 65001 > nul
title FAQ Bot - Restart
echo 🔄 Перезапуск FAQ бота...
echo.

echo 🛑 Остановка процессов бота...
:: Останавливаем все Python процессы с main.py
taskkill /f /im python.exe /fi "WINDOWTITLE eq FAQ Bot - Running" >nul 2>&1

:: Ждем немного для корректного завершения
timeout /t 3 /nobreak >nul

echo 📋 Запуск диагностики...
python diagnose_bot.py

echo.
echo 🚀 Перезапуск бота...
echo Нажмите любую клавишу для продолжения или Ctrl+C для отмены...
pause >nul

:: Запускаем бота снова
call start_bot.bat