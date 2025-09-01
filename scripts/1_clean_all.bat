@echo off
chcp 65001 > nul
title FAQ Bot - Complete Development Cleanup
echo 🧹 Полная очистка разработки...
echo.

:: Очистка кэша через существующий скрипт
echo ▶️ Очистка основного кэша...
call clear_cache.bat

echo.
echo ▶️ Удаление файлов разработки и тестирования...

:: Удаление документации разработки
if exist COMPREHENSIVE_TEST_REPORT.md (
    del COMPREHENSIVE_TEST_REPORT.md
    echo ✅ Удален COMPREHENSIVE_TEST_REPORT.md
)

if exist ERROR_ANALYSIS_REPORT.md (
    del ERROR_ANALYSIS_REPORT.md
    echo ✅ Удален ERROR_ANALYSIS_REPORT.md
)

if exist IMPLEMENTATION_SUMMARY.md (
    del IMPLEMENTATION_SUMMARY.md
    echo ✅ Удален IMPLEMENTATION_SUMMARY.md
)

:: Удаление тестовых файлов
if exist test_bot.py (
    del test_bot.py
    echo ✅ Удален test_bot.py
)

if exist test_new_structure.py (
    del test_new_structure.py
    echo ✅ Удален test_new_structure.py
)

if exist demo_functionality.py (
    del demo_functionality.py
    echo ✅ Удален demo_functionality.py
)

if exist final_demo.py (
    del final_demo.py
    echo ✅ Удален final_demo.py
)

:: Сброс аналитики
echo.
echo ▶️ Сброс аналитики...
call reset_db.bat

echo.
echo 🎉 Полная очистка завершена!
echo Проект готов к чистому запуску
echo Нажмите любую клавишу для выхода...
pause >nul