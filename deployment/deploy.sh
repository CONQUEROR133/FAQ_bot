#!/bin/bash

# FAQ Bot Deployment Script for Linux
# This script automates the deployment process on Linux servers

set -e  # Exit on any error

# Configuration
BOT_USER="botuser"
BOT_GROUP="botuser"
INSTALL_DIR="/opt/faq-bot"
SERVICE_NAME="faq-bot"
PYTHON_VERSION="3.11"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1"
}

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        error "This script must be run as root"
        exit 1
    fi
}

# Install system dependencies
install_dependencies() {
    log "Installing system dependencies..."
    
    if command -v apt-get &> /dev/null; then
        # Ubuntu/Debian
        apt-get update
        apt-get install -y python3.11 python3.11-venv python3.11-dev \
                          build-essential git curl wget \
                          supervisor nginx certbot
    elif command -v yum &> /dev/null; then
        # CentOS/RHEL
        yum update -y
        yum install -y python311 python311-devel python311-pip \
                      gcc gcc-c++ git curl wget \
                      supervisor nginx certbot
    else
        error "Unsupported package manager"
        exit 1
    fi
}

# Create bot user
create_user() {
    log "Creating bot user..."
    
    if ! id "$BOT_USER" &>/dev/null; then
        useradd -r -s /bin/bash -d "$INSTALL_DIR" -m "$BOT_USER"
        log "User $BOT_USER created"
    else
        log "User $BOT_USER already exists"
    fi
}

# Clone or update repository
setup_repository() {
    log "Setting up repository..."
    
    if [[ ! -d "$INSTALL_DIR" ]]; then
        mkdir -p "$INSTALL_DIR"
        chown "$BOT_USER:$BOT_GROUP" "$INSTALL_DIR"
    fi
    
    # If this script is being run from the repo directory
    if [[ -f "run_bot.py" ]]; then
        log "Copying files from current directory..."
        cp -r . "$INSTALL_DIR/"
        chown -R "$BOT_USER:$BOT_GROUP" "$INSTALL_DIR"
    else
        error "run_bot.py not found. Please run this script from the bot directory."
        exit 1
    fi
}

# Setup Python environment
setup_python() {
    log "Setting up Python virtual environment..."
    
    cd "$INSTALL_DIR"
    
    # Create virtual environment as bot user
    sudo -u "$BOT_USER" python3.11 -m venv venv
    
    # Install dependencies
    sudo -u "$BOT_USER" "$INSTALL_DIR/venv/bin/pip" install --upgrade pip
    sudo -u "$BOT_USER" "$INSTALL_DIR/venv/bin/pip" install -r requirements.txt
    
    log "Python environment setup complete"
}

# Setup environment configuration
setup_environment() {
    log "Setting up environment configuration..."
    
    if [[ ! -f "$INSTALL_DIR/.env" ]]; then
        if [[ -f "$INSTALL_DIR/.env.production" ]]; then
            cp "$INSTALL_DIR/.env.production" "$INSTALL_DIR/.env"
            log "Production environment template copied"
        else
            error ".env.production template not found"
            exit 1
        fi
        
        warn "Please update $INSTALL_DIR/.env with your actual configuration values"
    else
        log "Environment file already exists"
    fi
    
    chown "$BOT_USER:$BOT_GROUP" "$INSTALL_DIR/.env"
    chmod 600 "$INSTALL_DIR/.env"
}

# Setup systemd service
setup_service() {
    log "Setting up systemd service..."
    
    if [[ -f "$INSTALL_DIR/deployment/faq-bot.service" ]]; then
        cp "$INSTALL_DIR/deployment/faq-bot.service" "/etc/systemd/system/$SERVICE_NAME.service"
        systemctl daemon-reload
        systemctl enable "$SERVICE_NAME"
        log "Systemd service configured"
    else
        error "Service file not found"
        exit 1
    fi
}

# Setup nginx reverse proxy (optional)
setup_nginx() {
    log "Setting up nginx configuration..."
    
    cat > "/etc/nginx/sites-available/faq-bot" << EOF
server {
    listen 80;
    server_name your-domain.com;  # Update this
    
    location /health {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
    
    location /metrics {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        # Add basic auth for metrics endpoint
        auth_basic "Metrics";
        auth_basic_user_file /etc/nginx/.htpasswd;
    }
}
EOF
    
    ln -sf "/etc/nginx/sites-available/faq-bot" "/etc/nginx/sites-enabled/"
    nginx -t && systemctl reload nginx
    
    log "Nginx configuration complete"
}

# Setup log rotation
setup_logrotate() {
    log "Setting up log rotation..."
    
    cat > "/etc/logrotate.d/faq-bot" << EOF
$INSTALL_DIR/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 $BOT_USER $BOT_GROUP
    postrotate
        systemctl reload $SERVICE_NAME
    endscript
}
EOF
    
    log "Log rotation configured"
}

# Initialize database and cache
initialize_data() {
    log "Initializing database and cache..."
    
    cd "$INSTALL_DIR"
    
    # Create directories
    sudo -u "$BOT_USER" mkdir -p data cache files backups logs
    
    # Initialize database if it doesn't exist
    if [[ ! -f "data/analytics.db" ]]; then
        sudo -u "$BOT_USER" "$INSTALL_DIR/venv/bin/python" -c "
import sys
sys.path.insert(0, '$INSTALL_DIR/src')
from database import Database
db = Database()
db.init_db()
print('Database initialized')
"
    fi
    
    log "Data initialization complete"
}

# Start services
start_services() {
    log "Starting services..."
    
    systemctl start "$SERVICE_NAME"
    systemctl status "$SERVICE_NAME" --no-pager
    
    log "Services started"
}

# Health check
health_check() {
    log "Performing health check..."
    
    sleep 5  # Give the service time to start
    
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        log "✅ Service is running"
    else
        error "❌ Service is not running"
        systemctl status "$SERVICE_NAME" --no-pager
        exit 1
    fi
    
    # Check if the process is responding
    cd "$INSTALL_DIR"
    if sudo -u "$BOT_USER" "$INSTALL_DIR/venv/bin/python" -c "
import sys
sys.path.insert(0, '$INSTALL_DIR/src')
from config import config
print('✅ Configuration check passed')
" 2>/dev/null; then
        log "✅ Configuration check passed"
    else
        error "❌ Configuration check failed"
        exit 1
    fi
}

# Main deployment function
main() {
    log "Starting FAQ Bot deployment..."
    
    check_root
    install_dependencies
    create_user
    setup_repository
    setup_python
    setup_environment
    initialize_data
    setup_service
    setup_nginx
    setup_logrotate
    start_services
    health_check
    
    log "🎉 Deployment completed successfully!"
    log "Please update $INSTALL_DIR/.env with your actual configuration"
    log "Service logs: journalctl -u $SERVICE_NAME -f"
    log "Bot logs: tail -f $INSTALL_DIR/logs/bot.log"
}

# Run main function
main "$@"