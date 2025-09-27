@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion
title FAQ Bot - Status Check
echo 🔍 Проверка статуса FAQ бота...
echo.

cd /d "%~dp0"

echo 📊 Системная информация:
echo    Дата и время: %date% %time%
echo    Текущая директория: %cd%
echo.

:: Проверка наличия необходимых файлов
echo 🔍 Проверка файлов проекта...
set FILES_CHECKED=0
set FILES_FOUND=0

for %%f in (run_bot.py src\main.py data\faq.json .env) do (
    set /a FILES_CHECKED+=1
    if exist %%f (
        echo ✅ %%f найден
        set /a FILES_FOUND+=1
    ) else (
        echo ❌ %%f не найден
    )
)

echo    Проверено файлов: !FILES_CHECKED!
echo    Найдено файлов: !FILES_FOUND!
echo.

:: Проверка виртуального окружения
echo 🔍 Проверка виртуального окружения...
if exist venv (
    echo ✅ Виртуальное окружение найдено
    if exist venv\Scripts\activate.bat (
        echo ✅ Скрипт активации найден
    ) else (
        echo ❌ Скрипт активации не найден
    )
) else (
    echo ⚠️ Виртуальное окружение не найдено
)

echo.

:: Проверка установленных пакетов
echo 🔍 Проверка установленных пакетов...
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat >nul 2>&1
)

:: Проверка Python
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Python не найден
) else (
    for /f "tokens=* usebackq" %%i in (`python --version`) do set PYTHON_VERSION=%%i
    echo ✅ !PYTHON_VERSION!
)

:: Проверка ключевых пакетов
set PACKAGES_CHECKED=0
set PACKAGES_FOUND=0

for %%p in (aiogram sentence-transformers faiss-cpu psutil) do (
    set /a PACKAGES_CHECKED+=1
    python -c "import %%p" >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        echo ✅ %%p установлен
        set /a PACKAGES_FOUND+=1
    ) else (
        echo ❌ %%p не установлен
    )
)

echo    Проверено пакетов: !PACKAGES_CHECKED!
echo    Установлено пакетов: !PACKAGES_FOUND!
echo.

:: Проверка запущенных процессов
echo 🔍 Проверка запущенных процессов...
set BOT_RUNNING=0

:: Поиск по заголовку окна
for /f "tokens=*" %%i in ('tasklist /v /fo csv ^| findstr /i "FAQ Bot - Running" 2^>nul') do (
    set BOT_RUNNING=1
    echo ✅ Бот запущен ^(по заголовку окна^)
)

:: Поиск по имени процесса
if !BOT_RUNNING! EQU 0 (
    for /f "tokens=*" %%i in ('tasklist /v /fo csv ^| findstr /i python ^| findstr /i "run_bot.py" 2^>nul') do (
        set BOT_RUNNING=1
        echo ✅ Бот запущен ^(по имени процесса^)
    )
)

if !BOT_RUNNING! EQU 0 (
    echo ⚠️ Бот не запущен
)

echo.

:: Проверка файлов данных
echo 🔍 Проверка файлов данных...
if exist data\faq.json (
    for %%A in (data\faq.json) do (
        set FAQ_SIZE=%%~zA
    )
    echo ✅ faq.json: !FAQ_SIZE! байт
) else (
    echo ❌ faq.json не найден
)

if exist cache\faq_embeddings.pkl (
    for %%A in (cache\faq_embeddings.pkl) do (
        set EMBEDDINGS_SIZE=%%~zA
    )
    echo ✅ faq_embeddings.pkl: !EMBEDDINGS_SIZE! байт
) else (
    echo ⚠️ faq_embeddings.pkl не найден ^(может быть создан при первом запуске^)
)

if exist cache\faq_index.faiss (
    for %%A in (cache\faq_index.faiss) do (
        set INDEX_SIZE=%%~zA
    )
    echo ✅ faq_index.faiss: !INDEX_SIZE! байт
) else (
    echo ⚠️ faq_index.faiss не найден ^(может быть создан при первом запуске^)
)

if exist cache\bot.log (
    for %%A in (cache\bot.log) do (
        set LOG_SIZE=%%~zA
    )
    echo ✅ bot.log: !LOG_SIZE! байт
) else (
    echo ⚠️ bot.log не найден ^(будет создан при запуске бота^)
)

echo.

:: Проверка конфигурации
echo 🔍 Проверка конфигурации...
if exist .env (
    echo ✅ .env файл найден
    :: Проверка наличия ключевых переменных
    findstr /i "BOT_TOKEN" .env >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        echo ✅ BOT_TOKEN найден в .env
    ) else (
        echo ⚠️ BOT_TOKEN не найден в .env
    )
    
    findstr /i "ADMIN_ID" .env >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        echo ✅ ADMIN_ID найден в .env
    ) else (
        echo ⚠️ ADMIN_ID не найден в .env
    )
    
    findstr /i "ACCESS_PASSWORD" .env >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        echo ✅ ACCESS_PASSWORD найден в .env
    ) else (
        echo ⚠️ ACCESS_PASSWORD не найден в .env
    )
) else (
    echo ❌ .env файл не найден
)

echo.

:: Рекомендации
echo 📋 Рекомендации:
if !FILES_FOUND! LSS !FILES_CHECKED! (
    echo ⚠️  Некоторые необходимые файлы отсутствуют. Запустите 0_Setup.bat
)

if !PACKAGES_FOUND! LSS !PACKAGES_CHECKED! (
    echo ⚠️  Некоторые пакеты не установлены. Запустите 0_Setup.bat
)

if !BOT_RUNNING! EQU 0 (
    echo 💡  Для запуска бота используйте 1_Start_Bot.bat
) else (
    echo 💡  Для остановки бота используйте 2_Stop_bot.bat
)

echo.
echo 📊 Сводка проверки:
echo    Статус файлов: !FILES_FOUND!/!FILES_CHECKED!
echo    Статус пакетов: !PACKAGES_FOUND!/!PACKAGES_CHECKED!
if !BOT_RUNNING! EQU 1 (
    echo    Статус бота: Запущен
) else (
    echo    Статус бота: Остановлен
)

echo.
echo 🎉 Проверка завершена!
echo Нажмите любую клавишу для выхода...
pause >nul
endlocal