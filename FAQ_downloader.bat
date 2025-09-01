@echo off
chcp 65001 > nul
title FAQ Document Downloader & Manager
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║              📚 FAQ Document Downloader & Manager            ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

:: Navigate to project root
cd /d "%~dp0"

:: Check if virtual environment exists and activate it
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat >nul 2>&1
)

:main_menu
echo 📚 Управление FAQ документами
echo.
echo Выберите действие:
echo.
echo [1] 🖱️  GUI интерфейс загрузки (рекомендуется)
echo [2] 📁 Drag & Drop интерфейс
echo [3] 💻 Командная строка (продвинутые)
echo [4] 📋 Создать шаблоны файлов
echo [5] 👀 Просмотр текущего FAQ
echo [6] 📊 Статистика FAQ
echo [7] 🔧 Обновить эмбеддинги
echo [8] 📖 Справка по форматам
echo [0] ❌ Выход
echo.

set /p choice="Введите номер действия (0-8): "

if "%choice%"=="1" goto gui_interface
if "%choice%"=="2" goto dragdrop_interface
if "%choice%"=="3" goto cmdline_help
if "%choice%"=="4" goto create_templates
if "%choice%"=="5" goto preview_faq
if "%choice%"=="6" goto faq_stats
if "%choice%"=="7" goto update_embeddings
if "%choice%"=="8" goto format_help
if "%choice%"=="0" goto exit
echo ❌ Неверный выбор! Попробуйте снова.
echo.
pause
cls
goto main_menu

:gui_interface
echo.
echo 🖱️ Запуск GUI интерфейса загрузки...
echo.
if not exist utils\faq_gui.py (
    echo ❌ Файл utils\faq_gui.py не найден!
    echo 💡 Убедитесь, что файл существует в папке utils
    pause
    goto main_menu
)

python utils\faq_gui.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Ошибка запуска GUI интерфейса
    echo 💡 Возможные причины:
    echo    • Не установлен tkinter
    echo    • Отсутствуют зависимости
    echo    • Ошибка в файле faq_gui.py
    echo.
    pause
)
goto main_menu

:dragdrop_interface
echo.
echo 📁 Запуск Drag & Drop интерфейса...
echo 💡 Просто перетащите файлы в открывшееся окно!
echo.
if not exist utils\drag_drop_loader.py (
    echo ❌ Файл utils\drag_drop_loader.py не найден!
    echo 💡 Убедитесь, что файл существует в папке utils
    pause
    goto main_menu
)

python utils\drag_drop_loader.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Ошибка запуска Drag & Drop интерфейса
    echo.
    pause
)
goto main_menu

:cmdline_help
echo.
echo 💻 Использование командной строки:
echo.
echo ═══════════════════════════════════════════════════════════════
echo 📄 Загрузка CSV файла:
echo    python utils\bulk_loader.py data.csv csv
echo.
echo 📊 Загрузка Excel файла:
echo    python utils\bulk_loader.py data.xlsx excel
echo.
echo 📁 Загрузка всех файлов из папки:
echo    python utils\bulk_loader.py "C:\My Documents" folder
echo.
echo 📝 Загрузка текстового файла:
echo    python utils\bulk_loader.py questions.txt txt
echo.
echo 🔧 Создание шаблонов:
echo    python utils\bulk_loader.py --templates
echo.
echo ═══════════════════════════════════════════════════════════════
echo.
echo 🚀 Хотите попробовать загрузить файл прямо сейчас?
set /p file_path="Введите путь к файлу (или Enter для возврата): "

if "%file_path%"=="" goto main_menu

echo.
echo 📂 Определение типа файла...
python utils\bulk_loader.py "%file_path%" auto
echo.
pause
goto main_menu

:create_templates
echo.
echo 📋 Создание шаблонов файлов...
echo.
python utils\bulk_loader.py dummy dummy --templates
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Шаблоны успешно созданы!
    echo.
    echo 📁 Расположение: templates/
    echo    • faq_template.csv - для Excel/CSV
    echo    • faq_template.xlsx - для Excel
    echo    • faq_template.txt - для текстовых файлов
    echo.
    echo 💡 Используйте эти шаблоны для подготовки ваших FAQ данных
) else (
    echo ❌ Ошибка создания шаблонов
)
echo.
pause
goto main_menu

