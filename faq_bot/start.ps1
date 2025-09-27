# Simple PowerShell script to start the FAQ Bot
Write-Host "Starting FAQ Bot..."
Set-Location -Path "$PSScriptRoot"

# Check if required files exist
if (-not (Test-Path "run_bot.py")) {
    Write-Host "Error: run_bot.py not found!"
    exit 1
}

if (-not (Test-Path "src\main.py")) {
    Write-Host "Error: src\main.py not found!"
    exit 1
}

if (-not (Test-Path ".env")) {
    Write-Host "Error: .env file not found!"
    exit 1
}

if (-not (Test-Path "data\faq.json")) {
    Write-Host "Error: data\faq.json not found!"
    exit 1
}

Write-Host "All required files found"

# Activate virtual environment if it exists
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..."
    & ./venv/Scripts/Activate.ps1
}

Write-Host "Starting bot..."
Write-Host "Logs will be written to cache\bot.log"
Write-Host "Press Ctrl+C to stop the bot"

# Run the bot
python run_bot.py