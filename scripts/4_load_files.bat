@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion
title FAQ File Loader

:: Переходим в родительскую директорию проекта
cd /d "%~dp0.."

REM Set console colors for better visibility
color 0A

:start
cls
echo.
echo ╔═══════════════════════════════════════════════════════════════════════════╗
echo ║                    📁 FAQ File Loader - Загрузчик файлов                  ║
echo ║                         Быстрая загрузка данных в FAQ                     ║
echo ╚═══════════════════════════════════════════════════════════════════════════╝
echo.
echo 🎯 Выберите способ загрузки файлов:
echo.
echo ┌─────────────────────────────────────────────────────────────────────────┐
echo │  [1] 🖱️  GUI Интерфейс (рекомендуется для новичков)                      │
echo │      ↳ Простой графический интерфейс с кнопками                          │
echo │                                                                           │
echo │  [2] 📁 Drag && Drop загрузчик (самый удобный)                            │
echo │      ↳ Перетащите файлы прямо в окно программы                           │
echo │                                                                           │
echo │  [3] 💻 Простой загрузчик (без зависимостей)                             │
echo │      ↳ Базовый функционал, работает везде                                │
echo │                                                                           │
echo │  [4] ⚡ Командная строка (для опытных пользователей)                     │
echo │      ↳ Прямые команды с параметрами                                      │
echo └─────────────────────────────────────────────────────────────────────────┘
echo.
echo ┌─────────────────────────────────────────────────────────────────────────┐
echo │  [5] 📋 Создать шаблоны файлов                                           │
echo │  [6] 👀 Просмотр текущего FAQ                                            │
echo │  [7] 🔧 Диагностика системы                                              │
echo │  [8] 📖 Справка и документация                                           │
echo └─────────────────────────────────────────────────────────────────────────┘
echo.
echo   [0] ❌ Выход
echo.

set /p choice="🔹 Введите номер (0-8): "

REM Validate input
if "%choice%"=="" goto invalid_choice
if "%choice%"=="1" goto gui_interface
if "%choice%"=="2" goto drag_drop
if "%choice%"=="3" goto simple_loader
if "%choice%"=="4" goto command_line
if "%choice%"=="5" goto create_templates
if "%choice%"=="6" goto preview_faq
if "%choice%"=="7" goto diagnostics
if "%choice%"=="8" goto help
if "%choice%"=="0" goto exit

:invalid_choice
echo.
echo ❌ Неверный выбор! Пожалуйста, введите число от 0 до 8.
timeout /t 3 > nul
goto start

:gui_interface
echo.
echo 🖱️ Запускаем улучшенный GUI интерфейс для загрузки файлов...
echo ┌─────────────────────────────────────────────────────────────────────────┐
echo │ 💡 Новый улучшенный интерфейс включает:                                  │
echo │    • Умное определение типа файлов                                        │
echo │    • Предварительный просмотр данных                                      │
echo │    • Пакетную обработку файлов                                            │
echo │    • Детальную валидацию и отчетность                                     │
echo │    • Современный дизайн с прогресс-барами                                 │
echo └─────────────────────────────────────────────────────────────────────────┘
echo.

if exist "venv\Scripts\activate.bat" (
    echo 🔄 Активируем виртуальное окружение...
    call venv\Scripts\activate.bat
)

REM Try enhanced GUI first
if exist "utils\enhanced_faq_gui.py" (
    echo 🚀 Запускаем улучшенный интерфейс...
    python utils\enhanced_faq_gui.py
    if errorlevel 1 (
        echo.
        echo ⚠️ Проблема с улучшенным интерфейсом, пробуем стандартный...
        goto standard_gui
    )
    goto end
)

