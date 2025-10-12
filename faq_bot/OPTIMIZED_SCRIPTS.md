# 🛠 Optimized Scripts

This project includes optimized batch scripts for easier setup, execution, and maintenance of the Telegram FAQ Bot on Windows systems.

## 📋 Available Scripts

### `optimized_setup.bat`
- **Purpose**: Complete setup of the bot environment
- **Features**:
  - Checks Python installation and version compatibility
  - Creates and activates virtual environment
  - Installs all dependencies from requirements.txt
  - Creates required directories (data, cache, files, logs)
  - Generates template configuration files (.env, faq.json)
  - Provides clear error messages and user guidance

### `optimized_start_bot.bat`
- **Purpose**: Start the Telegram FAQ Bot
- **Features**:
  - Verifies all required files are present
  - Activates virtual environment if available
  - Checks that required Python packages are installed
  - Starts the bot with clear status messages
  - Displays log excerpts on error

### `optimized_clean.bat`
- **Purpose**: Clean cache, logs, and temporary files
- **Features**:
  - Confirmation prompt to prevent accidental deletion
  - Removes cache files, log files, and Python cache files
  - Preserves configuration and data files
  - Shows detailed cleanup statistics

### `optimized_train_model.bat`
- **Purpose**: Train the semantic search model
- **Features**:
  - Verifies FAQ data is present and not empty
  - Checks that required packages are installed
  - Creates cache directory if needed
  - Confirmation prompt before training
  - Shows training results and file sizes

## 🚀 Quick Start with Optimized Scripts

1. **Setup the environment**:
   ```cmd
   optimized_setup.bat
   ```
   Then edit the generated `.env` file with your configuration.

2. **Train the model**:
   ```cmd
   optimized_train_model.bat
   ```

3. **Start the bot**:
   ```cmd
   optimized_start_bot.bat
   ```

4. **Clean up** (when needed):
   ```cmd
   optimized_clean.bat
   ```

## 🛡 Error Handling

All optimized scripts include comprehensive error handling:
- Clear error messages with actionable advice
- File and directory existence checks
- Python and package version verification
- Graceful handling of missing dependencies
- User confirmation for destructive operations

## 🌐 Language

All optimized scripts use English for consistent user experience across different systems and user locales.