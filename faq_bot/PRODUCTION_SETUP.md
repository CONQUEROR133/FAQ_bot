# 🏭 Production Setup Guide

This guide provides instructions for deploying the FAQ Bot in a production environment.

## 📋 Prerequisites

1. **Server Requirements:**
   - Ubuntu 20.04 LTS or newer (recommended)
   - At least 4GB RAM
   - At least 20GB disk space
   - Python 3.8 or newer
   - Docker and Docker Compose (optional but recommended)

2. **Telegram Bot:**
   - Create a bot with [@BotFather](https://t.me/BotFather)
   - Note the bot token

3. **Environment Variables:**
   - Telegram Bot Token
   - Admin Telegram User ID
   - Access Password

## 🐳 Docker Deployment (Recommended)

### 1. Clone the Repository
```bash
git clone <repository-url>
cd faq_bot
```

### 2. Configure Environment
Create a `.env` file in the project root:
```env
BOT_TOKEN=your_bot_token_here
ADMIN_ID=your_telegram_id
ACCESS_PASSWORD=your_secure_password
```

### 3. Build and Start Services
```bash
docker-compose up -d
```

### 4. Monitor Logs
```bash
docker-compose logs -f
```

## 🖥️ Manual Deployment

### 1. Install System Dependencies
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv git
```

### 2. Clone Repository
```bash
git clone <repository-url>
cd faq_bot
```

### 3. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows
```

### 4. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure Environment
Create a `.env` file:
```env
BOT_TOKEN=your_bot_token_here
ADMIN_ID=your_telegram_id
ACCESS_PASSWORD=your_secure_password
```

### 6. Prepare Data Directory
```bash
mkdir -p data cache files logs
```

### 7. Train the Model
```bash
python train_model.py
```

### 8. Start the Bot
```bash
python run_bot.py
```

## 🛡️ Security Considerations

1. **Environment Variables:**
   - Never commit `.env` files to version control
   - Use strong passwords
   - Restrict access to configuration files

2. **Network Security:**
   - Use a firewall to restrict unnecessary access
   - Keep system and dependencies updated
   - Consider running behind a reverse proxy

3. **Access Control:**
   - Limit admin access to trusted users
   - Regularly review authenticated users
   - Monitor logs for suspicious activity

## 📊 Monitoring

### Health Check
The bot includes a built-in health check endpoint:
- Command: `/health`
- Provides system statistics and uptime information

### Log Monitoring
Logs are stored in the `logs/` directory:
- Main log: `logs/bot.log`
- JSON format for easy parsing
- Automatic rotation when reaching 10MB

### System Monitoring
Monitor system resources:
- CPU usage
- Memory usage
- Disk space
- Network connectivity

## 🔄 Maintenance

### Regular Tasks
1. **Log Rotation:**
   - Automatic rotation is enabled
   - Manually clean old logs if needed

2. **Model Retraining:**
   - Retrain when FAQ data changes significantly
   - Use `python train_model.py`

3. **System Updates:**
   - Regularly update system packages
   - Update Python dependencies

### Backup Strategy
1. **Data Backup:**
   - `data/faq.json` - FAQ content
   - `data/analytics.db` - Analytics data
   - `cache/` - Model files (embeddings and index)

2. **Configuration Backup:**
   - `.env` file (without sensitive data)
   - Custom configuration files

## 🚨 Troubleshooting

### Common Issues

1. **Bot Not Responding:**
   - Check internet connectivity
   - Verify bot token in `.env`
   - Check logs for errors

2. **Authentication Issues:**
   - Verify admin ID in `.env`
   - Check access password
   - Review authentication logs

3. **Model Loading Errors:**
   - Ensure model files exist in `cache/`
   - Check file permissions
   - Re-train model if corrupted

### Log Analysis
Use the log analysis tool:
```bash
python tools/aggregate_stats.py
```

## 📈 Performance Optimization

1. **Resource Allocation:**
   - Allocate sufficient RAM for model loading
   - Monitor CPU usage during peak times

2. **Caching:**
   - Embeddings are cached for performance
   - Clear cache when FAQ data changes

3. **Database Optimization:**
   - Regular maintenance of SQLite database
   - Monitor query performance

## 🆘 Support

For issues not covered in this guide:
1. Check the logs in `logs/bot.log`
2. Review the main README.md
3. Contact the development team