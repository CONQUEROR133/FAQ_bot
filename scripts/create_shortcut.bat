@echo off
REM Создание ярлыка на рабочем столе для загрузчика файлов FAQ

echo.
echo 🔗 Создание ярлыка для загрузчика файлов FAQ...
echo.

REM Получаем путь к рабочему столу
for /f "usebackq tokens=3*" %%i in (`reg query "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders" /v Desktop`) do set DESKTOP=%%i %%j

REM Получаем текущую директорию проекта
set PROJECT_DIR=%~dp0

REM Создаем VBS скрипт для создания ярлыка
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%TEMP%\CreateShortcut.vbs"
echo sLinkFile = "%DESKTOP%\FAQ File Loader.lnk" >> "%TEMP%\CreateShortcut.vbs"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%TEMP%\CreateShortcut.vbs"
echo oLink.TargetPath = "%PROJECT_DIR%4_load_files.bat" >> "%TEMP%\CreateShortcut.vbs"
echo oLink.WorkingDirectory = "%PROJECT_DIR%" >> "%TEMP%\CreateShortcut.vbs"
echo oLink.Description = "FAQ File Loader - Загрузчик файлов в базу знаний FAQ бота" >> "%TEMP%\CreateShortcut.vbs"
echo oLink.IconLocation = "shell32.dll,165" >> "%TEMP%\CreateShortcut.vbs"
echo oLink.Save >> "%TEMP%\CreateShortcut.vbs"

REM Выполняем VBS скрипт
cscript //nologo "%TEMP%\CreateShortcut.vbs"

REM Удаляем временный файл
del "%TEMP%\CreateShortcut.vbs" 2>nul

if exist "%DESKTOP%\FAQ File Loader.lnk" (
    echo ✅ Ярлык успешно создан на рабочем столе!
    echo.
    echo 📂 Путь: %DESKTOP%\FAQ File Loader.lnk
    echo 🎯 Описание: FAQ File Loader - Загрузчик файлов в базу знаний FAQ бота
    echo.
    echo 💡 Теперь вы можете запускать загрузчик файлов прямо с рабочего стола!
    echo    Просто дважды щелкните по ярлыку "FAQ File Loader"
) else (
    echo ❌ Ошибка создания ярлыка!
    echo 💡 Попробуйте запустить от имени администратора
)

echo.
pause