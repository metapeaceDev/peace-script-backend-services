# Rollback Procedures

**DMM Backend - Deployment Rollback Guide**

Version: 1.4.0  
Last Updated: 4 November 2568 (2025)  
Status: ✅ Production Ready

---

## Table of Contents

1. [Overview](#overview)
2. [When to Rollback](#when-to-rollback)
3. [Rollback Decision Matrix](#rollback-decision-matrix)
4. [Quick Rollback (Emergency)](#quick-rollback-emergency)
5. [Standard Rollback](#standard-rollback)
6. [Database Rollback](#database-rollback)
7. [Partial Rollback](#partial-rollback)
8. [Post-Rollback Procedures](#post-rollback-procedures)
9. [Rollback Testing](#rollback-testing)

---

## Overview

This document provides comprehensive procedures for rolling back failed or problematic deployments. Rollback procedures are designed to restore service quickly and safely.

### Rollback Principles

1. **Safety First**: Preserve data integrity above all
2. **Speed**: Restore service as quickly as possible
3. **Communication**: Keep stakeholders informed
4. **Documentation**: Record all actions taken
5. **Root Cause**: Identify and fix the underlying issue

### Rollback Types

| Type | Duration | Risk | Use Case |
|------|----------|------|----------|
| **Quick Rollback** | 2-5 min | Low | Code-only changes, no DB changes |
| **Standard Rollback** | 10-15 min | Medium | Standard deployments with testing |
| **Database Rollback** | 20-30 min | High | Deployments with schema changes |
| **Partial Rollback** | 5-10 min | Medium | Rollback specific components only |

---

## When to Rollback

### Critical Issues (Immediate Rollback)

⚠️ **Rollback immediately** if you observe:

- **Service Down**: API returns 5xx errors consistently (> 10% of requests)
- **Data Loss**: Evidence of data corruption or deletion
- **Security Breach**: Security vulnerability exposed
- **Critical Bug**: Breaks core functionality (login, payments, etc.)
- **Performance Degradation**: Response times > 10x normal
- **Database Errors**: Persistent database connection failures

**Decision Time**: < 5 minutes  
**Action**: Execute Quick Rollback

---

### Major Issues (Rollback Soon)

⚠️ **Rollback within 30 minutes** if:

- **High Error Rate**: Error rate > 5% of requests
- **Feature Broken**: Major feature not working as expected
- **Performance Issues**: Response times 2-5x slower than normal
- **Resource Exhaustion**: CPU/Memory usage > 90%
- **Customer Complaints**: Multiple customer reports of issues

**Decision Time**: 15-30 minutes  
**Action**: Execute Standard Rollback

---

### Minor Issues (Fix Forward or Rollback)

🔄 **Consider fix-forward OR rollback** if:

- **Minor Bug**: Non-critical feature affected
- **UI Issue**: Cosmetic or minor usability problem
- **Low Error Rate**: Error rate 1-5%
- **Known Workaround**: Users can work around the issue

**Decision Time**: 1-2 hours  
**Action**: Assess whether to fix forward or rollback

---

### No Rollback Needed

✅ **Continue monitoring** if:

- **All Tests Pass**: Automated and manual tests successful
- **Performance Normal**: Response times within acceptable range
- **No Errors**: Error rate < 1%
- **User Feedback Positive**: No customer complaints

**Action**: Continue standard post-deployment monitoring

---

## Rollback Decision Matrix

```
┌─────────────────────────────────────────────────────┐
│          Rollback Decision Tree                     │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
              Is service DOWN?
                 (5xx errors)
                 /         \
              YES           NO
               │             │
               ▼             ▼
         Quick Rollback   Is error rate > 10%?
         (2-5 min)          /          \
                         YES            NO
                          │              │
                          ▼              ▼
                    Quick Rollback   Is feature broken?
                    (2-5 min)          /          \
                                    YES            NO
                                     │              │
                                     ▼              ▼
                              Standard Rollback   Monitor
                              (10-15 min)         Continue
```

---

## Quick Rollback (Emergency)

### Overview

**Duration**: 2-5 minutes  
**Downtime**: 30-60 seconds  
**Use Case**: Critical production issues, service down

---

### Prerequisites

- [ ] Backup tag exists (`git tag backup-YYYYMMDD-HHMMSS`)
- [ ] Previous version was working
- [ ] No database schema changes in new version

---

### Step 1: Declare Emergency

```bash
# Notify team immediately
echo "🚨 EMERGENCY ROLLBACK INITIATED" | notify-team

# Document start time
echo "$(date): Emergency rollback started" >> /var/log/dmm/rollback.log
```

---

### Step 2: Revert Code (30 seconds)

```bash
# SSH to production server
ssh dmm@yourdomain.com

cd /home/dmm/digital-mind

# Find latest backup tag
git tag | grep backup | tail -1

# Revert to last backup
git reset --hard backup-YYYYMMDD-HHMMSS

# Or revert to previous commit
git reset --hard HEAD~1

# Verify
git log -1 --oneline
```

---

### Step 3: Restart Service (30 seconds)

```bash
cd dmm_backend

# Quick restart
sudo systemctl restart dmm-backend

# Verify immediately
sleep 5
curl http://localhost:8000/health
```

---

### Step 4: Verify Service (1 minute)

```bash
# Check service status
sudo systemctl status dmm-backend

# Check health endpoint
curl https://yourdomain.com/health

# Check logs for errors
sudo journalctl -u dmm-backend --since "1 minute ago" | grep -i error

# Test critical endpoint
curl -X POST https://yourdomain.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test"}'
```

---

### Step 5: Notify Team

```bash
# Send notification
echo "✅ Emergency rollback complete - service restored" | notify-team

# Update status page
# Update incident log
```

---

## Standard Rollback

### Overview

**Duration**: 10-15 minutes  
**Downtime**: 1-2 minutes  
**Use Case**: Standard deployments with issues

---

### Step 1: Prepare for Rollback

```bash
# Document issue
echo "Issue: $(description)" >> /var/log/dmm/rollback.log
echo "Time: $(date)" >> /var/log/dmm/rollback.log

# Notify team
echo "🔄 Standard rollback initiated" | notify-team

# Enable maintenance mode (optional)
# sudo systemctl stop dmm-backend
# Or configure Nginx maintenance page
```

---

### Step 2: Backup Current State

```bash
cd /home/dmm/digital-mind

# Create tag of failed deployment
git tag "failed-deployment-$(date +%Y%m%d-%H%M%S)"

# Backup current .env (might have changed)
cp dmm_backend/.env dmm_backend/.env.failed.$(date +%Y%m%d-%H%M%S)

# Backup logs
cp dmm_backend/logs/app.log dmm_backend/logs/app.log.failed.$(date +%Y%m%d-%H%M%S)
```

---

### Step 3: Revert Code

```bash
# Find last known good version
git tag | grep backup | tail -1

# Revert to last backup
git reset --hard backup-YYYYMMDD-HHMMSS

# Verify version
git log -1 --oneline
git show --stat
```

---

### Step 4: Restore Configuration

```bash
cd dmm_backend

# Restore previous .env if it changed
# Usually don't restore .env unless you know it changed
# cp .env.backup.YYYYMMDD-HHMMSS .env

# Verify configuration
grep -E "(API_KEY|JWT_SECRET_KEY|MONGO_URI)" .env
```

---

### Step 5: Restore Dependencies

```bash
# Activate venv
source venv/bin/activate

# Reinstall requirements from old version
pip install -r requirements.txt

# Verify
pip list | grep -E "(fastapi|motor|uvicorn)"
```

---

### Step 6: Restart Application

```bash
# Restart service
sudo systemctl restart dmm-backend

# Wait for startup
sleep 15

# Check status
sudo systemctl status dmm-backend
```

---

### Step 7: Comprehensive Verification

```bash
# 1. Health check
curl https://yourdomain.com/health

# 2. API endpoints
curl https://yourdomain.com/api/

# 3. Authentication
curl -X POST https://yourdomain.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test"}'

# 4. Database connectivity
mongosh "$MONGO_URI" --eval "db.stats()"

# 5. Critical workflows
# Test login, registration, main features

# 6. Response times
for i in {1..10}; do
    time curl -s https://yourdomain.com/health > /dev/null
done

# 7. Error logs
sudo journalctl -u dmm-backend --since "5 minutes ago" | grep -i error

# 8. System resources
htop
df -h
```

---

### Step 8: Disable Maintenance Mode

```bash
# If maintenance mode was enabled
# Start service
sudo systemctl start dmm-backend

# Or update Nginx
sudo systemctl reload nginx
```

---

### Step 9: Monitor for 30 Minutes

```bash
# Watch logs
sudo journalctl -u dmm-backend -f

# Monitor errors
watch -n 5 'sudo journalctl -u dmm-backend --since "1 minute ago" | grep -i error | wc -l'

# Monitor response times
watch -n 10 'curl -w "%{time_total}\n" -o /dev/null -s https://yourdomain.com/health'
```

---

## Database Rollback

### Overview

**Duration**: 20-30 minutes  
**Downtime**: 5-10 minutes  
**Risk**: 🔴 High  
**Use Case**: Deployments with database schema changes

---

### ⚠️ Warning

Database rollbacks are high-risk operations. Consider:
- **Data Loss**: Rolling back database may lose data created after deployment
- **Downtime**: Database restore requires service downtime
- **Complexity**: Requires careful coordination

**Alternative**: Consider fixing forward when possible

---

### Step 1: Assess Database Changes

```bash
# Check what changed in database
mongosh "$MONGO_URI" --eval "db.getCollectionNames()"

# Check if collections were added/removed
# Check if indexes were changed
# Check if data was migrated
```

---

### Step 2: Stop Application

```bash
# MUST stop application before database restore
sudo systemctl stop dmm-backend

# Verify stopped
sudo systemctl status dmm-backend
```

---

### Step 3: Backup Current Database

```bash
cd /home/dmm/digital-mind/dmm_backend

# Create safety backup of current state
MONGODB_URI=$MONGO_URI ./venv/bin/python scripts/backup_database.py

# Verify backup created
ls -lh backups/ | tail -1
```

---

### Step 4: Restore Previous Database

```bash
# Find pre-deployment backup
ls -lt backups/dmm_backup_*.tar.gz

# Restore from backup (before deployment)
MONGODB_URI=$MONGO_URI ./venv/bin/python scripts/restore_database.py \
  --backup backups/dmm_backup_YYYYMMDD_HHMMSS.tar.gz \
  --drop \
  --yes

# Wait for restore to complete
# Monitor output for errors
```

---

### Step 5: Verify Database

```bash
# Connect to database
mongosh "$MONGO_URI"

# Verify collections
db.getCollectionNames()

# Count documents
db.users.countDocuments({})
db.models.countDocuments({})

# Verify indexes
db.users.getIndexes()

# Exit
exit
```

---

### Step 6: Revert Code

```bash
cd /home/dmm/digital-mind

# Revert to version compatible with restored database
git reset --hard backup-YYYYMMDD-HHMMSS

cd dmm_backend
source venv/bin/activate
pip install -r requirements.txt
```

---

### Step 7: Start Application

```bash
# Start service
sudo systemctl start dmm-backend

# Wait for startup
sleep 15

# Check status
sudo systemctl status dmm-backend
```

---

### Step 8: Verify Application

```bash
# Full verification suite
curl https://yourdomain.com/health
curl https://yourdomain.com/api/

# Test database operations
curl -X POST https://yourdomain.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "rollback_test",
    "email": "rollback@test.com",
    "password": "Test123!",
    "full_name": "Rollback Test"
  }'

# Clean up test user
mongosh "$MONGO_URI" --eval 'db.users.deleteOne({username:"rollback_test"})'
```

---

## Partial Rollback

### Overview

**Duration**: 5-10 minutes  
**Use Case**: Rollback specific components without full rollback

---

### Rollback Specific Feature

```bash
# If deployment added new routes/features
# Use feature flags or configuration to disable

# Edit .env
nano .env

# Disable feature
FEATURE_NEW_API=false

# Restart
sudo systemctl restart dmm-backend
```

---

### Rollback Configuration Only

```bash
# If issue is in configuration

# Restore previous .env
cp .env.backup.YYYYMMDD-HHMMSS .env

# Restart
sudo systemctl restart dmm-backend

# Verify
curl https://yourdomain.com/health
```

---

### Rollback Dependencies Only

```bash
# If issue is in upgraded package

cd dmm_backend
source venv/bin/activate

# Downgrade specific package
pip install package_name==old_version

# Restart
sudo systemctl restart dmm-backend
```

---

## Post-Rollback Procedures

### Immediate Actions

- [ ] Verify service fully operational
- [ ] Monitor for 1 hour minimum
- [ ] Document rollback details
- [ ] Notify team and stakeholders
- [ ] Update status page (if applicable)

### Short-term Actions (Within 24 Hours)

- [ ] Conduct post-mortem meeting
- [ ] Identify root cause
- [ ] Document lessons learned
- [ ] Create fix plan
- [ ] Update deployment procedures
- [ ] Add preventive measures

### Documentation Template

```markdown
# Rollback Report

**Date**: YYYY-MM-DD HH:MM
**Environment**: Production/Staging
**Rollback Type**: Quick/Standard/Database
**Duration**: X minutes
**Downtime**: X minutes

## Issue Description
[What went wrong]

## Impact
- Users affected: X
- Functionality impacted: [list]
- Data loss: Yes/No

## Rollback Actions Taken
1. [Step 1]
2. [Step 2]
...

## Verification Results
- [ ] Health check passing
- [ ] All tests passing
- [ ] No errors in logs
- [ ] Performance normal

## Root Cause
[Why it happened]

## Prevention Measures
[How to prevent in future]

## Follow-up Actions
- [ ] Fix issue in development
- [ ] Add test coverage
- [ ] Update deployment checklist
- [ ] Redeploy with fix

**Reported by**: [Name]
**Verified by**: [Name]
```

---

## Rollback Testing

### Test Rollback Procedure (Staging)

**Frequency**: Before each production deployment

```bash
# 1. Deploy new version to staging
# 2. Perform rollback
# 3. Verify rollback successful
# 4. Document any issues
```

### Rollback Drill

**Frequency**: Quarterly

**Purpose**: Ensure team familiarity with rollback procedures

**Steps**:
1. Schedule drill (non-production hours)
2. Simulate deployment failure
3. Execute rollback procedure
4. Time the rollback
5. Document observations
6. Improve procedures

---

## Rollback Scripts

### Automated Rollback Script

Create `scripts/rollback.sh`:

```bash
#!/bin/bash
# Automated rollback script

set -e

BACKUP_TAG="${1:-$(git tag | grep backup | tail -1)}"

if [ -z "$BACKUP_TAG" ]; then
    echo "❌ No backup tag found!"
    exit 1
fi

echo "🔄 Rolling back to: $BACKUP_TAG"
echo "================================"

# 1. Create failed deployment tag
git tag "failed-deployment-$(date +%Y%m%d-%H%M%S)"

# 2. Revert code
git reset --hard "$BACKUP_TAG"

# 3. Restart service
cd dmm_backend
sudo systemctl restart dmm-backend

# 4. Wait for startup
sleep 15

# 5. Verify
curl -f http://localhost:8000/health || {
    echo "❌ Rollback verification failed!"
    exit 1
}

echo "================================"
echo "✅ Rollback complete!"
echo "Restored to: $BACKUP_TAG"
```

**Usage**:
```bash
chmod +x scripts/rollback.sh

# Rollback to latest backup
./scripts/rollback.sh

# Rollback to specific tag
./scripts/rollback.sh backup-20251104-210000
```

---

### Database Rollback Script

Create `scripts/rollback_database.sh`:

```bash
#!/bin/bash
# Database rollback script

set -e

BACKUP_FILE="${1}"

if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ Backup file not found: $BACKUP_FILE"
    exit 1
fi

echo "🔄 Rolling back database from: $BACKUP_FILE"
echo "⚠️  This will STOP the application and RESTORE the database!"
read -p "Type 'yes' to continue: " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "❌ Rollback cancelled"
    exit 1
fi

# 1. Stop application
echo "Stopping application..."
sudo systemctl stop dmm-backend

# 2. Restore database
echo "Restoring database..."
cd dmm_backend
MONGODB_URI=$MONGO_URI ./venv/bin/python scripts/restore_database.py \
  --backup "$BACKUP_FILE" \
  --drop \
  --yes

# 3. Start application
echo "Starting application..."
sudo systemctl start dmm-backend

# 4. Wait and verify
sleep 15
curl -f http://localhost:8000/health || {
    echo "❌ Database rollback verification failed!"
    exit 1
}

echo "✅ Database rollback complete!"
```

---

## Summary

This rollback guide provides comprehensive procedures for handling deployment failures:

- ✅ **Quick Rollback**: 2-5 minutes for emergencies
- ✅ **Standard Rollback**: 10-15 minutes for normal issues
- ✅ **Database Rollback**: 20-30 minutes for schema changes
- ✅ **Partial Rollback**: 5-10 minutes for component issues
- ✅ **Decision Matrix**: Clear criteria for when to rollback
- ✅ **Automation Scripts**: Automated rollback procedures
- ✅ **Testing**: Regular rollback drills

### Key Principles

1. **Act Quickly**: Don't wait if service is down
2. **Communicate**: Keep everyone informed
3. **Document**: Record everything
4. **Learn**: Conduct post-mortems
5. **Prevent**: Improve processes
6. **Practice**: Regular rollback drills

### Quick Reference

**Emergency Rollback**:
```bash
git reset --hard backup-TAG → restart service → verify (2-5 min)
```

**Standard Rollback**:
```bash
backup → revert code → restore deps → restart → verify (10-15 min)
```

**Database Rollback**:
```bash
stop app → backup → restore DB → revert code → start → verify (20-30 min)
```

---

**Document Owner**: DevOps Team  
**Review Cycle**: Quarterly + after each rollback  
**Next Review**: 2025-02-04

---

**Emergency Contact**:
- On-Call Engineer: [Phone]
- DevOps Lead: [Phone]
- DBA: [Phone]
