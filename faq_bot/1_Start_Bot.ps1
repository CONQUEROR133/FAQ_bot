# PowerShell script to start the FAQ Bot
Write-Host "🤖 Запуск FAQ бота..."
Write-Host ""

# Change to the project directory
Set-Location -Path "$PSScriptRoot"

# Check for required files
Write-Host "🔍 Проверка необходимых файлов..."

if (-not (Test-Path "run_bot.py")) {
    Write-Host "❌ Ошибка: Файл run_bot.py не найден!"
    Write-Host "Нажмите любую клавишу для выхода..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
} else {
    Write-Host "✅ run_bot.py найден"
}

if (-not (Test-Path "src\main.py")) {
    Write-Host "❌ Ошибка: Файл src\main.py не найден!"
    Write-Host "Нажмите любую клавишу для выхода..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
} else {
    Write-Host "✅ src\main.py найден"
}

# Check for virtual environment
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "💾 Активация виртуального окружения..."
    try {
        & ./venv/Scripts/Activate.ps1
        Write-Host "✅ Виртуальное окружение активировано"
    } catch {
        Write-Host "❌ Ошибка активации виртуального окружения"
        Write-Host "Попробовать запустить без виртуального окружения? (y/n)"
        $TRY_WITHOUT_VENV = Read-Host
        if ($TRY_WITHOUT_VENV -ne "y") {
            Write-Host "Нажмите любую клавишу для выхода..."
            $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
            exit 1
        }
    }
} else {
    Write-Host "⚠️ Виртуальное окружение не найдено, используем системный Python"
}

# Check configuration
Write-Host ""
Write-Host "🔍 Проверка конфигурации..."
if (-not (Test-Path ".env")) {
    Write-Host "⚠️ Файл .env не найден"
    Write-Host "Пожалуйста, создайте .env файл или запустите 0_Setup.bat"
    Write-Host "Нажмите любую клавишу для выхода..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
} else {
    Write-Host "✅ .env файл найден"
}

if (-not (Test-Path "data\faq.json")) {
    Write-Host "⚠️ Файл data\faq.json не найден"
    Write-Host "Пожалуйста, добавьте данные в faq.json или запустите 0_Setup.bat"
    Write-Host "Нажмите любую клавишу для выхода..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
} else {
    Write-Host "✅ data\faq.json найден"
}

# Start the bot
Write-Host ""
Write-Host "▶️ Запуск бота..."
Write-Host ""
Write-Host "📋 Логи будут записываться в cache\bot.log"
Write-Host "🛑 Нажмите Ctrl+C для остановки бота"
Write-Host ""

Start-Sleep -Seconds 3

# Run the bot with error output
Write-Host "Запуск бота с выводом ошибок..."
try {
    python run_bot.py
    $EXIT_CODE = $LASTEXITCODE
} catch {
    $EXIT_CODE = 1
}

Write-Host ""
Write-Host "Код завершения: $EXIT_CODE"
if ($EXIT_CODE -ne 0) {
    Write-Host "❌ Бот остановлен с ошибкой (Error Level: $EXIT_CODE)"
    
    # Check for log files
    if (Test-Path "cache\bot.log") {
        Write-Host "📋 Последние строки лога:"
        Get-Content "cache\bot.log" -Tail 20
        Write-Host ""
        Write-Host "💾 Полный лог сохранен в cache\bot.log"
    }
} else {
    Write-Host "✅ Бот остановлен нормально"
}

Write-Host ""
Write-Host "📊 Статистика выполнения:"
Write-Host "   Время запуска: $(Get-Date)"
if ($EXIT_CODE -ne 0) {
    Write-Host "   Статус: Ошибка ($EXIT_CODE)"
} else {
    Write-Host "   Статус: Успешно"
}

Write-Host ""
Write-Host "Нажмите любую клавишу для выхода..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")