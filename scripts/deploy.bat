@echo off
chcp 65001 > nul
title FAQ Bot - Deployment Manager
echo 🚀 FAQ Bot Deployment Manager
echo ================================
echo.

:menu
echo Select deployment option:
echo 1. Development Environment Setup
echo 2. Production Environment Setup  
echo 3. Docker Deployment
echo 4. Update Bot (Git Pull + Restart)
echo 5. Backup Database and Cache
echo 6. Restore from Backup
echo 7. Health Check
echo 8. View Logs
echo 9. Exit
echo.
set /p choice="Enter your choice (1-9): "

if "%choice%"=="1" goto dev_setup
if "%choice%"=="2" goto prod_setup
if "%choice%"=="3" goto docker_deploy
if "%choice%"=="4" goto update_bot
if "%choice%"=="5" goto backup
if "%choice%"=="6" goto restore
if "%choice%"=="7" goto health_check
if "%choice%"=="8" goto view_logs
if "%choice%"=="9" goto exit
goto menu

:dev_setup
echo.
echo 🔧 Setting up Development Environment...
if not exist .env.development (
    echo ❌ .env.development not found!
    goto menu
)
copy .env.development .env
echo ✅ Development configuration activated
call scripts\setup.bat
goto menu

:prod_setup
echo.
echo 🏭 Setting up Production Environment...
if not exist .env.production (
    echo ❌ .env.production not found!
    goto menu
)
copy .env.production .env
echo ✅ Production configuration activated
call scripts\setup.bat
echo.
echo ⚠️ Remember to update BOT_TOKEN and other sensitive values in .env
goto menu

:docker_deploy
echo.
echo 🐳 Docker Deployment...
docker --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Docker not found! Please install Docker first.
    goto menu
)
echo Building Docker image...
docker build -t faq-bot .
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Docker build failed!
    goto menu
)
echo Starting containers...
docker-compose up -d
echo ✅ Bot deployed with Docker
goto menu

:update_bot
echo.
echo 📥 Updating Bot...
git --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Git not found! Manual update required.
    goto menu
)
echo Pulling latest changes...
git pull
echo Restarting bot...
call scripts\restart_bot.bat
echo ✅ Bot updated and restarted
goto menu

:backup
echo.
echo 💾 Creating Backup...
set timestamp=%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set timestamp=%timestamp: =0%
mkdir backups\%timestamp% 2>nul
copy data\*.* backups\%timestamp%\ >nul
copy cache\*.* backups\%timestamp%\ >nul
copy .env backups\%timestamp%\ >nul
echo ✅ Backup created: backups\%timestamp%
goto menu

:restore
echo.
echo 📁 Available backups:
dir backups /b
echo.
set /p backup_name="Enter backup folder name: "
if not exist backups\%backup_name% (
    echo ❌ Backup not found!
    goto menu
)
copy backups\%backup_name%\*.* data\ >nul
copy backups\%backup_name%\*.* cache\ >nul
echo ✅ Backup restored from: %backup_name%
goto menu

:health_check
echo.
echo 🏥 Health Check...
python -c "import sys; sys.path.insert(0, 'src'); from config import config; print('✅ Configuration OK')" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Configuration check failed
) else (
    echo ✅ Configuration check passed
)

if exist data\analytics.db (
    echo ✅ Database file exists
) else (
    echo ❌ Database file missing
)

if exist cache\faq_embeddings.pkl (
    echo ✅ Embeddings cache exists
) else (
    echo ❌ Embeddings cache missing
)

goto menu

:view_logs
echo.
echo 📋 Recent Logs:
if exist cache\bot.log (
    echo Last 20 lines of bot.log:
    echo ------------------------
    powershell "Get-Content cache\bot.log -Tail 20"
) else (
    echo ❌ No log file found
)
echo.
pause
goto menu

:exit
echo.
echo 👋 Goodbye!
pause >nul
exit /b 0