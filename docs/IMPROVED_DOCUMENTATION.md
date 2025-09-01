# FAQ Bot - Comprehensive Documentation

## 📋 Table of Contents
1. [Overview](#overview)
2. [Key Features](#key-features)
3. [Technology Stack](#technology-stack)
4. [Project Architecture](#project-architecture)
5. [Installation & Setup](#installation--setup)
6. [Configuration](#configuration)
7. [Usage Guide](#usage-guide)
8. [Management Scripts](#management-scripts)
9. [Development](#development)
10. [Troubleshooting](#troubleshooting)
11. [Contributing](#contributing)

## 📖 Overview

The FAQ Bot is an intelligent Telegram bot designed to automatically answer user questions by matching them against a predefined FAQ database using semantic similarity. It leverages modern NLP techniques for accurate, context-aware responses and can automatically send files, documents, and links based on user queries.

## ✨ Key Features

### 🤖 Intelligent FAQ System
- **Semantic Search**: Uses sentence-transformers and FAISS for understanding question meaning
- **Auto-Send Logic**: Automatically sends single resources without confirmation
- **Keyboard Interface**: Shows selection UI for multiple resources
- **Variation Support**: Handles different ways of asking the same question

### 📁 Universal File Management
- **Multi-Format Support**: Handles images, documents, videos, and any file type
- **Bulk Loading**: Import FAQ data from CSV, Excel, JSON files
- **Drag & Drop Interface**: Easy file uploading
- **Template System**: Pre-built templates for FAQ data

### 🔒 Security & Authentication
- **Two-Factor Authentication**: Password protection for bot access
- **Admin Controls**: Special privileges for designated administrators
- **Content Filtering**: Blocks inappropriate content with customizable word lists

### 📊 Analytics & Monitoring
- **Usage Statistics**: Tracks question frequency and user interactions
- **Unanswered Questions**: Logs queries that didn't match FAQ entries
- **Performance Metrics**: Monitors response times and system health
- **Export Capabilities**: Detailed analytics reports

### 🛠️ Robust Operations
- **Auto-Reconnection**: Handles network interruptions gracefully
- **Health Monitoring**: Periodic connection checks and self-healing
- **Comprehensive Logging**: Detailed operational logs for debugging
- **Graceful Error Handling**: Professional error management

## 🧠 Technology Stack

- **Python 3.8+**: Core programming language
- **aiogram**: Telegram Bot API framework
- **sentence-transformers**: Semantic text understanding
- **FAISS**: Vector similarity search
- **SQLite**: Analytics database
- **C# WPF**: Advanced FAQ management GUI

## 🏗️ Project Architecture

```
faq_bot/
├── 📁 src/               # Core application code
│   ├── main.py           # Main application entry point
│   ├── config.py         # Configuration settings
│   ├── handlers.py       # Telegram bot message handlers
│   ├── faq_loader.py     # FAQ loading and search functionality
│   ├── database.py       # Database operations
│   ├── middlewares.py    # Aiogram middlewares
│   └── auth_middleware.py # Authentication middleware
│
├── 📁 tests/             # Test files
│   ├── quick_test.py     # Quick validation tests
│   ├── test_authentication.py # Authentication tests
│   └── ...
│
├── 📁 data/              # Application data
│   ├── faq.json          # FAQ knowledge base
│   └── analytics.db      # Analytics database
│
├── 📁 cache/             # Cache files (auto-generated)
│   ├── faq_embeddings.pkl  # Cached embeddings
│   ├── faq_index.faiss     # FAISS search index
│   └── bot.log             # Application logs
│
├── 📁 utils/             # Utility scripts
│   ├── bulk_loader.py    # Bulk FAQ loading utilities
│   ├── faq_gui.py        # GUI for FAQ management
│   └── diagnose_bot.py   # Bot diagnostics
│
├── 📁 scripts/           # Batch scripts
│   ├── 2_start_bot.bat   # Bot startup script
│   ├── clear_cache.bat   # Cache cleanup
│   └── setup.bat         # Project setup
│
├── 📁 docs/              # Documentation
├── 📁 files/             # Bot resource files
├── 📁 templates/         # Template files
└── 📁 backups/           # Backup files
```

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8+
- Telegram Bot Token (from @BotFather)
- Internet connection for initial model downloads

### Setup Process
1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd faq-bot
   ```

2. **Run setup**:
   ```bash
   setup.bat  # Windows
   ```

3. **Configure environment**:
   - Copy `.env.development` to `.env`
   - Add your `BOT_TOKEN` and `ADMIN_ID` to `.env`

4. **Start the bot**:
   ```bash
   start.bat  # Windows
   # or
   python run_bot.py  # Cross-platform
   ```

## ⚙️ Configuration

Key configuration options in `.env`:
- `BOT_TOKEN`: Your Telegram bot token
- `ADMIN_ID`: Your Telegram user ID for admin access
- `ACCESS_PASSWORD`: Password for user authentication
- `SIMILARITY_THRESHOLD`: Semantic search sensitivity (0.0-1.0, default: 0.7)

## 📖 Usage Guide

### Basic Operation
1. Start the bot using `start.bat` or `python run_bot.py`
2. Users can interact with the bot via Telegram
3. The bot will automatically respond to FAQ queries
4. For single resource queries, files are sent automatically
5. For multiple resource queries, a selection keyboard is displayed

### Admin Functions
- Admins can access special commands and controls
- Analytics dashboard provides usage statistics
- Content filtering can be configured

## 🛠️ Management Scripts

- **`start.bat`**: Launch the bot with environment setup
- **`Clean.bat`**: Clear cache, logs, and temporary files
- **`FAQ_downloader.bat`**: Manage FAQ entries and bulk loading
- **`setup.bat`**: Install dependencies and setup environment
- **`clear_cache.bat`**: Remove cached embeddings and indexes
- **`restart_bot.bat`**: Restart the bot with proper cleanup

## 👨‍💻 Development

### Code Structure
The bot follows a modular architecture with clear separation of concerns:
- **Message Handlers**: Process user interactions in `handlers.py`
- **FAQ Loader**: Semantic search and embedding management in `faq_loader.py`
- **Database Layer**: Analytics and authentication in `database.py`
- **Configuration**: Environment-based settings in `config.py`
- **Middlewares**: Dependency injection and authentication in `middlewares.py`

### Testing
Run tests using:
```bash
python tests/quick_test.py
python tests/test_authentication.py
```

### Adding New Features
1. Follow the existing code structure
2. Add new handlers in `handlers.py`
3. Update the FAQ database in `data/faq.json`
4. Test thoroughly before deployment

## 🆘 Troubleshooting

### Common Issues
1. **Bot not responding**: Check `cache/bot.log` for errors
2. **Authentication issues**: Verify `BOT_TOKEN` and `ADMIN_ID` in `.env`
3. **Slow responses**: First run may be slow due to model downloads
4. **Connection errors**: Check network connectivity and firewall settings

### Maintenance
- Regularly clear cache with `clear_cache.bat`
- Monitor logs in `cache/bot.log`
- Update dependencies as needed

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is proprietary and confidential.