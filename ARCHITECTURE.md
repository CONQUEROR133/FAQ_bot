# Project Architecture Documentation

## Overview

This project is a Python-based Telegram bot that serves FAQ responses to users using semantic search capabilities.

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

## Technology Stack

### faq_bot
- **Language**: Python 3.8+
- **Framework**: python-telegram-bot
- **Database**: SQLite
- **ML Libraries**: scikit-learn, numpy, pandas
- **Build System**: setuptools/pip

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

## Maintenance

### Regular Tasks
- Update FAQ data in faq.json
- Monitor bot performance and analytics
- Update dependencies and security patches
- Backup critical data files

### Monitoring
- Bot uptime monitoring
- Response time tracking
- User engagement metrics
- Error rate monitoring