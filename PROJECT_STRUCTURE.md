# Project Structure - FAQ Bot

## 📁 Organized Directory Structure

The project has been reorganized for better maintainability and performance:

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
│   ├── test_*.py         # All other test files
│   └── ...
│
├── 📁 data/              # Application data
│   ├── faq.json          # FAQ knowledge base
│   ├── analytics.db      # Analytics database
│   └── ...
│
├── 📁 cache/             # Cache files (auto-generated)
│   ├── faq_embeddings.pkl  # Cached embeddings
│   ├── faq_index.faiss     # FAISS search index
│   ├── bot.log             # Application logs
│   └── ...
│
├── 📁 utils/             # Utility scripts
│   ├── bulk_loader.py    # Bulk FAQ loading utilities
│   ├── faq_gui.py        # GUI for FAQ management
│   ├── diagnose_bot.py   # Bot diagnostics
│   └── ...
│
├── 📁 scripts/           # Batch scripts
│   ├── 2_start_bot.bat   # Bot startup script
│   ├── clear_cache.bat   # Cache cleanup
│   ├── setup.bat         # Project setup
│   └── ...
│
├── 📁 docs/              # Documentation
│   ├── readme.txt        # Main documentation
│   ├── *.md files        # Technical documentation
│   └── ...
│
├── 📁 files/             # Bot resource files
├── 📁 templates/         # Template files
├── 📁 backups/           # Backup files
├── 📁 venv/              # Python virtual environment
│
├── run_bot.py            # Main launcher script
├── .env                  # Environment variables
├── requirements.txt      # Python dependencies
└── .gitignore            # Git ignore rules
```

## 🚀 Quick Start

### Running the Bot
```bash
python run_bot.py
```
or use the batch script:
```bash
scripts/2_start_bot.bat
```

### Running Tests
```bash
python tests/quick_test.py
python tests/test_authentication.py
```

## 📊 Benefits of New Structure

1. **Better Organization**: Files are logically grouped
2. **Cleaner Root Directory**: Only essential files in root
3. **Improved Performance**: Separated cache and data files
4. **Easier Maintenance**: Clear separation of concerns
5. **Better Testing**: Dedicated test directory
6. **Documentation**: Centralized documentation

## 🔧 Configuration Updates

All file paths have been automatically updated to work with the new structure:
- Config paths now use relative references
- Import statements updated
- Cache files stored separately
- Logs go to cache directory

## 📝 Migration Notes

The reorganization maintains full backward compatibility while improving:
- Load times (separated cache files)
- Development workflow (organized code)
- Deployment process (cleaner structure)
- Debugging (better logging paths)