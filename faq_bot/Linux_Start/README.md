# Linux_Start

This directory contains scripts to run the FAQ Bot on Ubuntu VPS with the following specifications:
- Processor: Intel Xeon 2 GHz (1 core)
- RAM: 512 MB
- Storage: 10 GB HDD
- OS: Ubuntu

## Scripts

1. [0_Setup.sh](file://d:\Games\faq_bot\Linux_Start\0_Setup.sh) - Sets up the environment
2. [1_Train_Model.sh](file://d:\Games\faq_bot\Linux_Start\1_Train_Model.sh) - Trains the model with VPS-optimized settings
3. [2_Start_Bot.sh](file://d:\Games\faq_bot\Linux_Start\2_Start_Bot.sh) - Starts the bot
4. [3_Stop_Bot.sh](file://d:\Games\faq_bot\Linux_Start\3_Stop_Bot.sh) - Stops the bot
5. [4_Clean_All.sh](file://d:\Games\faq_bot\Linux_Start\4_Clean_All.sh) - Cleans cache files while preserving model files
6. [5_Check_Status.sh](file://d:\Games\faq_bot\Linux_Start\5_Check_Status.sh) - Checks the status of the bot and system
7. [convert_to_unix.sh](file://d:\Games\faq_bot\Linux_Start\convert_to_unix.sh) - Utility script to convert line endings to Unix format

## Documentation

- [VPS_DEPLOYMENT_GUIDE_RU.md](file://d:\Games\faq_bot\Linux_Start\VPS_DEPLOYMENT_GUIDE_RU.md) - Подробное руководство по запуску проекта на VPS (на русском языке)
- [PROJECT_ANALYSIS_RU.md](file://d:\Games\faq_bot\Linux_Start\PROJECT_ANALYSIS_RU.md) - Анализ проекта на русском языке

## Usage

1. Make scripts executable:
   ```bash
   chmod +x *.sh
   ```

2. Run setup:
   ```bash
   ./0_Setup.sh
   ```

3. Train the model (optional, if FAQ data has changed):
   ```bash
   ./1_Train_Model.sh
   ```

4. Start the bot:
   ```bash
   ./2_Start_Bot.sh
   ```

## Optimization Notes

- Batch size reduced to 8 (from 16) to accommodate limited RAM
- Cache sizes reduced to 100/200 to minimize memory usage
- Model files are preserved during cleanup to avoid retraining
- Scripts are designed to work with limited system resources

## Note for Windows Users

If you're preparing these scripts on Windows, make sure to convert line endings to Unix format (LF) before uploading to your Linux VPS. You can use the [convert_to_unix.sh](file://d:\Games\faq_bot\Linux_Start\convert_to_unix.sh) script or tools like `dos2unix` or text editors like VS Code or Notepad++ to convert line endings.