:standard_gui
if exist "utils\faq_gui.py" (
    echo 🖱️ Запускаем стандартный GUI интерфейс...
    python utils\faq_gui.py
    if errorlevel 1 (
        echo.
        echo ❌ Ошибка запуска GUI интерфейса!
        echo 💡 Проверьте установку зависимостей: tkinter, pandas, openpyxl
        echo 🔧 Запустите setup.bat для установки зависимостей
        pause
    )
else (
    echo ❌ Ошибка: GUI интерфейсы не найдены!
    echo 💡 Убедитесь, что вы находитесь в правильной папке проекта.
    pause
)
goto end

:drag_drop
echo.
echo 📁 Запускаем Drag && Drop интерфейс...
echo ┌─────────────────────────────────────────────────────────────────────────┐
echo │ 💡 Совет: В Drag && Drop интерфейсе:                                      │
echo │    • Просто перетащите файлы в окно программы                            │
echo │    • Поддерживаются: CSV, Excel, JSON, TXT, папки                       │
echo │    • Автоматическое определение формата файла                            │
echo │    • Предварительный просмотр перед загрузкой                            │
echo └─────────────────────────────────────────────────────────────────────────┘
echo.

if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

if not exist "utils\drag_drop_loader.py" (
    echo ❌ Ошибка: utils\drag_drop_loader.py не найден!
    pause
    goto start
)

python utils\drag_drop_loader.py
if errorlevel 1 (
    echo.
    echo ❌ Ошибка запуска Drag && Drop интерфейса!
    echo 💡 Проверьте установку: tkinterdnd2, pandas
    pause
)
goto end

:simple_loader
echo.
echo 💻 Запускаем простой загрузчик (без внешних зависимостей)...
echo ┌─────────────────────────────────────────────────────────────────────────┐
echo │ 💡 Возможности простого загрузчика:                                      │
echo │    • Загрузка CSV файлов                                                  │
echo │    • Загрузка JSON файлов                                                 │
echo │    • Загрузка текстовых списков                                           │
echo │    • Автоматическая обработка папок с файлами                            │
echo │    • Создание резервных копий                                             │
echo └─────────────────────────────────────────────────────────────────────────┘
echo.

if not exist "utils\simple_bulk_loader.py" (
    echo ❌ Ошибка: utils\simple_bulk_loader.py не найден!
    pause
    goto start
)

echo 📋 Примеры использования:
echo.
echo   Загрузка CSV файла:
echo   python utils\simple_bulk_loader.py data.csv csv
echo.
echo   Загрузка JSON файла:
echo   python utils\simple_bulk_loader.py data.json json
echo.
echo   Загрузка папки:
echo   python utils\simple_bulk_loader.py "C:\My Files" folder
echo.
echo   Создание шаблонов:
echo   python utils\simple_bulk_loader.py --templates
echo.

set /p manual_cmd="💡 Хотите ввести команду вручную? (y/N): "
if /i "%manual_cmd%"=="y" (
    echo.
    set /p user_cmd="🔹 Введите команду: python utils\simple_bulk_loader.py "
    python utils\simple_bulk_loader.py !user_cmd!
) else (
    echo.
    echo 📂 Интерактивный режим будет добавлен в следующей версии.
    echo 💡 Используйте GUI интерфейс для удобной загрузки.
    pause
)
goto end

:command_line
echo.
echo ⚡ Командная строка - Продвинутый режим
echo ┌─────────────────────────────────────────────────────────────────────────┐
echo │ 🎯 Доступные команды:                                                    │
echo │                                                                           │
echo │ 📊 CSV файлы:                                                            │
echo │    python utils\bulk_loader.py data.csv csv                             │
echo │                                                                           │
echo │ 📈 Excel файлы:                                                          │
echo │    python utils\bulk_loader.py data.xlsx excel                         │
echo │                                                                           │
echo │ 📁 Папки с файлами:                                                      │
echo │    python utils\bulk_loader.py "C:\MyFiles" folder                     │
echo │                                                                           │
echo │ 🔄 JSON данные:                                                          │
echo │    python utils\bulk_loader.py data.json json                          │
echo │                                                                           │
echo │ 📝 Текстовые списки:                                                     │
echo │    python utils\bulk_loader.py list.txt txt                            │
echo └─────────────────────────────────────────────────────────────────────────┘
echo.

if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

echo 🔹 Введите команду загрузки:
set /p cmd_input="python utils\bulk_loader.py "

if "%cmd_input%"=="" (
    echo ❌ Команда не введена!
    pause
    goto start
)

echo.
echo 🚀 Выполняем: python utils\bulk_loader.py %cmd_input%
python utils\bulk_loader.py %cmd_input%
goto end

:create_templates
echo.
echo 📋 Создание шаблонов файлов...
echo.

if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

echo 🔄 Создаем шаблоны с помощью основного загрузчика...
python utils\bulk_loader.py dummy dummy --templates

if exist "templates\" (
    echo.
    echo ✅ Шаблоны успешно созданы в папке 'templates\'!
    echo.
    echo 📄 Доступные шаблоны:
    if exist "templates\faq_template.csv" echo    • CSV шаблон: templates\faq_template.csv
    if exist "templates\faq_template.xlsx" echo    • Excel шаблон: templates\faq_template.xlsx
    if exist "templates\faq_template.txt" echo    • Текстовый шаблон: templates\faq_template.txt
    if exist "templates\faq_template.json" echo    • JSON шаблон: templates\faq_template.json
    echo.
    echo 💡 Отредактируйте шаблоны и загрузите их обратно в систему.
) else (
    echo ❌ Ошибка создания шаблонов!
)
pause
goto end

