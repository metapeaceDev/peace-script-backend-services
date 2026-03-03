# DMM Backend Deployment Guide

**Digital Mind Model Backend - Production Deployment**

Version: 1.4.0  
Last Updated: 4 November 2568 (2025)  
Status: ✅ Production Ready

---

## Table of Contents

1. [Overview](#overview)
2. [System Requirements](#system-requirements)
3. [Pre-Deployment Checklist](#pre-deployment-checklist)
4. [Installation Steps](#installation-steps)
5. [Production Configuration](#production-configuration)
6. [SSL/TLS Setup](#ssltls-setup)
7. [Process Management](#process-management)
8. [Reverse Proxy Setup](#reverse-proxy-setup)
9. [Database Setup](#database-setup)
10. [Security Hardening](#security-hardening)
11. [Monitoring Setup](#monitoring-setup)
12. [Post-Deployment Verification](#post-deployment-verification)
13. [Troubleshooting](#troubleshooting)

---

## Overview

This guide provides comprehensive instructions for deploying the DMM Backend to production environments. The system consists of:

- **Backend API**: FastAPI application (Python 3.9+)
- **Database**: MongoDB (NoSQL document database)
- **Frontend**: React + Vite (separate deployment)
- **Process Manager**: PM2 or systemd
- **Web Server**: Nginx (reverse proxy)

### Deployment Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Internet                          │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│              Nginx (Port 80/443)                    │
│           SSL Termination & Proxy                   │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│          FastAPI Backend (Port 8000)                │
│              Uvicorn ASGI Server                    │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│         MongoDB Database (Port 27017)               │
│            Document Store & Indexes                 │
└─────────────────────────────────────────────────────┘
```

---

## System Requirements

### Hardware Requirements

#### Minimum (Development/Testing)
- **CPU**: 2 cores
- **RAM**: 4 GB
- **Storage**: 20 GB SSD
- **Network**: 10 Mbps

#### Recommended (Production)
- **CPU**: 4+ cores
- **RAM**: 8+ GB
- **Storage**: 50+ GB SSD
- **Network**: 100+ Mbps

#### High Performance (Production)
- **CPU**: 8+ cores
- **RAM**: 16+ GB
- **Storage**: 100+ GB NVMe SSD
- **Network**: 1+ Gbps

### Software Requirements

#### Operating System
- **Primary**: Ubuntu 22.04 LTS (recommended)
- **Alternative**: Ubuntu 20.04 LTS, Debian 11+, CentOS 8+, macOS 12+

#### Core Dependencies
- **Python**: 3.9, 3.10, or 3.11
- **MongoDB**: 6.0+ (7.0+ recommended)
- **Nginx**: 1.18+ (or Apache 2.4+)
- **Git**: 2.30+

#### Optional Tools
- **PM2**: 5.0+ (Node.js process manager)
- **systemd**: Built-in (Linux service manager)
- **Docker**: 24.0+ (containerized deployment)
- **Let's Encrypt**: certbot (SSL certificates)

---

## Pre-Deployment Checklist

### Infrastructure Preparation

- [ ] Server provisioned with adequate resources
- [ ] Domain name registered and DNS configured
- [ ] Firewall rules configured (ports 80, 443, 8000, 27017)
- [ ] SSH access configured with key-based authentication
- [ ] Backup strategy documented and tested
- [ ] Monitoring system ready

### Software Installation

- [ ] Python 3.9+ installed
- [ ] MongoDB 6.0+ installed and configured
- [ ] Nginx installed
- [ ] Git installed
- [ ] SSL certificate obtained (Let's Encrypt recommended)

### Configuration Files

- [ ] `.env` file prepared with production values
- [ ] MongoDB connection string configured
- [ ] API keys and secrets generated
- [ ] CORS origins configured
- [ ] Log directories created

### Security

- [ ] Firewall enabled and configured
- [ ] SSH password authentication disabled
- [ ] MongoDB authentication enabled
- [ ] Secrets rotated from development values
- [ ] Security headers configured

### Documentation

- [ ] Deployment plan documented
- [ ] Rollback procedure documented
- [ ] Team trained on deployment process
- [ ] Emergency contacts listed

---

## Installation Steps

### Step 1: System Update

```bash
# Ubuntu/Debian
sudo apt update
sudo apt upgrade -y

# CentOS/RHEL
sudo yum update -y

# Install essential tools
sudo apt install -y build-essential curl git wget vim
```

### Step 2: Install Python 3.9+

```bash
# Check Python version
python3 --version

# If Python 3.9+ not available, install
sudo apt install -y python3.9 python3.9-venv python3-pip

# Verify installation
python3.9 --version
```

### Step 3: Install MongoDB

```bash
# Import MongoDB GPG key
wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -

# Add MongoDB repository
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list

# Update package list
sudo apt update

# Install MongoDB
sudo apt install -y mongodb-org

# Start MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod

# Verify installation
mongod --version
sudo systemctl status mongod
```

### Step 4: Install Nginx

```bash
# Install Nginx
sudo apt install -y nginx

# Start Nginx
sudo systemctl start nginx
sudo systemctl enable nginx

# Verify installation
nginx -v
sudo systemctl status nginx
```

### Step 5: Install MongoDB Database Tools

```bash
# Ubuntu/Debian
sudo apt install -y mongodb-database-tools

# Verify installation
mongodump --version
mongorestore --version
```

### Step 6: Create Application User

```bash
# Create dedicated user for the application
sudo useradd -m -s /bin/bash dmm
sudo usermod -aG sudo dmm  # Optional: if admin access needed

# Switch to dmm user
sudo su - dmm
```

### Step 7: Clone Repository

```bash
# As dmm user
cd /home/dmm

# Clone repository
git clone https://github.com/PeaceScript/digital-mind.git
cd digital-mind

# Checkout production branch
git checkout main  # or your production branch
```

### Step 8: Setup Python Virtual Environment

```bash
# Navigate to backend directory
cd dmm_backend

# Create virtual environment
python3.9 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Verify installation
pip list
```

### Step 9: Create Required Directories

```bash
# Create directories
mkdir -p logs backups uploads temp

# Set permissions
chmod 755 logs backups uploads temp
```

---

## Production Configuration

### Step 1: Create Production Environment File

```bash
# Create .env file
nano .env
```

**Production `.env` template**:

```bash
# Application Settings
API_TITLE="Digital Mind API"
API_DESCRIPTION="API for simulating and interacting with a Digital Mind Model."
API_VERSION="1.4.0"
DEBUG_MODE=false
API_KEY="your-secure-api-key-change-this-in-production"

# Database Configuration
MONGO_URI="mongodb://dmm_user:STRONG_PASSWORD@localhost:27017/digital_mind_model?authSource=admin"
MONGODB_URI="mongodb://dmm_user:STRONG_PASSWORD@localhost:27017/digital_mind_model?authSource=admin"
MONGO_DB_NAME="digital_mind_model"
DATABASE_NAME="digital_mind_model"

# Security - JWT
JWT_SECRET_KEY="your-jwt-secret-key-min-32-chars-change-in-production"
JWT_ALGORITHM="HS256"
JWT_EXPIRATION_MINUTES=60

# CORS Configuration (Production URLs)
CORS_ORIGINS="https://yourdomain.com,https://www.yourdomain.com,https://api.yourdomain.com"

# Backup Configuration
BACKUP_DIR="/home/dmm/digital-mind/dmm_backend/backups"
RETENTION_DAYS=30
COMPRESS=true
NOTIFY_EMAIL="admin@yourdomain.com"

# Logging
LOG_LEVEL="INFO"
LOG_FILE="/home/dmm/digital-mind/dmm_backend/logs/app.log"

# Server Configuration
HOST="127.0.0.1"
PORT=8000
WORKERS=4

# Optional: Database TTL
KAMMA_TTL_SECONDS=2592000  # 30 days
UNIQUE_TIMELINE_PER_MODEL=false
```

**Important**: 
- ⚠️ Change all default passwords and secrets
- ⚠️ Use strong, randomly generated values
- ⚠️ Never commit `.env` to version control
- ⚠️ Restrict file permissions: `chmod 600 .env`

### Step 2: Generate Secure Secrets

```bash
# Generate API key (32 bytes, base64 encoded)
python3 -c "import secrets; import base64; print(base64.urlsafe_b64encode(secrets.token_bytes(32)).decode())"

# Generate JWT secret (32 bytes, hex encoded)
python3 -c "import secrets; print(secrets.token_hex(32))"

# Or use openssl
openssl rand -base64 32
openssl rand -hex 32
```

### Step 3: Configure MongoDB Authentication

```bash
# Connect to MongoDB
mongosh

# Switch to admin database
use admin

# Create admin user
db.createUser({
  user: "admin",
  pwd: "STRONG_ADMIN_PASSWORD",
  roles: [ { role: "userAdminAnyDatabase", db: "admin" }, "readWriteAnyDatabase" ]
})

# Create application user
db.createUser({
  user: "dmm_user",
  pwd: "STRONG_APP_PASSWORD",
  roles: [ { role: "readWrite", db: "digital_mind_model" } ]
})

# Exit mongosh
exit
```

**Enable MongoDB authentication**:

```bash
# Edit MongoDB config
sudo nano /etc/mongod.conf

# Add security section:
security:
  authorization: enabled

# Restart MongoDB
sudo systemctl restart mongod
```

### Step 4: Test Database Connection

```bash
# Test connection with new credentials
mongosh "mongodb://dmm_user:STRONG_APP_PASSWORD@localhost:27017/digital_mind_model?authSource=admin"

# Verify access
use digital_mind_model
db.stats()
exit
```

---

## SSL/TLS Setup

### Option 1: Let's Encrypt (Recommended)

```bash
# Install certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtain certificate (HTTP-01 challenge)
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Follow prompts:
# - Enter email address
# - Agree to terms
# - Choose redirect option (2)

# Verify auto-renewal
sudo certbot renew --dry-run

# Certificate locations:
# - Certificate: /etc/letsencrypt/live/yourdomain.com/fullchain.pem
# - Private Key: /etc/letsencrypt/live/yourdomain.com/privkey.pem
```

### Option 2: Self-Signed Certificate (Development/Testing)

```bash
# Create directory
sudo mkdir -p /etc/nginx/ssl

# Generate self-signed certificate (valid 1 year)
sudo openssl req -x509 -nodes -days 365 -newkey rsa:4096 \
  -keyout /etc/nginx/ssl/dmm.key \
  -out /etc/nginx/ssl/dmm.crt \
  -subj "/C=TH/ST=Bangkok/L=Bangkok/O=DMM/CN=yourdomain.com"

# Set permissions
sudo chmod 600 /etc/nginx/ssl/dmm.key
sudo chmod 644 /etc/nginx/ssl/dmm.crt
```

### Option 3: Commercial Certificate

1. Generate CSR (Certificate Signing Request)
2. Purchase certificate from CA
3. Download certificate files
4. Install certificate in `/etc/nginx/ssl/`
5. Configure Nginx to use certificate

---

## Process Management

### Option 1: systemd (Recommended for Linux)

**Create systemd service file**:

```bash
sudo nano /etc/systemd/system/dmm-backend.service
```

**Service configuration**:

```ini
[Unit]
Description=DMM Backend API Service
After=network.target mongod.service
Requires=mongod.service

[Service]
Type=notify
User=dmm
Group=dmm
WorkingDirectory=/home/dmm/digital-mind/dmm_backend
Environment="PATH=/home/dmm/digital-mind/dmm_backend/venv/bin"
EnvironmentFile=/home/dmm/digital-mind/dmm_backend/.env
ExecStart=/home/dmm/digital-mind/dmm_backend/venv/bin/uvicorn main:app \
  --host 127.0.0.1 \
  --port 8000 \
  --workers 4 \
  --log-level info \
  --access-log \
  --use-colors
Restart=always
RestartSec=10
StandardOutput=append:/home/dmm/digital-mind/dmm_backend/logs/app.log
StandardError=append:/home/dmm/digital-mind/dmm_backend/logs/error.log

# Security
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/home/dmm/digital-mind/dmm_backend/logs /home/dmm/digital-mind/dmm_backend/backups
ProtectKernelTunables=true
ProtectControlGroups=true
RestrictRealtime=true
RestrictNamespaces=true

[Install]
WantedBy=multi-user.target
```

**Enable and start service**:

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service (start on boot)
sudo systemctl enable dmm-backend

# Start service
sudo systemctl start dmm-backend

# Check status
sudo systemctl status dmm-backend

# View logs
sudo journalctl -u dmm-backend -f

# Restart service
sudo systemctl restart dmm-backend

# Stop service
sudo systemctl stop dmm-backend
```

### Option 2: PM2 (Alternative)

**Install PM2**:

```bash
# Install Node.js (if not installed)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Install PM2 globally
sudo npm install -g pm2

# Verify installation
pm2 --version
```

**Create PM2 ecosystem file**:

```bash
nano ecosystem.config.js
```

**Configuration**:

```javascript
module.exports = {
  apps: [{
    name: 'dmm-backend',
    script: './venv/bin/uvicorn',
    args: 'main:app --host 127.0.0.1 --port 8000 --workers 4',
    cwd: '/home/dmm/digital-mind/dmm_backend',
    interpreter: 'none',
    env: {
      NODE_ENV: 'production',
    },
    error_file: './logs/pm2-error.log',
    out_file: './logs/pm2-out.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
    merge_logs: true,
    autorestart: true,
    max_restarts: 10,
    min_uptime: '10s',
    max_memory_restart: '500M',
    watch: false,
    instances: 1,
    exec_mode: 'fork'
  }]
};
```

**Start with PM2**:

```bash
# Start application
pm2 start ecosystem.config.js

# Save PM2 process list
pm2 save

# Setup PM2 startup script
pm2 startup systemd

# Check status
pm2 status
pm2 logs dmm-backend
pm2 monit

# Restart
pm2 restart dmm-backend

# Stop
pm2 stop dmm-backend
```

---

## Reverse Proxy Setup

### Nginx Configuration

**Create Nginx site configuration**:

```bash
sudo nano /etc/nginx/sites-available/dmm-backend
```

**Configuration for HTTP + HTTPS**:

```nginx
# Upstream definition
upstream dmm_backend {
    server 127.0.0.1:8000 fail_timeout=10s max_fails=3;
    keepalive 32;
}

# HTTP - Redirect to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name yourdomain.com www.yourdomain.com;

    # Let's Encrypt challenge
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }

    # Redirect all HTTP to HTTPS
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS - Main configuration
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_trusted_certificate /etc/letsencrypt/live/yourdomain.com/chain.pem;

    # SSL Security Settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_stapling on;
    ssl_stapling_verify on;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline';" always;

    # Logging
    access_log /var/log/nginx/dmm-backend-access.log;
    error_log /var/log/nginx/dmm-backend-error.log;

    # Client body size (for file uploads)
    client_max_body_size 10M;

    # Timeouts
    proxy_connect_timeout 60s;
    proxy_send_timeout 60s;
    proxy_read_timeout 60s;
    send_timeout 60s;

    # Proxy settings
    location /api {
        proxy_pass http://dmm_backend;
        proxy_http_version 1.1;
        
        # Headers
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port $server_port;
        
        # WebSocket support (if needed)
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Buffering
        proxy_buffering off;
        proxy_request_buffering off;
        
        # Keepalive
        proxy_set_header Connection "";
    }

    # Health check endpoint
    location /health {
        proxy_pass http://dmm_backend/health;
        access_log off;
    }

    # API documentation
    location /docs {
        proxy_pass http://dmm_backend/docs;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # Root redirect
    location = / {
        return 302 /docs;
    }

    # Deny access to hidden files
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }
}
```

**Enable site and restart Nginx**:

```bash
# Create symlink to enable site
sudo ln -s /etc/nginx/sites-available/dmm-backend /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx

# Check status
sudo systemctl status nginx
```

---

## Database Setup

### Initialize Database

```bash
# Activate virtual environment
cd /home/dmm/digital-mind/dmm_backend
source venv/bin/activate

# Run database initialization (if you have a script)
python -m seed_db

# Or manually create collections and indexes
python -c "
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

async def init_db():
    client = AsyncIOMotorClient('mongodb://dmm_user:PASSWORD@localhost:27017/digital_mind_model?authSource=admin')
    db = client.digital_mind_model
    
    # Create collections if they don't exist
    collections = await db.list_collection_names()
    if 'users' not in collections:
        await db.create_collection('users')
    if 'models' not in collections:
        await db.create_collection('models')
    
    # Create indexes
    await db.users.create_index('username', unique=True)
    await db.users.create_index('email', unique=True)
    
    print('Database initialized successfully')
    client.close()

asyncio.run(init_db())
"
```

### Database Backup Setup

```bash
# Create cron job for daily backups
crontab -e

# Add this line (daily at 2 AM)
0 2 * * * cd /home/dmm/digital-mind/dmm_backend && MONGODB_URI="mongodb://dmm_user:PASSWORD@localhost:27017/digital_mind_model?authSource=admin" ./venv/bin/python scripts/backup_database.py >> logs/backup.log 2>&1
```

---

## Security Hardening

### Firewall Configuration

```bash
# Enable UFW firewall
sudo ufw enable

# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow MongoDB only from localhost (default)
# Do NOT open port 27017 to external connections

# Check status
sudo ufw status verbose
```

### Fail2Ban Setup

```bash
# Install Fail2Ban
sudo apt install -y fail2ban

# Create local configuration
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local

# Edit configuration
sudo nano /etc/fail2ban/jail.local

# Enable nginx protection
[nginx-http-auth]
enabled = true

[nginx-limit-req]
enabled = true

[nginx-botsearch]
enabled = true

# Restart Fail2Ban
sudo systemctl restart fail2ban
sudo systemctl status fail2ban
```

### Secure File Permissions

```bash
# Set ownership
sudo chown -R dmm:dmm /home/dmm/digital-mind

# Secure sensitive files
chmod 600 /home/dmm/digital-mind/dmm_backend/.env
chmod 600 /home/dmm/digital-mind/dmm_backend/logs/*.log

# Make scripts executable
chmod +x /home/dmm/digital-mind/dmm_backend/scripts/*.py
```

---

## Monitoring Setup

### System Monitoring

```bash
# Install monitoring tools
sudo apt install -y htop iotop nethogs

# Check system resources
htop          # CPU and memory
iotop         # Disk I/O
nethogs       # Network usage
```

### Application Logs

```bash
# View application logs
tail -f /home/dmm/digital-mind/dmm_backend/logs/app.log

# View error logs
tail -f /home/dmm/digital-mind/dmm_backend/logs/error.log

# View Nginx logs
sudo tail -f /var/log/nginx/dmm-backend-access.log
sudo tail -f /var/log/nginx/dmm-backend-error.log

# View systemd logs
sudo journalctl -u dmm-backend -f
```

### Health Checks

```bash
# Check API health
curl http://localhost:8000/api/health

# Check via Nginx
curl https://yourdomain.com/health

# Check with full response
curl -i https://yourdomain.com/health
```

---

## Post-Deployment Verification

### Verification Checklist

- [ ] API accessible via HTTPS
- [ ] SSL certificate valid
- [ ] Health check endpoint responding
- [ ] API documentation accessible (/docs)
- [ ] Authentication working
- [ ] Database connections working
- [ ] Logs being written
- [ ] Backups running
- [ ] Monitoring active
- [ ] Security headers present

### Test Commands

```bash
# 1. Health check
curl -I https://yourdomain.com/health

# 2. API documentation
curl https://yourdomain.com/docs

# 3. Test authentication
curl -X POST https://yourdomain.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "TestPass123!",
    "full_name": "Test User"
  }'

# 4. Test login
curl -X POST https://yourdomain.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "TestPass123!"
  }'

# 5. Check security headers
curl -I https://yourdomain.com/api/health | grep -E "(Strict-Transport|X-Frame|X-Content)"

# 6. Test database connection
mongosh "mongodb://dmm_user:PASSWORD@localhost:27017/digital_mind_model?authSource=admin" --eval "db.stats()"

# 7. Check service status
sudo systemctl status dmm-backend
sudo systemctl status nginx
sudo systemctl status mongod

# 8. Check logs for errors
sudo journalctl -u dmm-backend --since "1 hour ago" | grep -i error
```

### Performance Testing

```bash
# Install Apache Bench
sudo apt install -y apache2-utils

# Test endpoint performance
ab -n 1000 -c 10 https://yourdomain.com/health

# Expected results:
# - Requests per second: > 100
# - Time per request: < 100ms
# - Failed requests: 0
```

---

## Troubleshooting

### Issue 1: Service Won't Start

**Symptoms**: systemd service fails to start

**Diagnosis**:
```bash
sudo systemctl status dmm-backend
sudo journalctl -u dmm-backend -n 50
```

**Common Causes**:
- Missing or invalid .env file
- MongoDB not running
- Port already in use
- Permission issues

**Solutions**:
```bash
# Check MongoDB
sudo systemctl status mongod

# Check port availability
sudo lsof -i :8000

# Check file permissions
ls -la /home/dmm/digital-mind/dmm_backend/.env

# Test manually
cd /home/dmm/digital-mind/dmm_backend
source venv/bin/activate
./venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000
```

### Issue 2: 502 Bad Gateway

**Symptoms**: Nginx returns 502 error

**Diagnosis**:
```bash
sudo tail -f /var/log/nginx/dmm-backend-error.log
sudo systemctl status dmm-backend
```

**Common Causes**:
- Backend not running
- Backend listening on wrong host/port
- Firewall blocking connection

**Solutions**:
```bash
# Check backend status
sudo systemctl status dmm-backend

# Check backend is listening
sudo netstat -tlnp | grep 8000

# Restart services
sudo systemctl restart dmm-backend
sudo systemctl restart nginx
```

### Issue 3: SSL Certificate Issues

**Symptoms**: SSL errors, certificate warnings

**Diagnosis**:
```bash
sudo certbot certificates
openssl s_client -connect yourdomain.com:443 -servername yourdomain.com
```

**Solutions**:
```bash
# Renew certificate
sudo certbot renew

# Force renewal
sudo certbot renew --force-renewal

# Check Nginx SSL configuration
sudo nginx -t
```

### Issue 4: Database Connection Errors

**Symptoms**: Cannot connect to MongoDB

**Diagnosis**:
```bash
sudo systemctl status mongod
mongosh "mongodb://localhost:27017" --eval "db.serverStatus()"
```

**Solutions**:
```bash
# Start MongoDB
sudo systemctl start mongod

# Check MongoDB logs
sudo tail -f /var/log/mongodb/mongod.log

# Test connection
mongosh "mongodb://dmm_user:PASSWORD@localhost:27017/digital_mind_model?authSource=admin"
```

---

## Summary

This deployment guide provides comprehensive instructions for deploying the DMM Backend to production. Key points:

- ✅ **System Requirements**: Clearly defined hardware and software requirements
- ✅ **Installation**: Step-by-step installation process
- ✅ **Configuration**: Production-ready configuration templates
- ✅ **SSL/TLS**: Multiple options for secure connections
- ✅ **Process Management**: systemd and PM2 options
- ✅ **Reverse Proxy**: Nginx configuration with security headers
- ✅ **Security**: Comprehensive hardening guidelines
- ✅ **Monitoring**: Logging and health check setup
- ✅ **Verification**: Complete testing procedures
- ✅ **Troubleshooting**: Common issues and solutions

**Next Steps**:
- Review CONFIG.md for detailed configuration options
- Review DEPLOY_STEPS.md for step-by-step procedures
- Review ROLLBACK.md for rollback procedures

---

**Document Owner**: DevOps Team  
**Review Cycle**: Quarterly  
**Next Review**: 2025-02-04
