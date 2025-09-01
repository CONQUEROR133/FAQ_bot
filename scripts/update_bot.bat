@echo off
chcp 65001 > nul
title FAQ Bot - Full Update
echo 🔄 Полное обновление бота...
echo.

echo ▶️ Очистка кэша...
call clear_cache.bat

echo.
echo ▶️ Сброс аналитики...
call reset_db.bat

echo.
echo 🎉 Бот полностью обновлен!
echo Используйте start_bot.bat для запуска
echo Нажмите любую клавишу для выхода...
pause >nul