:preview_faq
echo.
echo 👀 Просмотр текущего содержимого FAQ...
echo.

if exist "data\faq.json" (
    python -c "
import json
try:
    with open('data/faq.json', 'r', encoding='utf-8') as f:
        faq = json.load(f)
    print(f'📚 FAQ содержит {len(faq)} записей:')
    print('=' * 60)
    for i, entry in enumerate(faq[:15], 1):
        query = entry.get('query', 'Без названия')[:50]
        resources_count = len(entry.get('resources', []))
        print(f'{i:2}. {query}... (ресурсов: {resources_count})')
    if len(faq) > 15:
        print(f'    ... и еще {len(faq)-15} записей')
    print('=' * 60)
    print(f'📊 Общая статистика: {len(faq)} записей в базе знаний')
except Exception as e:
    print(f'❌ Ошибка чтения FAQ: {e}')
"
) else (
    echo ❌ Файл data\faq.json не найден!
    echo 💡 Возможно, база данных FAQ еще не создана.
)
echo.
pause
goto end

:diagnostics
echo.
echo 🔧 Диагностика системы загрузки файлов...
echo.

echo 📂 Проверка файлов...
if exist "utils\bulk_loader.py" (echo ✅ utils\bulk_loader.py - найден) else (echo ❌ utils\bulk_loader.py - отсутствует)
if exist "utils\simple_bulk_loader.py" (echo ✅ utils\simple_bulk_loader.py - найден) else (echo ❌ utils\simple_bulk_loader.py - отсутствует)
if exist "utils\enhanced_faq_gui.py" (echo ✅ utils\enhanced_faq_gui.py - найден (НОВЫЙ!)) else (echo ⚠️ utils\enhanced_faq_gui.py - отсутствует)
if exist "utils\faq_gui.py" (echo ✅ utils\faq_gui.py - найден) else (echo ❌ utils\faq_gui.py - отсутствует)
if exist "utils\drag_drop_loader.py" (echo ✅ utils\drag_drop_loader.py - найден) else (echo ❌ utils\drag_drop_loader.py - отсутствует)

