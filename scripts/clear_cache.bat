@echo off
chcp 65001 > nul
title FAQ Bot - Clearing Cache
echo 🧹 Очистка кэша бота...
echo.

:: Переходим в родительскую директорию проекта
cd /d "%~dp0.."

:: Удаление файлов эмбеддингов и индексов из cache/
if exist cache\faq_embeddings.pkl (
    del cache\faq_embeddings.pkl
    echo ✅ Удален cache\faq_embeddings.pkl
)

if exist cache\faq_index.faiss (
    del cache\faq_index.faiss
    echo ✅ Удален cache\faq_index.faiss
)

:: Удаление файлов из корневой директории (старая структура)
if exist faq_embeddings.pkl (
    del faq_embeddings.pkl
    echo ✅ Удален faq_embeddings.pkl
)

if exist faq_index.faiss (
    del faq_index.faiss
    echo ✅ Удален faq_index.faiss
)

:: Удаление Python кэша
if exist __pycache__ (
    rd /s /q __pycache__
    echo ✅ Удален __pycache__
)

:: Удаление временных баз данных
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

:: Удаление логов
if exist bot.log (
    del bot.log
    echo ✅ Удален bot.log
)

if exist logs\bot.log (
    del logs\bot.log
    echo ✅ Удален logs\bot.log
)

:: Удаление файлов результатов тестов
if exist test_results.txt (
    del test_results.txt
    echo ✅ Удален test_results.txt
)

if exist validation_report.txt (
    del validation_report.txt
    echo ✅ Удален validation_report.txt
)

echo.
echo 🎉 Кэш успешно очищен! Запустите start_bot.bat для запуска бота.
echo Нажмите любую клавишу для выхода...
pause >nul