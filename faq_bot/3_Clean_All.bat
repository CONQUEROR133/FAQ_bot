@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion
title FAQ Bot - Complete Cleanup
echo 🧹 Полная очистка...
echo.

:: Переходим в родительскую директорию проекта
cd /d "%~dp0"

:: Подтверждение очистки
echo ⚠️ ВНИМАНИЕ: Будут удалены все кэшированные данные и логи
echo Продолжить? (y/n)
set /p CONFIRM_CLEAN=
if /i not "!CONFIRM_CLEAN!"=="y" (
    echo ❌ Очистка отменена
    echo Нажмите любую клавишу для выхода...
    pause >nul
    exit /b 0
)

echo.
echo 🧹 Начало очистки...
set FILES_DELETED=0

:: Удаление файлов эмбеддингов и индексов из cache/
echo 🧹 Удаление кэша ML модели...
if exist cache\faq_embeddings.pkl (
    del cache\faq_embeddings.pkl
    if !ERRORLEVEL! EQU 0 (
        echo ✅ Удален cache\faq_embeddings.pkl
        set /a FILES_DELETED+=1
    ) else (
        echo ❌ Ошибка удаления cache\faq_embeddings.pkl
    )
)

if exist cache\faq_index.faiss (
    del cache\faq_index.faiss
    if !ERRORLEVEL! EQU 0 (
        echo ✅ Удален cache\faq_index.faiss
        set /a FILES_DELETED+=1
    ) else (
        echo ❌ Ошибка удаления cache\faq_index.faiss
    )
)

:: Удаление файлов из корневой директории (старая структура)
echo 🧹 Удаление устаревших файлов...
if exist faq_embeddings.pkl (
    del faq_embeddings.pkl
    if !ERRORLEVEL! EQU 0 (
        echo ✅ Удален faq_embeddings.pkl
        set /a FILES_DELETED+=1
    ) else (
        echo ❌ Ошибка удаления faq_embeddings.pkl
    )
)

if exist faq_index.faiss (
    del faq_index.faiss
    if !ERRORLEVEL! EQU 0 (
        echo ✅ Удален faq_index.faiss
        set /a FILES_DELETED+=1
    ) else (
        echo ❌ Ошибка удаления faq_index.faiss
    )
)

:: Удаление Python кэша
echo 🧹 Удаление Python кэша...
set PYCACHE_DELETED=0
for /d %%i in (*__pycache__*) do (
    rd /s /q "%%i" >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        echo ✅ Удален %%i
        set /a PYCACHE_DELETED+=1
    ) else (
        echo ❌ Ошибка удаления %%i
    )
)

if !PYCACHE_DELETED! GTR 0 (
    echo ✅ Удалено !PYCACHE_DELETED! каталогов __pycache__
    set /a FILES_DELETED+=!PYCACHE_DELETED!
) else (
    echo ⚠️ Каталоги __pycache__ не найдены
)

:: Удаление логов
echo 🧹 Удаление логов...
if exist cache\bot.log (
    del cache\bot.log
    if !ERRORLEVEL! EQU 0 (
        echo ✅ Удален cache\bot.log
        set /a FILES_DELETED+=1
    ) else (
        echo ❌ Ошибка удаления cache\bot.log
    )
)

if exist bot.log (
    del bot.log
    if !ERRORLEVEL! EQU 0 (
        echo ✅ Удален bot.log
        set /a FILES_DELETED+=1
    ) else (
        echo ❌ Ошибка удаления bot.log
    )
)

:: Удаление других временных файлов
echo 🧹 Удаление временных файлов...
if exist cache\*.tmp (
    del cache\*.tmp >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        echo ✅ Удалены временные файлы из cache\
    )
)

:: Удаление файлов резервных копий
echo 🧹 Удаление резервных копий...
if exist backups\*.bak (
    del backups\*.bak >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        echo ✅ Удалены резервные копии из backups\
    )
)

if exist backups\*.backup (
    del backups\*.backup >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        echo ✅ Удалены резервные копии из backups\
    )
)

:: Удаление трассировочных файлов
echo 🧹 Удаление трассировочных файлов...
if exist *.log (
    del *.log >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        echo ✅ Удалены лог-файлы из корневой директории
    )
)

if exist cache\*.log (
    del cache\*.log >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        echo ✅ Удалены лог-файлы из cache\
    )
)

:: Удаление файлов профилирования
echo 🧹 Удаление файлов профилирования...
if exist *.prof (
    del *.prof >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        echo ✅ Удалены файлы профилирования
    )
)

if exist cache\*.prof (
    del cache\*.prof >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        echo ✅ Удалены файлы профилирования из cache\
    )
)

:: Запуск Python скрипта очистки
echo 🧹 Запуск расширенной очистки...
if exist cleanup.py (
    python cleanup.py
    if !ERRORLEVEL! EQU 0 (
        echo ✅ Расширенная очистка завершена
    ) else (
        echo ⚠️ Ошибка при расширенной очистке
    )
) else (
    echo ⚠️ Скрипт расширенной очистки не найден
)

echo.
echo 📊 Статистика очистки:
echo    Удалено файлов и каталогов: !FILES_DELETED!
echo    Время очистки: %date% %time%

echo.
echo 🎉 Полная очистка завершена!
echo.
echo 📋 Рекомендации после очистки:
echo 1. Запустите 0_Setup.bat для переустановки зависимостей (опционально)
echo 2. Запустите 1_Start_Bot.bat для запуска бота

echo.
echo Нажмите любую клавишу для выхода...
pause >nul
endlocal