echo.
echo 📁 Проверка папок...
if exist "templates\" (echo ✅ templates\ - найдена) else (echo ⚠️  templates\ - отсутствует ^(будет создана^))
if exist "files\" (echo ✅ files\ - найдена) else (echo ⚠️  files\ - отсутствует ^(будет создана^))
if exist "backups\" (echo ✅ backups\ - найдена) else (echo ⚠️  backups\ - отсутствует ^(будет создана^))

echo.
echo 🐍 Проверка Python и зависимостей...
python --version 2>nul
if errorlevel 1 (
    echo ❌ Python не найден или не установлен!
    echo 💡 Установите Python 3.8+ с официального сайта
) else (
    echo ✅ Python найден
)

echo.
echo 📦 Проверка ключевых модулей...
python -c "import json; print('✅ json - встроенный модуль')" 2>nul
python -c "import pandas; print('✅ pandas - установлен')" 2>nul || echo "⚠️  pandas - не установлен (нужен для Excel)"
python -c "import openpyxl; print('✅ openpyxl - установлен')" 2>nul || echo "⚠️  openpyxl - не установлен (нужен для Excel)"
python -c "import tkinter; print('✅ tkinter - доступен')" 2>nul || echo "❌ tkinter - не доступен (нужен для GUI)"

echo.
echo 💡 Для установки недостающих зависимостей запустите setup.bat
pause
goto end

:help
echo.
echo 📖 Справка - FAQ File Loader
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo 🎯 НАЗНАЧЕНИЕ:
echo    Загрузка файлов и данных в базу знаний FAQ бота.
echo    Поддержка различных форматов: CSV, Excel, JSON, TXT, папки с файлами.
echo.
echo 🚀 БЫСТРЫЙ СТАРТ:
echo    1. Выберите пункт [1] для GUI интерфейса (самый простой способ)
echo    2. Нажмите "Обзор" и выберите файл данных
echo    3. Выберите формат файла
echo    4. Нажмите "Загрузить FAQ"
echo    5. Перезапустите бота командой: 2_start_bot.bat
echo.
echo 📋 ПОДДЕРЖИВАЕМЫЕ ФОРМАТЫ:
echo    • CSV - таблицы с разделителями (Excel может сохранить в CSV)
echo    • Excel (.xlsx) - таблицы Microsoft Excel
echo    • JSON - структурированные данные в формате JSON
echo    • TXT - простые текстовые списки с разделителями
echo    • Folder - автоматическое создание FAQ из файлов в папке
echo.
echo 💡 ПОЛЕЗНЫЕ СОВЕТЫ:
echo    • Начните с создания шаблонов (пункт [5])
echo    • Используйте режим "Объединение" для добавления к существующим данным
echo    • Проверяйте результат через "Просмотр FAQ" (пункт [6])
echo    • Делайте резервные копии (создаются автоматически)
echo.
echo 🔧 УСТРАНЕНИЕ ПРОБЛЕМ:
echo    • Если GUI не запускается - проверьте установку tkinter
echo    • Если Excel не читается - установите openpyxl
echo    • Если ошибки кодировки - убедитесь, что файл в UTF-8
echo    • Запустите диагностику (пункт [7]) для проверки системы
echo.
echo 📞 ДОПОЛНИТЕЛЬНАЯ ПОМОЩЬ:
echo    • Подробная документация: readme.txt
echo    • Примеры файлов: папка templates\
echo    • Техническая поддержка: смотрите контакты в readme.txt
echo.
pause
goto end

:end
echo.
echo ✅ Операция завершена!
echo.
echo 💡 Следующие шаги:
echo    • Проверьте результат через "Просмотр FAQ"
echo    • Перезапустите бота: 2_start_bot.bat
echo    • При проблемах запустите диагностику
echo.
pause
goto start

:exit
echo.
echo 👋 Завершение работы...
echo.
echo 💡 Помните:
echo    • После загрузки новых данных перезапустите бота
echo    • Резервные копии сохраняются автоматически
echo    • При проблемах используйте диагностику
echo.
echo До свидания!
timeout /t 3 > nul
exit /b 0