:preview_faq
echo.
echo 👀 Просмотр текущего FAQ...
echo.
python -c "
import sys
import os
import json
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))
try:
    faq_file = 'data/faq.json'
    if os.path.exists(faq_file):
        with open(faq_file, 'r', encoding='utf-8') as f:
            faq = json.load(f)
        print(f'📚 FAQ содержит {len(faq)} записей\\n')
        for i, entry in enumerate(faq[:10], 1):
            query = entry.get('query', 'Без названия')
            print(f'{i:2d}. {query[:60]}{'...' if len(query) > 60 else ''}')
        if len(faq) > 10:
            print(f'\\n... и еще {len(faq)-10} записей')
    else:
        print('❌ Файл FAQ не найден: data/faq.json')
        print('💡 Создайте FAQ используя один из интерфейсов загрузки')
except Exception as e:
    print(f'❌ Ошибка чтения FAQ: {e}')
"
echo.
pause
goto main_menu

:faq_stats
echo.
echo 📊 Статистика FAQ...
echo.
python -c "
import sys
import os
import json
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))
try:
    faq_file = 'data/faq.json'
    if os.path.exists(faq_file):
        with open(faq_file, 'r', encoding='utf-8') as f:
            faq = json.load(f)
        
        total_entries = len(faq)
        total_queries = sum(len(entry.get('variations', [])) + 1 for entry in faq)
        avg_variations = total_queries / total_entries if total_entries > 0 else 0
        
        print(f'📊 Статистика FAQ:')
        print(f'   • Общее количество записей: {total_entries}')
        print(f'   • Общее количество вопросов: {total_queries}')
        print(f'   • Среднее количество вариантов на запись: {avg_variations:.1f}')
        
        # Categories analysis
        categories = {}
        for entry in faq:
            category = entry.get('category', 'Без категории')
            categories[category] = categories.get(category, 0) + 1
        
        if categories:
            print(f'\\n📂 Категории:')
            for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                print(f'   • {cat}: {count} записей')
    else:
        print('❌ Файл FAQ не найден: data/faq.json')
except Exception as e:
    print(f'❌ Ошибка анализа FAQ: {e}')
"
echo.
pause
goto main_menu

:update_embeddings
echo.
echo 🔧 Обновление эмбеддингов...
echo.
echo ⚠️ Это может занять некоторое время в зависимости от размера FAQ
echo.
set /p confirm="Продолжить? (y/N): "
if /I not "%confirm%"=="y" goto main_menu

echo.
echo 🗑️ Удаление старых эмбеддингов...
if exist cache\faq_embeddings.pkl del cache\faq_embeddings.pkl
if exist cache\faq_index.faiss del cache\faq_index.faiss

echo 🔄 Перестроение эмбеддингов...
python -c "
import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))
try:
    from faq_loader import FAQLoader
    from config import config
    
    loader = FAQLoader(
        faq_file=config.FAQ_FILE,
        embeddings_file=config.EMBEDDINGS_FILE,
        index_file=config.INDEX_FILE
    )
    
    print('📖 Загрузка FAQ...')
    loader.load_faq()
    
    print('🧠 Создание эмбеддингов...')
    loader.create_embeddings()
    
    print('✅ Эмбеддинги успешно обновлены!')
except Exception as e:
    print(f'❌ Ошибка обновления эмбеддингов: {e}')
"
echo.
pause
goto main_menu

:format_help
echo.
echo 📖 Справка по поддерживаемым форматам
echo.
echo ═══════════════════════════════════════════════════════════════
echo 📄 CSV файлы (.csv):
echo    • Колонки: query, answer, category (опционально)
echo    • Разделитель: запятая или точка с запятой
echo    • Кодировка: UTF-8
echo.
echo 📊 Excel файлы (.xlsx, .xls):
echo    • Первая строка - заголовки
echo    • Колонки: query, answer, category (опционально)
echo.
echo 📝 Текстовые файлы (.txt):
echo    • Формат: Вопрос^Ответ^Категория
echo    • Каждая пара на новой строке
echo    • Разделитель: символ ^
echo.
echo 📁 Папки:
echo    • Загружаются все поддерживаемые файлы из папки
echo    • Рекурсивный поиск в подпапках
echo.
echo 💡 Рекомендации:
echo    • Используйте четкие и понятные вопросы
echo    • Добавляйте варианты вопросов для лучшего поиска
echo    • Группируйте по категориям для удобства
echo ═══════════════════════════════════════════════════════════════
echo.
pause
goto main_menu

:exit
echo.
echo 👋 Спасибо за использование FAQ Downloader!
echo.
timeout /t 2 > nul
exit /b 0