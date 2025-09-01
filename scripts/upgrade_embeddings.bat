@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

REM Set console colors
color 0B

:start
cls
echo.
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                    🚀 Embedding Model Upgrade Utility                        ║
echo ║                      Улучшение модели семантического поиска                  ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.
echo 📊 Текущая модель: paraphrase-MiniLM-L6-v2 (устаревшая)
echo.
echo 🎯 Выберите новую модель для улучшения качества поиска:
echo.
echo ┌──────────────────────────────────────────────────────────────────────────────┐
echo │  [1] 🏆 BGE-M3 (РЕКОМЕНДУЕТСЯ)                                                │
echo │      ↳ Лучшая мультиязычная модель, отличная поддержка русского             │
echo │      ↳ Размер: ~2.3GB, Качество: 9/10, Скорость: 7/10                      │
echo │                                                                                │
echo │  [2] ⚡ Jina Embeddings v3                                                     │
echo │      ↳ Быстрая и качественная, специально для поиска                        │
echo │      ↳ Размер: ~1.2GB, Качество: 8.5/10, Скорость: 8/10                    │
echo │                                                                                │
echo │  [3] 🇷🇺 ru-en-RoSBERTa                                                        │
echo │      ↳ Оптимизирована для русского языка                                     │
echo │      ↳ Размер: ~500MB, Качество: 8.5/10, Скорость: 8/10                     │
echo │                                                                                │
echo │  [4] 🧠 E5-mistral-7b-instruct (Требует GPU)                                 │
echo │      ↳ Мощная модель на базе LLM, лучшее качество                           │
echo │      ↳ Размер: ~7GB, Качество: 9/10, Скорость: 5/10                         │
echo └──────────────────────────────────────────────────────────────────────────────┘
echo.
echo ┌──────────────────────────────────────────────────────────────────────────────┐
echo │  [5] 📊 Показать подробное сравнение моделей                                  │
echo │  [6] 🔧 Создать резервную копию текущих настроек                             │
echo │  [7] ↩️  Откатиться к предыдущей модели                                       │
echo │  [8] 📖 Справка по выбору модели                                              │
echo └──────────────────────────────────────────────────────────────────────────────┘
echo.
echo   [0] ❌ Выход без изменений
echo.

set /p choice="🔹 Введите номер (0-8): "

if "%choice%"=="" goto invalid_choice
if "%choice%"=="1" goto bge_m3
if "%choice%"=="2" goto jina_v3
if "%choice%"=="3" goto ru_rosbert
if "%choice%"=="4" goto e5_mistral
if "%choice%"=="5" goto show_comparison
if "%choice%"=="6" goto create_backup
if "%choice%"=="7" goto rollback
if "%choice%"=="8" goto help
if "%choice%"=="0" goto exit

:invalid_choice
echo.
echo ❌ Неверный выбор! Пожалуйста, введите число от 0 до 8.
timeout /t 3 > nul
goto start

:bge_m3
echo.
echo 🏆 Установка BGE-M3 - лучшей мультиязычной модели...
echo.
echo ℹ️  BGE-M3 Information:
echo    • Размер модели: ~2.3GB (будет загружена при первом запуске)
echo    • Поддержка языков: 100+ включая русский
echo    • Размерность эмбеддингов: 1024
echo    • Ожидаемое улучшение: 25-40%% для русских запросов
echo.

set /p confirm="❓ Продолжить установку BGE-M3? (y/N): "
if /i not "%confirm%"=="y" goto start

call :create_backup_silent
call :update_model "BAAI/bge-m3" "0.75"
echo ✅ BGE-M3 установлена! Перезапустите бота для применения изменений.
goto end

:jina_v3
echo.
echo ⚡ Установка Jina Embeddings v3...
echo.
echo ℹ️  Jina v3 Information:
echo    • Размер модели: ~1.2GB
echo    • Поддержка языков: 89 включая русский
echo    • Оптимизирована для поисковых задач
echo    • Хороший баланс скорости и качества
echo.

set /p confirm="❓ Продолжить установку Jina v3? (y/N): "
if /i not "%confirm%"=="y" goto start

call :create_backup_silent
call :update_model "jinaai/jina-embeddings-v3" "0.72"
echo ✅ Jina Embeddings v3 установлена! Перезапустите бота.
goto end

:ru_rosbert
echo.
echo 🇷🇺 Установка ru-en-RoSBERTa (русскоязычная модель)...
echo.
echo ℹ️  ru-en-RoSBERTa Information:
echo    • Размер модели: ~500MB
echo    • Специализация: русский и английский языки
echo    • Оптимизирована для российского контента
echo    • Быстрая работа на CPU
echo.

