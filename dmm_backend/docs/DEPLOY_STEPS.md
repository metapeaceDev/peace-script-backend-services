# Deployment Steps Guide

**DMM Backend - Step-by-Step Deployment Procedures**

Version: 1.4.0  
Last Updated: 4 November 2568 (2025)  
Status: ✅ Production Ready

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Development Deployment](#development-deployment)
4. [Staging Deployment](#staging-deployment)
5. [Production Deployment](#production-deployment)
6. [Zero-Downtime Deployment](#zero-downtime-deployment)
7. [Post-Deployment Steps](#post-deployment-steps)
8. [Verification Procedures](#verification-procedures)

---

## Overview

This guide provides detailed, step-by-step procedures for deploying the DMM Backend to different environments. Each environment has specific requirements and verification steps.

### Deployment Environments

| Environment | Purpose | URL | Deployment Frequency |
|-------------|---------|-----|----------------------|
| **Development** | Local development and testing | localhost:8000 | On-demand |
| **Staging** | Pre-production testing | staging.yourdomain.com | Weekly |
| **Production** | Live production system | yourdomain.com | Bi-weekly/Monthly |

### Deployment Timeline

```
Development → Staging → Production
     ↓            ↓          ↓
  On-demand   1-2 days   3-7 days
  (instant)   (testing)  (validation)
```

---

## Prerequisites

### Required Before Any Deployment

- [ ] Code reviewed and approved
- [ ] Tests passing (all automated tests)
- [ ] Documentation updated
- [ ] Configuration prepared for target environment
- [ ] Backup taken (production only)
- [ ] Rollback plan documented
- [ ] Team notified (staging/production)

### Required Tools

- [ ] SSH access to target server
- [ ] Git (v2.30+)
- [ ] Python 3.9+
- [ ] MongoDB access credentials
- [ ] Sudo/admin access (for system services)

### Required Files

- [ ] `.env` file for target environment
- [ ] SSL certificates (staging/production)
- [ ] Database credentials
- [ ] API keys and secrets

---

## Development Deployment

### Overview

Local development deployment for testing and development.

**Duration**: 5-10 minutes  
**Downtime**: N/A (local environment)  
**Risk Level**: ⚫ None

---

### Step 1: Clone or Update Repository

```bash
# If first time
cd ~/projects
git clone https://github.com/PeaceScript/digital-mind.git
cd digital-mind

# If updating
cd ~/projects/digital-mind
git fetch origin
git checkout develop  # or your dev branch
git pull origin develop
```

**Verification**:
```bash
git status
git log -1  # Check latest commit
```

---

### Step 2: Setup Python Environment

```bash
# Navigate to backend
cd dmm_backend

# Create virtual environment (first time only)
python3.9 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install/Update dependencies
pip install -r requirements.txt
```

**Verification**:
```bash
which python  # Should show venv path
pip list | grep fastapi
pip list | grep motor
```

---

### Step 3: Configure Environment

```bash
# Create .env file from example
cp .env.example .env

# Edit configuration
nano .env
```

**Minimal Development `.env`**:
```bash
API_KEY="dev-api-key"
MONGO_URI="mongodb://localhost:27017/digital_mind_model_dev"
JWT_SECRET_KEY="dev-jwt-secret"
DEBUG_MODE=true
LOG_LEVEL="DEBUG"
```

**Verification**:
```bash
cat .env | grep -v "^#" | grep -v "^$"  # Show non-empty, non-comment lines
```

---

### Step 4: Start MongoDB

```bash
# macOS
brew services start mongodb-community

# Linux
sudo systemctl start mongod

# Verify
mongosh --eval "db.serverStatus()" | grep "ok"
```

**Verification**:
```bash
# Should return "ok" : 1
mongosh --eval "db.adminCommand('ping')"
```

---

### Step 5: Start Backend Server

```bash
# Method 1: Direct Uvicorn (recommended for development)
uvicorn main:app --reload --host 127.0.0.1 --port 8000

# Method 2: VS Code Task
# Press Cmd+Shift+P → "Tasks: Run Task" → "Run backend (local venv)"

# Method 3: Make command (if Makefile exists)
make dev
```

**Verification**:
```bash
# In another terminal
curl http://localhost:8000/api/health

# Expected output:
# {"status":"healthy","timestamp":"..."}
```

---

### Step 6: Verify Installation

```bash
# 1. Check API health
curl http://localhost:8000/api/health

# 2. Check API docs
open http://localhost:8000/docs  # macOS
# or visit in browser

# 3. Test authentication
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testdev",
    "email": "testdev@example.com",
    "password": "Test123!",
    "full_name": "Test Developer"
  }'

# 4. Check logs
tail -f logs/app.log  # if logging to file
```

---

## Staging Deployment

### Overview

Staging deployment for pre-production testing and validation.

**Duration**: 15-20 minutes  
**Downtime**: 1-2 minutes  
**Risk Level**: 🟡 Low

---

### Pre-Deployment Checklist

- [ ] All tests passing in CI/CD
- [ ] Code reviewed and merged to staging branch
- [ ] Database backup taken
- [ ] Team notified of deployment
- [ ] Staging server accessible via SSH

---

### Step 1: Connect to Staging Server

```bash
# SSH to staging server
ssh dmm@staging.yourdomain.com

# Or with key
ssh -i ~/.ssh/dmm-staging.pem dmm@staging.yourdomain.com

# Verify correct server
hostname
echo $HOSTNAME  # Should show staging server name
```

**Verification**:
```bash
whoami  # Should be 'dmm' user
pwd     # Should be /home/dmm or similar
```

---

### Step 2: Navigate to Application Directory

```bash
cd /home/dmm/digital-mind

# Verify current version
git branch --show-current
git log -1 --oneline
```

---

### Step 3: Backup Current State

```bash
# Create backup tag
git tag "backup-$(date +%Y%m%d-%H%M%S)"

# Create database backup
cd dmm_backend
MONGODB_URI=$MONGO_URI ./venv/bin/python scripts/backup_database.py

# Verify backup created
ls -lh backups/ | tail -1
```

**Verification**:
```bash
# Check backup file exists and has reasonable size
LATEST_BACKUP=$(ls -t backups/dmm_backup_*.tar.gz | head -1)
if [ -f "$LATEST_BACKUP" ]; then
    echo "✅ Backup created: $LATEST_BACKUP"
    ls -lh "$LATEST_BACKUP"
else
    echo "❌ Backup failed!"
    exit 1
fi
```

---

### Step 4: Pull Latest Code

```bash
# Fetch latest changes
git fetch origin

# Checkout staging branch
git checkout staging

# Pull latest code
git pull origin staging

# Verify version
git log -1 --oneline
```

**Verification**:
```bash
# Check no uncommitted changes
git status

# Verify on correct branch
git branch --show-current  # Should show 'staging'
```

---

### Step 5: Update Dependencies

```bash
cd dmm_backend

# Activate virtual environment
source venv/bin/activate

# Update dependencies
pip install -r requirements.txt --upgrade

# Verify critical packages
pip list | grep -E "(fastapi|motor|uvicorn)"
```

**Verification**:
```bash
# Check for dependency conflicts
pip check

# Should output: "No broken requirements found."
```

---

### Step 6: Run Database Migrations (if any)

```bash
# If you have migration scripts
python scripts/migrate_db.py

# Or run seed if needed
python -m seed_db

# Verify database collections
mongosh "$MONGO_URI" --eval "db.getCollectionNames()"
```

---

### Step 7: Update Environment Configuration

```bash
# Backup current .env
cp .env .env.backup.$(date +%Y%m%d-%H%M%S)

# Review changes needed
nano .env

# Verify critical variables
grep -E "(API_KEY|JWT_SECRET_KEY|MONGO_URI)" .env
```

**⚠️ Important**: Never overwrite .env completely - only update changed values

---

### Step 8: Restart Application

```bash
# If using systemd
sudo systemctl restart dmm-backend
sudo systemctl status dmm-backend

# If using PM2
pm2 restart dmm-backend
pm2 status

# Watch logs for errors
sudo journalctl -u dmm-backend -f  # systemd
pm2 logs dmm-backend              # PM2
```

**Verification**:
```bash
# Wait 10 seconds for startup
sleep 10

# Check service is running
sudo systemctl is-active dmm-backend  # Should return 'active'

# Check no error logs
sudo journalctl -u dmm-backend --since "1 minute ago" | grep -i error
```

---

### Step 9: Verify Deployment

```bash
# 1. Health check
curl https://staging.yourdomain.com/health

# 2. API version
curl https://staging.yourdomain.com/api/ | jq .version

# 3. Test authentication
curl -X POST https://staging.yourdomain.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"existing_user","password":"password"}'

# 4. Check response time
time curl https://staging.yourdomain.com/health
# Should be < 200ms
```

---

### Step 10: Smoke Testing

```bash
# Run automated smoke tests
cd dmm_backend
pytest tests/test_smoke.py -v

# Or manual smoke tests
# - Register new user
# - Login
# - Create resource
# - Retrieve resource
# - Delete resource
```

---

### Step 11: Monitor for Issues

```bash
# Monitor logs for 5 minutes
sudo journalctl -u dmm-backend -f

# Check for:
# - No error messages
# - Normal request patterns
# - No database errors
# - No authentication failures

# Check system resources
htop  # CPU/Memory
df -h  # Disk space
```

---

### Step 12: Notify Team

```bash
# Send deployment notification
# - Slack/Discord: "Staging deployed - version X.Y.Z"
# - Email: "Staging deployment complete"
# - Update deployment log

# Example Slack message:
# ✅ Staging Deployment Complete
# Version: 1.4.0
# Commit: abc123f
# Time: 2025-11-04 20:30 GMT+7
# Status: All checks passed
```

---

## Production Deployment

### Overview

Production deployment with zero-downtime strategy.

**Duration**: 25-35 minutes  
**Downtime**: 0 minutes (rolling deployment)  
**Risk Level**: 🔴 High (requires approval)

---

### Pre-Deployment Checklist

- [ ] Staging deployment successful and tested (minimum 24 hours)
- [ ] All automated tests passing
- [ ] Manual testing completed
- [ ] Performance testing passed
- [ ] Security audit completed (for major releases)
- [ ] Database backup verified
- [ ] Rollback plan documented and tested
- [ ] Change request approved (CAB/manager)
- [ ] Team on standby for deployment
- [ ] Maintenance window scheduled (if downtime expected)
- [ ] Monitoring alerts configured
- [ ] Customer notification sent (for major changes)

---

### Step 1: Pre-Deployment Meeting

**15 minutes before deployment**:

- [ ] All team members present
- [ ] Deployment checklist reviewed
- [ ] Rollback procedure confirmed
- [ ] Communication channels open
- [ ] Monitoring dashboards open

---

### Step 2: Enable Maintenance Mode (Optional)

```bash
# If expecting any downtime, enable maintenance mode
# Update Nginx to show maintenance page
sudo nano /etc/nginx/sites-available/dmm-backend

# Add at top of server block:
# return 503;
# Or redirect to maintenance page

# Reload Nginx
sudo nginx -t
sudo systemctl reload nginx
```

---

### Step 3: Create Production Backup

```bash
# SSH to production server
ssh dmm@yourdomain.com

cd /home/dmm/digital-mind/dmm_backend

# Create full database backup
MONGODB_URI=$MONGO_URI ./venv/bin/python scripts/backup_database.py

# Verify backup
LATEST_BACKUP=$(ls -t backups/dmm_backup_*.tar.gz | head -1)
ls -lh "$LATEST_BACKUP"

# Test backup integrity
MONGODB_URI=$MONGO_URI ./venv/bin/python scripts/restore_database.py \
  --backup "$LATEST_BACKUP" \
  --skip-safety  # Don't create another backup
  # Type 'no' when prompted - we're just testing

# Backup code (create tag)
git tag "production-$(date +%Y%m%d-%H%M%S)"
git push --tags
```

**Verification**:
```bash
# Verify backup file size (should be > 0)
BACKUP_SIZE=$(stat -f%z "$LATEST_BACKUP" 2>/dev/null || stat -c%s "$LATEST_BACKUP")
if [ "$BACKUP_SIZE" -gt 1000000 ]; then  # > 1MB
    echo "✅ Backup size OK: $BACKUP_SIZE bytes"
else
    echo "❌ Backup too small!"
    exit 1
fi
```

---

### Step 4: Deploy New Version

```bash
# Pull latest code
git fetch origin
git checkout main  # or production branch
git pull origin main

# Verify commit
git log -1 --oneline
git show --stat

# Check for breaking changes
git diff HEAD~1 HEAD --name-status
```

---

### Step 5: Update Dependencies

```bash
cd dmm_backend
source venv/bin/activate

# Update dependencies
pip install -r requirements.txt --upgrade

# Verify no conflicts
pip check
```

---

### Step 6: Run Database Migrations

```bash
# If you have migrations
python scripts/migrate_db.py --dry-run  # Test first
python scripts/migrate_db.py            # Then run

# Verify migrations
mongosh "$MONGO_URI" --eval "db.migrations.find().pretty()"
```

---

### Step 7: Rolling Restart (Zero-Downtime)

**If using multiple workers/instances**:

```bash
# Restart workers one at a time
for i in {1..4}; do
    echo "Restarting worker $i..."
    pm2 restart dmm-backend-$i
    sleep 30  # Wait for startup
    
    # Verify worker health
    curl http://localhost:8000/health || echo "❌ Worker $i unhealthy!"
done

# Or with systemd instances
for i in {1..4}; do
    sudo systemctl restart dmm-backend@$i
    sleep 30
    sudo systemctl is-active dmm-backend@$i
done
```

**If using single instance**:

```bash
# Quick restart (1-2 seconds downtime)
sudo systemctl restart dmm-backend

# Verify
sleep 10
sudo systemctl status dmm-backend
curl http://localhost:8000/health
```

---

### Step 8: Disable Maintenance Mode

```bash
# Remove maintenance mode from Nginx
sudo nano /etc/nginx/sites-available/dmm-backend
# Remove: return 503; line

# Reload Nginx
sudo nginx -t
sudo systemctl reload nginx

# Verify
curl -I https://yourdomain.com/health
```

---

### Step 9: Comprehensive Verification

```bash
# 1. Health checks
curl https://yourdomain.com/health

# 2. API endpoints
curl https://yourdomain.com/api/

# 3. Authentication
curl -X POST https://yourdomain.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test"}'

# 4. Database connectivity
mongosh "$MONGO_URI" --eval "db.stats()"

# 5. Response times
for i in {1..10}; do
    time curl -s https://yourdomain.com/health > /dev/null
done

# 6. Error logs
sudo journalctl -u dmm-backend --since "5 minutes ago" | grep -i error

# 7. Resource usage
htop
df -h

# 8. SSL certificate
echo | openssl s_client -connect yourdomain.com:443 2>/dev/null | \
  openssl x509 -noout -dates
```

---

### Step 10: Run Production Smoke Tests

```bash
# Automated smoke tests
cd dmm_backend
pytest tests/test_production_smoke.py -v

# Manual testing checklist:
# - [ ] Homepage loads
# - [ ] User can login
# - [ ] User can register
# - [ ] Create operation works
# - [ ] Read operation works
# - [ ] Update operation works
# - [ ] Delete operation works
# - [ ] Search functionality works
# - [ ] File upload works (if applicable)
# - [ ] Payment gateway works (if applicable)
```

---

### Step 11: Monitor for 30 Minutes

```bash
# Watch logs
sudo journalctl -u dmm-backend -f

# Monitor system resources
htop

# Watch for errors
watch -n 5 'sudo journalctl -u dmm-backend --since "1 minute ago" | grep -i error | wc -l'

# Monitor response times
watch -n 10 'curl -w "%{time_total}\n" -o /dev/null -s https://yourdomain.com/health'

# Check monitoring dashboard
# - Application errors
# - Response times
# - Database queries
# - Server resources
```

**Success Criteria**:
- No errors in logs
- Response times normal
- All endpoints working
- No customer complaints
- Resources within normal range

---

### Step 12: Post-Deployment Verification

```bash
# Run full test suite against production (read-only tests)
pytest tests/test_production_readonly.py -v

# Performance test
ab -n 100 -c 10 https://yourdomain.com/health

# Load test (if appropriate)
locust -f locustfile.py --host https://yourdomain.com

# Check database integrity
mongosh "$MONGO_URI" --eval "
  db.users.countDocuments({});
  db.models.countDocuments({});
  db.timelines.countDocuments({});
"
```

---

### Step 13: Post-Deployment Notification

**Send deployment completion notification**:

```
✅ Production Deployment Complete

Version: 1.4.0
Commit: abc123f
Deployed: 2025-11-04 21:00 GMT+7
Duration: 25 minutes
Downtime: 0 minutes

Verification:
✅ All health checks passing
✅ Smoke tests passed
✅ No errors in logs
✅ Response times normal (< 100ms)
✅ Database connectivity OK
✅ SSL certificate valid

Team: Available for monitoring

Next steps:
- Continue monitoring for 2 hours
- Customer support team notified
- Rollback ready if needed
```

---

### Step 14: Update Documentation

```bash
# Update deployment log
echo "$(date): Production deployment 1.4.0 - SUCCESS" >> deployment_log.txt

# Update version in docs
# Update CHANGELOG.md
# Update any affected documentation
```

---

## Zero-Downtime Deployment

### Overview

Advanced deployment strategy with zero downtime using Blue-Green or Rolling deployment.

---

### Blue-Green Deployment

**Architecture**:
```
         Load Balancer
              |
      +-------+-------+
      |               |
   Blue (old)     Green (new)
   Port 8000      Port 8001
```

**Steps**:

1. **Deploy to Green**:
```bash
# Start new version on port 8001
PORT=8001 uvicorn main:app --host 127.0.0.1 --port 8001 &

# Wait for startup
sleep 10

# Verify green
curl http://localhost:8001/health
```

2. **Switch Traffic**:
```bash
# Update Nginx upstream
sudo nano /etc/nginx/sites-available/dmm-backend

# Change:
# upstream dmm_backend {
#     server 127.0.0.1:8001;  # Changed from 8000
# }

sudo nginx -t
sudo systemctl reload nginx
```

3. **Verify Switch**:
```bash
# Check traffic going to green
curl https://yourdomain.com/health

# Monitor old blue instance
# No new requests should arrive
```

4. **Stop Blue**:
```bash
# After verification (15-30 minutes)
systemctl stop dmm-backend  # Old instance
```

---

### Rolling Deployment

**For multiple instances**:

```bash
# Deploy to instances one by one
for instance in 1 2 3 4; do
    echo "Deploying to instance $instance..."
    
    # Remove from load balancer
    # Deploy new version
    # Add back to load balancer
    # Verify health
    # Wait before next
    
    sleep 60
done
```

---

## Post-Deployment Steps

### Immediate Actions (Within 1 Hour)

- [ ] Monitor application logs
- [ ] Monitor system resources
- [ ] Monitor error rates
- [ ] Check response times
- [ ] Verify critical workflows
- [ ] Monitor customer support tickets

### Short-term Actions (Within 24 Hours)

- [ ] Review deployment metrics
- [ ] Analyze performance data
- [ ] Check backup completion
- [ ] Update monitoring baselines
- [ ] Document any issues encountered
- [ ] Update runbooks if needed

### Long-term Actions (Within 1 Week)

- [ ] Conduct post-deployment review
- [ ] Update deployment procedures
- [ ] Share lessons learned
- [ ] Plan next deployment
- [ ] Archive deployment artifacts

---

## Verification Procedures

### Automated Verification Script

Create `scripts/verify_deployment.sh`:

```bash
#!/bin/bash
# Deployment verification script

set -e

HOST="${1:-https://yourdomain.com}"
ERRORS=0

echo "🔍 Verifying deployment to $HOST"
echo "================================"

# 1. Health check
echo -n "1. Health check... "
if curl -sf "$HOST/health" > /dev/null; then
    echo "✅"
else
    echo "❌"
    ((ERRORS++))
fi

# 2. API availability
echo -n "2. API availability... "
if curl -sf "$HOST/api/" > /dev/null; then
    echo "✅"
else
    echo "❌"
    ((ERRORS++))
fi

# 3. Response time
echo -n "3. Response time... "
RESPONSE_TIME=$(curl -w "%{time_total}" -o /dev/null -s "$HOST/health")
if (( $(echo "$RESPONSE_TIME < 0.5" | bc -l) )); then
    echo "✅ (${RESPONSE_TIME}s)"
else
    echo "⚠️  Slow (${RESPONSE_TIME}s)"
fi

# 4. SSL certificate
echo -n "4. SSL certificate... "
if echo | openssl s_client -connect ${HOST#https://}:443 2>/dev/null | \
   openssl x509 -noout -checkend 86400 > /dev/null; then
    echo "✅"
else
    echo "❌"
    ((ERRORS++))
fi

# 5. Security headers
echo -n "5. Security headers... "
if curl -sI "$HOST/health" | grep -q "Strict-Transport-Security"; then
    echo "✅"
else
    echo "❌"
    ((ERRORS++))
fi

echo "================================"
if [ $ERRORS -eq 0 ]; then
    echo "✅ All checks passed!"
    exit 0
else
    echo "❌ $ERRORS check(s) failed!"
    exit 1
fi
```

**Usage**:
```bash
chmod +x scripts/verify_deployment.sh

# Verify staging
./scripts/verify_deployment.sh https://staging.yourdomain.com

# Verify production
./scripts/verify_deployment.sh https://yourdomain.com
```

---

## Summary

This deployment guide provides step-by-step procedures for deploying to different environments:

- ✅ **Development**: Quick local setup (5-10 min)
- ✅ **Staging**: Pre-production deployment (15-20 min)  
- ✅ **Production**: Zero-downtime deployment (25-35 min)
- ✅ **Verification**: Automated and manual checks
- ✅ **Post-Deployment**: Monitoring and documentation

### Key Principles

1. **Always backup before deployment**
2. **Test in staging first**
3. **Verify each step**
4. **Monitor after deployment**
5. **Document everything**
6. **Have rollback ready**

### Quick Reference

**Development**:
```bash
git pull → pip install -r requirements.txt → uvicorn main:app --reload
```

**Staging**:
```bash
backup → git pull → pip install → restart service → verify
```

**Production**:
```bash
approve → backup → test backup → deploy → rolling restart → verify → monitor
```

---

**Document Owner**: DevOps Team  
**Review Cycle**: After each deployment  
**Next Review**: After next production deployment
