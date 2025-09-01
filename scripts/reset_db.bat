@echo off
chcp 65001 > nul
title FAQ Bot - Resetting Analytics
echo 📋 Сброс базы аналитики...
echo.

:: Удаление основной базы аналитики
if exist analytics.db (
    del analytics.db
    echo ✅ Основная база аналитики удалена
) else (
    echo ⚠️ Основная база аналитики не найдена
)

echo.
echo 🎉 Аналитика сброшена! Запустите start_bot.bat для запуска бота.
echo Нажмите любую клавишу для выхода...
pause >nul