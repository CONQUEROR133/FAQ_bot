# FAQ Management System

This project contains two independent applications for managing a FAQ (Frequently Asked Questions) system:

1. **faq_bot** - A Python-based Telegram bot for providing FAQ responses
2. **faq_loader** - A C# application for loading and processing FAQ data

## Project Structure

```
Games/
├── faq_bot/           # Telegram bot for providing FAQ (Python)
│   ├── src/           # Source code of the bot
│   ├── data/          # FAQ data and database
│   ├── utils/         # Bot utility tools
│   ├── scripts/       # Bot management scripts
│   ├── templates/     # Data templates
│   ├── files/         # FAQ related files
│   ├── tests/         # Tests
│   ├── pyproject.toml # Project configuration and bot dependencies
│   ├── .env           # Bot configuration
│   └── README.md      # Bot documentation
│
├── faq_loader/        # Utility for loading FAQ data (C#)
│   ├── Business/      # Business logic and algorithms
│   ├── Data/          # Data repositories
│   ├── Presentation/  # WPF UI components
│   ├── Program.cs     # Entry point
│   ├── UniversalFAQLoader.sln  # Visual Studio solution file
│   ├── UniversalFAQLoader.csproj  # Project file
│   ├── .env           # Loader configuration
│   └── README.md      # Loader documentation
```

## Applications Overview

### faq_bot (Python Telegram Bot)

A sophisticated Telegram bot that provides intelligent FAQ responses using machine learning algorithms.

#### Key Components:

##### src/ - Main source code
- `main.py` - Bot entry point, initialization and startup
- `config.py` - Application configuration, environment variable loading
- `database.py` - SQLite database operations for statistics and authentication
- `faq_loader.py` - FAQ data loading and searching with ML
- `handlers.py` - Telegram command and message handlers
- `auth_middleware.py` - Middleware for user authentication
- `security_middleware.py` - Middleware for security
- `middlewares.py` - Middleware for dependency injection
- `performance_manager.py` - Performance management and caching

##### utils/ - Utility tools
- `bulk_loader.py` - Loading FAQ data from various formats
- `diagnose_bot.py` - Bot state diagnostics
- `drag_drop_loader.py` - Drag-and-drop loader support
- `simple_bulk_loader.py` - Simple data loader
- `smart_faq_processor.py` - Intelligent FAQ data processing

##### data/ - Application data
- `faq.json` - Main FAQ data file
- `analytics.db` - SQLite database for statistics and authentication

##### templates/ - Data loading templates
- Templates in CSV, TXT, XLSX formats for loading FAQ data

##### files/ - FAQ-related files
- Images, documents and other files mentioned in FAQ

##### scripts/ - Management scripts
- Batch scripts for various bot operations

##### tests/ - Tests
- Unit and integration tests for bot components

#### Installation

```bash
cd faq_bot
pip install -e .
```

Or install dependencies only:

```bash
pip install .
```

#### Running the Bot

##### Via Python:

```bash
python run_bot.py
```

##### Via batch script:

```bash
start_bot.bat
```

#### Configuration

Create a `.env` file with the following variables:

```
BOT_TOKEN=your_telegram_bot_token
ADMIN_ID=your_telegram_user_id
ACCESS_PASSWORD=your_access_password
```

### faq_loader (C# Application)

A powerful C# application for loading, processing, and analyzing FAQ data with advanced algorithms.

#### Key Components:

##### Business/ - Business logic
- `FAQAlgorithmService.cs` - Main algorithm service
- `DependencyAnalyzer.cs` - FAQ dependency analysis
- `SemanticGrouper.cs` - Semantic grouping
- `SmartLinker.cs` - Intelligent linking between entries
- `ResponseOptimizer.cs` - Response optimization
- `IFAQAlgorithm.cs` - Algorithm interface
- `FAQModels.cs` - Data models

##### Data/ - Data repositories
- `IFAQRepository.cs` - Repository interface
- `JsonFAQRepository.cs` - JSON data repository
- `SqliteFAQRepository.cs` - SQLite repository
- `HybridFAQRepository.cs` - Hybrid repository

##### Presentation/ - WPF UI
- `Views/MainWindow.xaml` - Main application window
- `ViewModels/MainViewModel.cs` - ViewModel for main window
- `Controls/FAQGraphVisualization.xaml` - Graph visualization control

##### Project files
- `Program.cs` - Application entry point
- `UniversalFAQLoader.csproj` - Project file
- `UniversalFAQLoader.sln` - Visual Studio solution file

#### Installation and Build

##### Requirements:
- .NET 6.0 SDK
- Visual Studio 2022 or newer (for development)

##### Building via command line:

```bash
cd faq_loader
dotnet build
```

##### Running:

```bash
cd faq_loader
dotnet run
```

##### Via batch script:

```bash
cd faq_loader
start_loader.bat
```

## Application Integration

1. **faq_loader** creates data for **faq_bot**:
   - Generates faq.json
   - Can create and update analytics.db

2. **faq_bot** uses data from **faq_loader**:
   - Loads faq.json for searching answers
   - Uses analytics.db for statistics

## Configuration

Each application uses its own `.env` file for configuration. See each application's documentation for details.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request