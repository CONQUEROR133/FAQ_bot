@echo off
title FAQ Bot - Cleanup...

echo ================================
echo   FAQ Bot - Cleanup Utility
echo ================================
echo.

REM Ask for confirmation
echo This will remove:
echo  - Cache files
echo  - Log files
echo  - Temporary files
echo  - Statistics data
echo.
set /p confirm=Continue? (y/N): 

if /i not "%confirm%"=="y" (
    echo Cleanup cancelled
    pause
    exit /b
)

echo.
echo 🗑️ Cleaning up...

REM Clean cache directory
if exist "cache" (
    echo Removing cache files...
    del /q "cache\*" >nul 2>&1
    for /d %%i in ("cache\*") do rmdir /s /q "%%i" >nul 2>&1
    echo ✅ Cache cleaned
) else (
    echo ⚠️ Cache directory not found
)

REM Clean logs directory
if exist "logs" (
    echo Removing log files...
    del /q "logs\*" >nul 2>&1
    for /d %%i in ("logs\*") do rmdir /s /q "%%i" >nul 2>&1
    echo ✅ Logs cleaned
) else (
    echo ⚠️ Logs directory not found
)

REM Clear statistics data from database
if exist "data\analytics.db" (
    echo Clearing statistics data...
    python clear_stats.py
    if %errorlevel% equ 0 (
        echo ✅ Statistics data cleared
    ) else (
        echo ❌ Failed to clear statistics data
    )
) else (
    echo ⚠️ Statistics database not found
)

REM Run the Python cleanup script
if exist "cleanup.py" (
    echo Running Python cleanup script...
    python cleanup.py
    echo ✅ Python cleanup completed
) else (
    echo ⚠️ Python cleanup script not found
)

echo.
echo 🎉 Cleanup completed!
echo.
pause