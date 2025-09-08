# Project Architecture Documentation

## Overview

This project consists of two independent applications that work together to provide a comprehensive FAQ management system:

1. **faq_bot** - A Python-based Telegram bot that serves FAQ responses to users
2. **faq_loader** - A C# application that processes and loads FAQ data

## faq_bot Architecture

### Core Components

#### Main Application (`src/main.py`)
- Entry point for the Telegram bot
- Initializes all components and starts the bot
- Handles graceful shutdown

#### Configuration (`src/config.py`)
- Loads environment variables
- Provides centralized configuration management
- Validates required settings

#### Database Layer (`src/database.py`)
- SQLite database interface
- Handles user authentication and statistics
- Manages analytics data

#### FAQ Processing (`src/faq_loader.py`)
- Loads FAQ data from JSON files
- Implements machine learning-based search algorithms
- Provides intelligent FAQ matching

#### Telegram Handlers (`src/handlers.py`)
- Processes incoming Telegram messages
- Implements command handlers (/start, /help, /search, etc.)
- Routes requests to appropriate services

#### Middleware Components
- **Authentication Middleware** (`src/auth_middleware.py`) - Validates user access
- **Security Middleware** (`src/security_middleware.py`) - Implements security measures
- **Dependency Injection** (`src/middlewares.py`) - Manages component dependencies

#### Performance Management (`src/performance_manager.py`)
- Implements caching mechanisms
- Manages resource usage
- Optimizes response times

### Data Flow

```
User Message → Telegram API → Bot Handlers → FAQ Processor → Database → Response
                    ↓
              Authentication
                    ↓
               Performance Manager
```

### Utility Components (`utils/`)
- **Bulk Loader** (`bulk_loader.py`) - Loads FAQ data from various formats
- **Diagnostics** (`diagnose_bot.py`) - Checks bot health and status
- **Drag & Drop Loader** (`drag_drop_loader.py`) - GUI-based data loading
- **Simple Bulk Loader** (`simple_bulk_loader.py`) - Basic data loading utility
- **Smart FAQ Processor** (`smart_faq_processor.py`) - Advanced FAQ processing

## faq_loader Architecture

### Core Components

#### Business Logic Layer (`Business/`)
- **FAQ Algorithm Service** (`FAQAlgorithmService.cs`) - Main processing engine
- **Dependency Analyzer** (`DependencyAnalyzer.cs`) - Analyzes relationships between FAQ entries
- **Semantic Grouper** (`SemanticGrouper.cs`) - Groups similar FAQ entries
- **Smart Linker** (`SmartLinker.cs`) - Creates intelligent links between entries
- **Response Optimizer** (`ResponseOptimizer.cs`) - Optimizes FAQ responses
- **FAQ Models** (`FAQModels.cs`) - Data models and structures

#### Data Access Layer (`Data/`)
- **Repository Interface** (`IFAQRepository.cs`) - Standard data access interface
- **JSON Repository** (`JsonFAQRepository.cs`) - JSON-based data storage
- **SQLite Repository** (`SqliteFAQRepository.cs`) - Database-based storage
- **Hybrid Repository** (`HybridFAQRepository.cs`) - Combined storage approach

#### Presentation Layer (`Presentation/`)
- **Main Window** (`Views/MainWindow.xaml`) - Primary application interface
- **View Model** (`ViewModels/MainViewModel.cs`) - Application logic for UI
- **Graph Visualization** (`Controls/FAQGraphVisualization.xaml`) - Visual representation of FAQ relationships

### Data Flow

```
Input Data → Processing Engine → Analysis → Optimization → Output Files
     ↓           ↓                ↓           ↓              ↓
  Formats   Algorithms      Relationships  Responses      JSON/DB
```

## Integration Between Applications

### Data Exchange
1. **faq_loader** generates `faq.json` - the primary FAQ data file
2. **faq_loader** can create/update `analytics.db` - the analytics database
3. **faq_bot** consumes `faq.json` for answering user queries
4. **faq_bot** uses `analytics.db` for tracking usage statistics

### Synchronization
- Both applications can work independently
- Data is synchronized through shared files
- No direct communication between applications required

## Technology Stack

### faq_bot
- **Language**: Python 3.8+
- **Framework**: python-telegram-bot
- **Database**: SQLite
- **ML Libraries**: scikit-learn, numpy, pandas
- **Build System**: setuptools/pip

### faq_loader
- **Language**: C# (.NET 6.0)
- **Framework**: WPF (Windows Presentation Foundation)
- **Database**: SQLite
- **Build System**: MSBuild
- **UI**: XAML

## Deployment Architecture

```
┌─────────────────┐    ┌──────────────────┐
│   Telegram      │    │   User Device    │
│   Messenger     │◄──►│   (Mobile/Web)   │
└─────────────────┘    └──────────────────┘
         │
         ▼
┌─────────────────┐
│   faq_bot       │
│   (Python)      │
│                 │
│  ┌───────────┐  │    ┌──────────────────┐
│  │ Telegram  │  │    │   Configuration  │
│  │  API      │◄─┼───►│   (.env)         │
│  └───────────┘  │    └──────────────────┘
│                 │
│  ┌───────────┐  │    ┌──────────────────┐
│  │ FAQ Data  │◄─┼───►│   faq.json       │
│  │ Processor │  │    └──────────────────┘
│  └───────────┘  │
│                 │    ┌──────────────────┐
│  ┌───────────┐  │    │   Analytics      │
│  │ Database  │◄─┼───►│   (analytics.db) │
│  │ Manager   │  │    └──────────────────┘
│  └───────────┘  │
└─────────────────┘

┌─────────────────┐    ┌──────────────────┐
│   faq_loader    │    │   Data Sources   │
│   (C#)          │◄──►│   (Files/DB)     │
└─────────────────┘    └──────────────────┘
         │
         ▼
┌─────────────────┐    ┌──────────────────┐
│   Processed     │◄──►│   Output Files   │
│   Data          │    │                  │
│                 │    │  ┌────────────┐  │
│                 │    │  │ faq.json   │  │
│                 │    │  └────────────┘  │
│                 │    │                  │
│                 │    │  ┌────────────┐  │
│                 │    │  │ analytics. │  │
│                 │    │  │ db         │  │
│                 │    │  └────────────┘  │
└─────────────────┘    └──────────────────┘
```

## Scalability Considerations

### Horizontal Scaling
- Multiple bot instances can be deployed behind a load balancer
- Database can be moved to a dedicated server
- FAQ processing can be distributed across multiple nodes

### Vertical Scaling
- Increase resources (CPU, RAM) for existing components
- Optimize database queries and indexes
- Implement more efficient caching strategies

## Security Considerations

### faq_bot
- User authentication via password or whitelist
- Rate limiting to prevent abuse
- Input validation and sanitization
- Secure storage of sensitive data

### faq_loader
- File access controls
- Data validation during processing
- Secure configuration management

## Maintenance

### Regular Tasks
- Update FAQ data using faq_loader
- Monitor bot performance and analytics
- Update dependencies and security patches
- Backup critical data files

### Monitoring
- Bot uptime monitoring
- Response time tracking
- User engagement metrics
- Error rate monitoring