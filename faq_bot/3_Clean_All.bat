@echo off
chcp 65001 > nul
title FAQ Bot - Complete Cleanup
echo 🧹 Полная очистка...
echo.

:: Переходим в родительскую директорию проекта
cd /d "%~dp0"

:: Удаление файлов эмбеддингов и индексов из cache/
echo 🧹 Удаление кэша...
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
echo 🧹 Удаление Python кэша...
for /d %%i in (*__pycache__*) do (
    rd /s /q "%%i"
    echo ✅ Удален %%i
)

:: Удаление логов
echo 🧹 Удаление логов...
if exist cache\bot.log (
    del cache\bot.log
    echo ✅ Удален cache\bot.log
)

if exist bot.log (
    del bot.log
    echo ✅ Удален bot.log
)

echo.
echo 🎉 Полная очистка завершена!
echo Проект готов к чистому запуску
echo Нажмите любую клавишу для выхода...
pause >nul