set /p confirm="❓ Продолжить установку ru-en-RoSBERTa? (y/N): "
if /i not "%confirm%"=="y" goto start

call :create_backup_silent
call :update_model "grib0ed0v/ru-en-RoSBERTa" "0.73"
echo ✅ ru-en-RoSBERTa установлена! Перезапустите бота.
goto end

:e5_mistral
echo.
echo 🧠 Установка E5-mistral-7b-instruct (требует GPU)...
echo.
echo ⚠️  ВНИМАНИЕ: Эта модель требует:
echo    • GPU с минимум 8GB VRAM ИЛИ 16GB+ RAM
echo    • Размер модели: ~7GB
echo    • Значительно медленнее на CPU
echo.
echo ℹ️  E5-Mistral Information:
echo    • Лучшее качество понимания запросов
echo    • Основана на Mistral-7B LLM
echo    • Поддержка сложных инструкций
echo.

set /p confirm="❓ У вас есть подходящее оборудование? Продолжить? (y/N): "
if /i not "%confirm%"=="y" goto start

call :create_backup_silent
call :update_model "intfloat/e5-mistral-7b-instruct" "0.76"
echo ✅ E5-mistral установлена! ТРЕБУЕТСЯ GPU для оптимальной работы.
goto end

:show_comparison
echo.
echo 📊 Подробное сравнение моделей эмбеддингов:
echo.
echo ┌─────────────────────────────────────────────────────────────────────────────┐
echo │ Модель                    │ Рус. │ Скор. │ Память │ Размер │ Общая оценка │
echo ├─────────────────────────────────────────────────────────────────────────────┤
echo │ paraphrase-MiniLM-L6-v2   │ 6/10 │ 10/10 │ 10/10  │ 23MB   │ 6.5/10      │
echo │ (текущая)                 │      │       │        │        │ УСТАРЕЛА    │
echo ├─────────────────────────────────────────────────────────────────────────────┤
echo │ BGE-M3 🏆                 │ 9/10 │  7/10 │  6/10  │ 2.3GB  │ 9/10        │
echo │ (рекомендуется)           │      │       │        │        │ ЛУЧШИЙ      │
echo ├─────────────────────────────────────────────────────────────────────────────┤
echo │ Jina Embeddings v3        │ 8/10 │  8/10 │  7/10  │ 1.2GB  │ 8.5/10      │
echo ├─────────────────────────────────────────────────────────────────────────────┤
echo │ ru-en-RoSBERTa           │10/10 │  8/10 │  8/10  │ 500MB  │ 8.5/10      │
echo │ (для русского)            │      │       │        │        │ РУС СПЕЦ    │
echo ├─────────────────────────────────────────────────────────────────────────────┤
echo │ E5-mistral-7b-instruct    │ 9/10 │  5/10 │  4/10  │ 7GB    │ 8/10        │
echo │ (требует GPU)             │      │       │        │        │ GPU ONLY    │
echo └─────────────────────────────────────────────────────────────────────────────┘
echo.
echo 💡 Рекомендация: BGE-M3 для большинства случаев использования
echo.
pause
goto start

:create_backup
echo.
echo 🔧 Создание резервной копии текущих настроек...
call :create_backup_silent
echo ✅ Резервная копия создана в папке backups\
pause
goto start

:rollback
echo.
echo ↩️  Откат к предыдущей модели...
echo.

if not exist "backups\config_backup.py" (
    echo ❌ Резервная копия не найдена!
    echo 💡 Сначала создайте резервную копию через пункт [6]
    pause
    goto start
)

echo 📂 Найдены резервные копии:
dir /b backups\config_backup*.py 2>nul

set /p confirm="❓ Восстановить из резервной копии? (y/N): "
if /i not "%confirm%"=="y" goto start

copy "backups\config_backup.py" "config.py" >nul
if exist "backups\faq_embeddings_backup.pkl" copy "backups\faq_embeddings_backup.pkl" "faq_embeddings.pkl" >nul
if exist "backups\faq_index_backup.faiss" copy "backups\faq_index_backup.faiss" "faq_index.faiss" >nul

echo ✅ Восстановление завершено! Перезапустите бота.
goto end

