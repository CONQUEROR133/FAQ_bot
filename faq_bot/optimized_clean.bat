@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion
title Telegram FAQ Bot - Cleanup
echo ====================================================
echo           Telegram FAQ Bot - Cleanup
echo ====================================================
echo.

:: Check if running from the correct directory
if not exist "cache" if not exist "logs" (
    echo ⚠️  Warning: Not running from project root directory
    echo    Current directory: %CD%
    echo.
)

echo ⚠️  WARNING: This will remove cache files and logs
echo.
echo Files to be removed:
echo  - Cache files ^(cache/*^)
echo  - Log files ^(logs/*^)
echo  - Python cache files ^(__pycache__, *.pyc^)
echo.
echo Configuration files and data will NOT be removed:
echo  - .env configuration
echo  - data/faq.json
echo  - files/ directory
echo.
echo Continue with cleanup? (y/N)
set /p CONFIRM_CLEAN=
if /i not "%CONFIRM_CLEAN%"=="y" (
    echo ❌ Cleanup cancelled
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 0
)

:: Cleanup cache directory
echo.
echo 🗑️  Cleaning cache directory...
if exist "cache" (
    echo Removing cache files...
    del /f /q cache\*.* >nul 2>&1
    for /d %%i in (cache\*) do rd /s /q "%%i" >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        echo ✅ Cache directory cleaned
    ) else (
        echo ⚠️  Some cache files could not be removed
    )
) else (
    echo ⚠️  Cache directory not found
)

:: Cleanup logs directory
echo.
echo 🗑️  Cleaning logs directory...
if exist "logs" (
    echo Removing log files...
    del /f /q logs\*.* >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        echo ✅ Logs directory cleaned
    ) else (
        echo ⚠️  Some log files could not be removed
    )
) else (
    echo ⚠️  Logs directory not found
)

:: Cleanup Python cache files
echo.
echo 🗑️  Cleaning Python cache files...
set PYCACHE_COUNT=0
for /d /r %%i in (__pycache__) do (
    if exist "%%i" (
        rd /s /q "%%i" >nul 2>&1
        if !ERRORLEVEL! EQU 0 (
            set /a PYCACHE_COUNT+=1
        )
    )
)

set PYC_COUNT=0
for /r %%i in (*.pyc) do (
    if exist "%%i" (
        del /f /q "%%i" >nul 2>&1
        if !ERRORLEVEL! EQU 0 (
            set /a PYC_COUNT+=1
        )
    )
)

echo ✅ Removed !PYCACHE_COUNT! __pycache__ directories
echo ✅ Removed !PYC_COUNT! .pyc files

:: Cleanup temporary files
echo.
echo 🗑️  Cleaning temporary files...
set TEMP_COUNT=0
for %%i in (*.log *.tmp *.bak) do (
    if exist "%%i" (
        del /f /q "%%i" >nul 2>&1
        if !ERRORLEVEL! EQU 0 (
            set /a TEMP_COUNT+=1
        )
    )
)
echo ✅ Removed !TEMP_COUNT! temporary files

echo.
echo ====================================================
echo           Cleanup Completed Successfully!
echo ====================================================
echo.
echo ✅ Cache cleared
echo ✅ Logs cleared
echo ✅ Python cache cleared
echo ✅ Temporary files removed
echo.
echo Press any key to exit...
pause >nul
endlocal