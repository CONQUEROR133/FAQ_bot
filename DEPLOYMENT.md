# 🚀 FAQ Bot Deployment Guide

This guide covers deployment options for the FAQ Bot in different environments.

## 📋 Prerequisites

- Python 3.9+ (recommended: 3.11)
- Git (for updates)
- 4GB+ RAM (for ML model)
- Internet connection for model downloads

## 🛠️ Environment Setup

### Development Environment

1. Copy development configuration:
   ```bash
   cp .env.development .env
   ```

2. Update `.env` with your values:
   ```bash
   BOT_TOKEN="your_development_bot_token"
   ADMIN_ID="your_telegram_user_id"
   ```

3. Run setup:
   ```bash
   scripts/setup.bat          # Windows
   ./deployment/deploy.sh     # Linux
   ```

### Production Environment

1. Copy production configuration:
   ```bash
   cp .env.production .env
   ```

2. Update critical settings:
   ```bash
   BOT_TOKEN="your_production_bot_token"
   ACCESS_PASSWORD="strong_production_password"
   ADMIN_ID="your_telegram_user_id"
   ```

3. Review security settings in `.env`

## 🐳 Docker Deployment

### Quick Start with Docker Compose

1. Ensure `.env` is configured
2. Build and run:
   ```bash
   docker-compose up -d
   ```

3. Check status:
   ```bash
   docker-compose ps
   docker-compose logs faq-bot
   ```

### Manual Docker Build

```bash
# Build image
docker build -t faq-bot .

# Run container
docker run -d \
  --name faq-bot \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/cache:/app/cache \
  -v $(pwd)/files:/app/files \
  faq-bot
```

## 🐧 Linux Server Deployment

### Automated Deployment

1. Upload project files to server
2. Make deployment script executable:
   ```bash
   chmod +x deployment/deploy.sh
   ```

3. Run as root:
   ```bash
   sudo ./deployment/deploy.sh
   ```

This will:
- Install system dependencies
- Create bot user
- Setup Python environment
- Configure systemd service
- Setup nginx reverse proxy
- Configure log rotation

### Manual Linux Setup

1. **Create user:**
   ```bash
   sudo useradd -r -s /bin/bash -d /opt/faq-bot -m botuser
   ```

2. **Setup files:**
   ```bash
   sudo cp -r . /opt/faq-bot/
   sudo chown -R botuser:botuser /opt/faq-bot
   ```

3. **Install dependencies:**
   ```bash
   cd /opt/faq-bot
   sudo -u botuser python3 -m venv venv
   sudo -u botuser venv/bin/pip install -r requirements.txt
   ```

4. **Setup systemd service:**
   ```bash
   sudo cp deployment/faq-bot.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable faq-bot
   sudo systemctl start faq-bot
   ```

## 🪟 Windows Deployment

### Using Scripts

1. Run deployment manager:
   ```cmd
   scripts\deploy.bat
   ```

2. Select option 2 for production setup

### Manual Windows Setup

1. **Setup environment:**
   ```cmd
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure as Windows Service:**
   - Install NSSM (Non-Sucking Service Manager)
   - Create service:
     ```cmd
     nssm install "FAQ Bot" "C:\path\to\venv\Scripts\python.exe" "C:\path\to\run_bot.py"
     ```

## 📊 Monitoring Setup

### Prometheus Monitoring

1. **Enable monitoring profile:**
   ```bash
   docker-compose --profile monitoring up -d
   ```

2. **Access dashboards:**
   - Prometheus: http://localhost:9090
   - Bot metrics: http://localhost:8080/metrics

### Health Checks

- **Docker:** Built-in health check every 30s
- **systemd:** Service monitoring with auto-restart
- **Manual:** `scripts/deploy.bat` → option 7

## 🔄 Updates and Maintenance

### Automated Updates

```bash
# Using deployment script (Windows)
scripts\deploy.bat → option 4

# Using Git (Linux)
cd /opt/faq-bot
git pull
systemctl restart faq-bot
```

### Backup and Restore

```bash
# Create backup
scripts\deploy.bat → option 5

# Restore backup
scripts\deploy.bat → option 6

# Manual backup (Linux)
tar -czf backup-$(date +%Y%m%d).tar.gz data cache .env
```

## 🔧 Configuration Management

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `BOT_TOKEN` | Telegram bot token | Required |
| `ADMIN_ID` | Admin user ID | Required |
| `ACCESS_PASSWORD` | Bot access password | Required |
| `DEBUG` | Enable debug mode | false |
| `LOG_LEVEL` | Logging level | INFO |
| `SIMILARITY_THRESHOLD` | ML similarity threshold | 0.73 |
| `MAX_REQUESTS_PER_MINUTE` | Rate limiting | 20 |

### File Structure

```
/opt/faq-bot/
├── src/              # Source code
├── data/             # Database and FAQ data
├── cache/            # ML models and embeddings
├── files/            # Bot resource files
├── logs/             # Application logs
├── backups/          # Automated backups
├── deployment/       # Deployment configs
└── .env             # Environment config
```

## 🚨 Troubleshooting

### Common Issues

1. **Import errors:**
   ```bash
   export PYTHONPATH=/opt/faq-bot/src  # Linux
   set PYTHONPATH=C:\path\to\src       # Windows
   ```

2. **Permission errors:**
   ```bash
   sudo chown -R botuser:botuser /opt/faq-bot
   ```

3. **Memory issues:**
   - Increase swap space
   - Use smaller ML model
   - Enable model offloading

4. **Network timeouts:**
   - Check internet connection
   - Increase timeout values in `.env`
   - Verify bot token validity

### Log Analysis

```bash
# Service logs (Linux)
journalctl -u faq-bot -f

# Application logs
tail -f logs/bot.log

# Docker logs
docker-compose logs faq-bot -f
```

## 🔐 Security Considerations

### Production Security

1. **Use strong passwords** for `ACCESS_PASSWORD`
2. **Limit file permissions:**
   ```bash
   chmod 600 .env
   chmod 755 src/
   ```
3. **Enable firewall:**
   ```bash
   ufw allow ssh
   ufw allow 80
   ufw allow 443
   ufw enable
   ```
4. **Regular updates:**
   - System packages
   - Python dependencies
   - Bot code

### Monitoring Security

- Enable rate limiting in production
- Monitor for suspicious activity
- Review logs regularly
- Use HTTPS for web interfaces

## 📞 Support

For deployment issues:
1. Check logs for error messages
2. Verify configuration values
3. Test with development environment first
4. Use health check tools provided

## 🎯 Quick Commands Reference

```bash
# Start bot
systemctl start faq-bot          # Linux
scripts\2_start_bot.bat          # Windows

# Stop bot
systemctl stop faq-bot           # Linux
Ctrl+C                           # Windows

# Status check
systemctl status faq-bot         # Linux
scripts\deploy.bat → option 7    # Windows

# View logs
journalctl -u faq-bot -f         # Linux
scripts\deploy.bat → option 8    # Windows

# Update bot
git pull && systemctl restart faq-bot  # Linux
scripts\deploy.bat → option 4          # Windows
```