:help
echo.
echo 📖 Справка по выбору модели эмбеддингов:
echo.
echo 🎯 КАК ВЫБРАТЬ МОДЕЛЬ:
echo.
echo 1️⃣  Если в основном русские запросы → ru-en-RoSBERTa
echo 2️⃣  Если нужен баланс качества/скорости → Jina Embeddings v3
echo 3️⃣  Если нужно максимальное качество → BGE-M3
echo 4️⃣  Если есть мощный GPU → E5-mistral-7b-instruct
echo.
echo 🔍 КРИТЕРИИ ВЫБОРА:
echo    • Язык контента (русский/английский/многоязычный)
echo    • Доступные ресурсы (RAM/GPU)
echo    • Требования к скорости отклика
echo    • Сложность запросов пользователей
echo.
echo 📈 ОЖИДАЕМЫЕ УЛУЧШЕНИЯ:
echo    • BGE-M3: 25-40%% лучше для русских FAQ
echo    • Jina v3: 20-30%% общее улучшение
echo    • ru-RoSBERTa: 30-50%% для русского контента
echo    • E5-mistral: 35-45%% при наличии GPU
echo.
echo 🚨 ВАЖНО:
echo    • После смены модели нужно очистить кэш (clear_cache.bat)
echo    • Перезапустить бота (2_start_bot.bat)
echo    • Первый запуск может быть медленным (загрузка модели)
echo.
pause
goto start

:create_backup_silent
if not exist "backups\" mkdir backups
set backup_time=%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set backup_time=%backup_time: =0%
copy "config.py" "backups\config_backup_%backup_time%.py" >nul 2>&1
if exist "faq_embeddings.pkl" copy "faq_embeddings.pkl" "backups\faq_embeddings_backup_%backup_time%.pkl" >nul 2>&1
if exist "faq_index.faiss" copy "faq_index.faiss" "backups\faq_index_backup_%backup_time%.faiss" >nul 2>&1
exit /b

:update_model
echo.
echo 🔄 Обновление конфигурации модели...
echo.

REM Create new config.py with updated model
(
echo import os
echo from dotenv import load_dotenv
echo.
echo load_dotenv(^)
echo.
echo class Config:
echo     BOT_TOKEN = os.getenv("BOT_TOKEN"^)
echo     ADMIN_ID = int(os.getenv("ADMIN_ID", 0^)^)
echo     DB_PATH = "analytics.db"
echo     FAQ_FILE = "faq.json"
echo     EMBEDDINGS_FILE = "faq_embeddings.pkl"
echo     INDEX_FILE = "faq_index.faiss"
echo     SIMILARITY_THRESHOLD = %~2
echo     MODEL_NAME = "%~1"
echo     
echo     # Настройки сети и стабильности
echo     REQUEST_TIMEOUT = 30  # секунд
echo     CONNECT_TIMEOUT = 30  # секунд
echo     READ_TIMEOUT = 30     # секунд
echo     
echo     # Настройки повторных попыток
echo     MAX_RETRIES = 3       # максимальное количество повторов
echo     RETRY_DELAY = 1       # задержка между повторами (секунд^)
echo     
echo     # Аутентификация
echo     ACCESS_PASSWORD = os.getenv("ACCESS_PASSWORD", "1337"^)  # Moved to env
echo     
echo     BLOCKED_WORDS = [
echo         "хуй", "пизда", "ебан", "гандон", "пидор", "бля",
echo         "сука", "мудак", "долбоеб", "уебан", "залупа"
echo     ]
echo.
echo config = Config(^)
) > config.py

echo ✅ Модель обновлена: %~1
echo ✅ Порог сходства: %~2
echo.
echo 🧹 Очистка старых эмбеддингов...
if exist "faq_embeddings.pkl" del "faq_embeddings.pkl" 2>nul
if exist "faq_index.faiss" del "faq_index.faiss" 2>nul
echo ✅ Кэш очищен.
echo.
exit /b

:end
echo.
echo ✅ Операция завершена!
echo.
echo 📋 Следующие шаги:
echo    1. Перезапустите бота: 2_start_bot.bat
echo    2. При первом запуске новая модель будет загружена
echo    3. Протестируйте качество поиска с русскими запросами
echo    4. При необходимости настройте порог сходства
echo.
echo 💡 Полезные команды:
echo    • clear_cache.bat - если нужна принудительная очистка
echo    • diagnose_bot.py - для диагностики проблем
echo.
pause
goto start

:exit
echo.
echo 👋 Выход без изменений...
echo.
echo 💡 Помните: 
echo    Текущая модель paraphrase-MiniLM-L6-v2 устарела.
echo    Рекомендуется обновление для лучшего качества поиска.
echo.
timeout /t 3 > nul
exit /b 0