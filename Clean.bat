@echo off
chcp 65001 > nul
title FAQ Bot - System Cleanup
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                 🧹 FAQ Bot - System Cleanup                  ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo 🧹 Выполняется полная очистка системы...
echo.

:: Navigate to project root
cd /d "%~dp0"

echo ▶️ Очистка кэша и временных файлов...
echo.

:: Clean embeddings and index files from cache/
if exist cache\faq_embeddings.pkl (
    del cache\faq_embeddings.pkl
    echo ✅ Удален cache\faq_embeddings.pkl
)

if exist cache\faq_index.faiss (
    del cache\faq_index.faiss
    echo ✅ Удален cache\faq_index.faiss
)

:: Clean legacy files from root directory
if exist faq_embeddings.pkl (
    del faq_embeddings.pkl
    echo ✅ Удален faq_embeddings.pkl
)

if exist faq_index.faiss (
    del faq_index.faiss
    echo ✅ Удален faq_index.faiss
)

:: Clean Python cache
if exist __pycache__ (
    rd /s /q __pycache__
    echo ✅ Удален __pycache__
)

if exist src\__pycache__ (
    rd /s /q src\__pycache__
    echo ✅ Удален src\__pycache__
)

:: Clean temporary databases
if exist temp_test.db (
    del temp_test.db
    echo ✅ Удален temp_test.db
)

if exist temp_validation.db (
    del temp_validation.db
    echo ✅ Удален temp_validation.db
)

if exist test_analytics.db (
    del test_analytics.db
    echo ✅ Удален test_analytics.db
)

:: Clean log files
if exist bot.log (
    del bot.log
    echo ✅ Удален bot.log
)

if exist cache\bot.log (
    del cache\bot.log
    echo ✅ Удален cache\bot.log
)

if exist logs\bot.log (
    del logs\bot.log
    echo ✅ Удален logs\bot.log
)

:: Clean test result files
if exist test_results.txt (
    del test_results.txt
    echo ✅ Удален test_results.txt
)

if exist validation_report.txt (
    del validation_report.txt
    echo ✅ Удален validation_report.txt
)

:: Clean development documentation files
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

:: Clean test files
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

echo.
echo ▶️ Сброс базы данных аналитики...

:: Reset analytics database
if exist data\analytics.db (
    del data\analytics.db
    echo ✅ База данных аналитики сброшена
)

echo.
echo 🎉 Полная очистка завершена!
echo.
echo 📋 Очищено:
echo    • Кэш эмбеддингов и индексов
echo    • Временные файлы и логи
echo    • Кэш Python
echo    • База данных аналитики
echo    • Файлы разработки и тестирования
echo.
echo 💡 Теперь можно запустить бота командой: Start.bat
echo.
echo Нажмите любую клавишу для выхода...
pause >nul