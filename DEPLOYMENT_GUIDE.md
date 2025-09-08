# Deployment Guide

## Project Overview

This repository contains two independent applications for managing a FAQ (Frequently Asked Questions) system:

1. **faq_bot** - A Python-based Telegram bot for providing FAQ responses
2. **faq_loader** - A C# application for loading and processing FAQ data

## Repository Structure

```
.
├── ARCHITECTURE.md         # Detailed architecture documentation
├── DEPLOYMENT_GUIDE.md     # This file
├── DOCUMENTATION.md        # Russian documentation
├── LICENSE                 # MIT License
├── README.md               # Russian README
├── README_EN.md            # English README for GitHub
├── faq_bot/                # Python Telegram bot application
│   ├── data/               # FAQ data and database files
│   ├── files/              # Supporting files (images, documents)
│   ├── src/                # Source code
│   ├── templates/          # Data templates
│   ├── tests/              # Test suite
│   ├── utils/              # Utility scripts
│   ├── .env.example        # Example configuration file
│   ├── pyproject.toml      # Python project configuration
│   ├── requirements.txt    # Python dependencies
│   └── ...                 # Various scripts and documentation
└── faq_loader/             # C# FAQ loader application
    ├── Business/           # Business logic
    ├── Data/               # Data access layer
    ├── Presentation/       # UI components
    ├── .env.example        # Example configuration file
    ├── UniversalFAQLoader.csproj  # C# project file
    └── ...                 # Other C# project files
```

## Setting up GitHub Repository

1. Go to GitHub.com and log in to your account
2. Click the "+" icon in the top right corner and select "New repository"
3. Name your repository (e.g., "faq-management-system")
4. Choose if it should be Public or Private
5. Don't initialize with a README (we already have one)
6. Don't add .gitignore or license files (we already have them)
7. Click "Create repository"

## Pushing to GitHub

After creating the repository on GitHub, you'll get instructions for pushing an existing repository. Execute these commands:

```bash
cd d:\Games
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git
git branch -M main
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username and `YOUR_REPOSITORY_NAME` with your repository name.

## Deploying the Applications

### faq_bot (Python Telegram Bot)

#### Prerequisites
- Python 3.8 or higher
- pip package manager

#### Installation
1. Navigate to the faq_bot directory:
   ```bash
   cd faq_bot
   ```

2. Install dependencies:
   ```bash
   pip install -e .
   ```
   Or install dependencies only:
   ```bash
   pip install .
   ```

#### Configuration
1. Create a `.env` file in the faq_bot directory based on `.env.example`
2. Set the required environment variables:
   ```
   BOT_TOKEN=your_telegram_bot_token
   ADMIN_ID=your_telegram_user_id
   ACCESS_PASSWORD=your_access_password
   ```

#### Running the Bot
Option 1 - Direct execution:
```bash
python run_bot.py
```

Option 2 - Using batch script:
```bash
start_bot.bat
```

### faq_loader (C# Application)

#### Prerequisites
- .NET 6.0 SDK
- Visual Studio 2022 or newer (for development)
- Or Visual Studio Code with C# extensions

#### Building
1. Navigate to the faq_loader directory:
   ```bash
   cd faq_loader
   ```

2. Build the project:
   ```bash
   dotnet build
   ```

#### Running
Option 1 - Direct execution:
```bash
dotnet run
```

Option 2 - Using batch script:
```bash
start_loader.bat
```

## Integration Between Applications

The two applications work together through shared data files:

1. **faq_loader** generates `faq.json` - the primary FAQ data file
2. **faq_loader** can create/update `analytics.db` - the analytics database
3. **faq_bot** consumes `faq.json` for answering user queries
4. **faq_bot** uses `analytics.db` for tracking usage statistics

Ensure both applications have access to the same data directory for proper integration.

## Testing

### faq_bot Tests
Navigate to the faq_bot directory and run:
```bash
cd faq_bot
python -m pytest tests/
```

Or run all tests:
```bash
python tests/run_all_tests.py
```

## Maintenance

### Updating Dependencies

#### faq_bot
Update Python dependencies:
```bash
cd faq_bot
pip install --upgrade -e .
```

#### faq_loader
Update C# dependencies:
```bash
cd faq_loader
dotnet restore
```

### Regular Tasks
1. Update FAQ data using faq_loader when FAQ content changes
2. Monitor bot performance and analytics
3. Update dependencies and security patches
4. Backup critical data files

## Troubleshooting

### Common Issues

#### faq_bot
- **Bot not responding**: Check BOT_TOKEN in .env file
- **Authentication failed**: Verify ADMIN_ID and ACCESS_PASSWORD
- **Database errors**: Ensure data directory has write permissions

#### faq_loader
- **Build failures**: Ensure .NET 6.0 SDK is installed
- **File access errors**: Check file permissions
- **Data processing issues**: Validate input data format

### Getting Help
- Check the documentation in each application's README.md
- Review the ARCHITECTURE.md file for detailed component information
- Open an issue on GitHub for bugs or feature requests