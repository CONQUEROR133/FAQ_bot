@echo off
chcp 65001 > nul
title FAQ Bulk Loader
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                🚀 FAQ Bulk Loader - Быстрая загрузка файлов   ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

:: Переходим в родительскую директорию проекта
cd /d "%~dp0.."

:start
echo Выберите способ загрузки:
echo.
echo [1] 🖱️  GUI интерфейс (простой)
echo [2] 📁 Drag & Drop (перетаскивание)
echo [3] 💻 Командная строка
echo [4] 📋 Создать шаблоны
echo [5] 👀 Просмотр FAQ
echo [0] ❌ Выход
echo.

set /p choice="Введите номер (0-5): "

if "%choice%"=="1" goto gui
if "%choice%"=="2" goto dragdrop
if "%choice%"=="3" goto cmdline
if "%choice%"=="4" goto templates
if "%choice%"=="5" goto preview
if "%choice%"=="0" goto exit
echo Неверный выбор!
pause
goto start

:gui
echo.
echo 🖱️ Запускаем GUI интерфейс...
echo 📁 Папка: utils\faq_gui.py
python utils\faq_gui.py
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Ошибка запуска GUI. Проверьте зависимости.
    echo Нажмите любую клавишу для возврата...
    pause >nul
    goto start
)
goto end

:dragdrop
echo.
echo 📁 Запускаем Drag & Drop интерфейс...
echo 📁 Папка: utils\drag_drop_loader.py
python utils\drag_drop_loader.py
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Ошибка запуска Drag & Drop. Проверьте зависимости.
    echo Нажмите любую клавишу для возврата...
    pause >nul
    goto start
)
goto end

:cmdline
echo.
echo 💻 Примеры использования командной строки:
echo.
echo Загрузка CSV:
echo   python utils\bulk_loader.py data.csv csv
echo.
echo Загрузка Excel:
echo   python utils\bulk_loader.py data.xlsx excel
echo.
echo Загрузка папки:
echo   python utils\bulk_loader.py "C:\My Files" folder
echo.
echo Создание шаблонов:
echo   python utils\bulk_loader.py --templates
echo.
pause
goto start

:templates
echo.
echo 📋 Создаем шаблоны...
python utils\bulk_loader.py dummy dummy --templates
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Шаблоны созданы в папке 'templates/'
    echo    - faq_template.csv
    echo    - faq_template.xlsx
    echo    - faq_template.txt
) else (
    echo ❌ Ошибка создания шаблонов
)
echo.
pause
goto start

:preview
echo.
echo 👀 Просмотр текущего FAQ...
python -c "
import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'utils'))
from bulk_loader import BulkFAQLoader
loader = BulkFAQLoader()
faq = loader.load_existing_faq()
print(f'📚 FAQ содержит {len(faq)} записей')
for i, entry in enumerate(faq[:10], 1):
    print(f'{i}. {entry.get(\"query\", \"Без названия\")}')
if len(faq) > 10:
    print(f'... и еще {len(faq)-10} записей')
"
echo.
pause
goto start

:end
echo.
echo ✅ Операция завершена!
pause

:exit
echo.
echo 👋 До свидания!
timeout /t 2 > nul