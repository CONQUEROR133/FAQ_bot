@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion
title FAQ Bot - Model Training
echo 🧠 Обучение ML модели...
echo.

cd /d "%~dp0"

:: Проверка наличия виртуального окружения
if exist venv\Scripts\activate.bat (
    echo 💾 Активация виртуального окружения...
    call venv\Scripts\activate.bat
    if !ERRORLEVEL! NEQ 0 (
        echo ❌ Ошибка активации виртуального окружения
        echo Нажмите любую клавишу для выхода...
        pause >nul
        exit /b 1
    )
    echo ✅ Виртуальное окружение активировано
) else (
    echo ⚠️ Виртуальное окружение не найдено, используем системный Python
)

:: Проверка наличия необходимых пакетов
echo 🔍 Проверка установленных пакетов...
python -c "import sentence_transformers" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ⚠️ sentence-transformers не установлен
    echo Пожалуйста, запустите 0_Setup.bat для установки зависимостей
    echo Нажмите любую клавишу для выхода...
    pause >nul
    exit /b 1
) else (
    echo ✅ sentence-transformers установлен
)

:: Проверка наличия данных для обучения
echo 🔍 Проверка данных для обучения...
if not exist data\faq.json (
    echo ⚠️ Файл data\faq.json не найден
    echo Пожалуйста, добавьте данные в faq.json
    echo Нажмите любую клавишу для выхода...
    pause >nul
    exit /b 1
) else (
    echo ✅ data\faq.json найден
)

:: Проверка наличия скрипта обучения
if exist src\train_model.py (
    set TRAIN_SCRIPT=src\train_model.py
    echo ✅ Найден скрипт обучения: !TRAIN_SCRIPT!
) else if exist train_model.py (
    set TRAIN_SCRIPT=train_model.py
    echo ✅ Найден скрипт обучения: !TRAIN_SCRIPT!
) else (
    echo ⚠️ Скрипт обучения не найден
    echo Создание базового скрипта обучения...
    
    (
        echo #!/usr/bin/env python3
        echo """Basic model training script for FAQ Bot"""
        echo.
        echo import sys
        echo import os
        echo sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
        echo.
        echo from faq_loader import FAQLoader
        echo from config import config
        echo.
        echo def main^(^):
        echo     print^("🚀 Начало обучения модели..."^)
        echo     try:
        echo         # Initialize FAQ loader
        echo         faq_loader = FAQLoader^(^)
        echo.
        echo         # Load FAQ data
        echo         print^("📥 Загрузка FAQ данных..."^)
        echo         stats = faq_loader.load_faq^(^)
        echo         print^(f"✅ Загружено {stats.valid_queries} записей"^)
        echo.
        echo         # Create embeddings ^(rebuild^)
        echo         print^("🧠 Создание эмбеддингов..."^)
        echo         faq_loader.create_embeddings^(force_rebuild=True^)
        echo         print^("✅ Эмбеддинги созданы и сохранены"^)
        echo.
        echo         print^("🎉 Обучение модели завершено успешно!"^)
        echo         return 0
        echo     except Exception as e:
        echo         print^(f"❌ Ошибка обучения модели: {e}"^)
        echo         return 1
        echo.
        echo if __name__ == "__main__":
        echo     sys.exit^(main^(^)^)
    ) > train_model.py
    
    set TRAIN_SCRIPT=train_model.py
    echo ✅ Базовый скрипт обучения создан
)

:: Подтверждение обучения
echo.
echo ⚠️ ВНИМАНИЕ: Будет выполнено переобучение модели
echo Это может занять несколько минут в зависимости от объема данных
echo Продолжить? (y/n)
set /p CONFIRM_TRAIN=
if /i not "%CONFIRM_TRAIN%"=="y" (
    echo ❌ Обучение отменено
    echo Нажмите любую клавишу для выхода...
    pause >nul
    exit /b 0
)

:: Создание директории cache если не существует
if not exist cache (
    echo 📁 Создание директории cache...
    mkdir cache
    echo ✅ Директория cache создана
)

:: Запуск обучения
echo.
echo ▶️ Начало обучения модели...
echo 📋 Логи будут отображаться ниже:
echo.

python %TRAIN_SCRIPT%

set EXIT_CODE=%ERRORLEVEL%
echo.
if %EXIT_CODE% NEQ 0 (
    echo ❌ Обучение модели остановлено с ошибкой (!EXIT_CODE!)
) else (
    echo ✅ Обучение модели завершено успешно
)

echo.
echo 📊 Статистика обучения:
echo    Время завершения: %date% %time%
if %EXIT_CODE% NEQ 0 (
    echo    Статус: Ошибка (!EXIT_CODE!)
) else (
    echo    Статус: Успешно
)

echo.
echo Нажмите любую клавишу для выхода...
pause >nul
endlocal