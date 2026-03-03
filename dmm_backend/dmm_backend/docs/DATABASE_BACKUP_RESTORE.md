# Database Backup & Restore Guide

**DMM Backend - Production Database Management**

Version: 1.0  
Last Updated: 4 November 2568 (2025)  
Status: ✅ COMPLETE

---

## Table of Contents

1. [Overview](#overview)
2. [Backup Strategy](#backup-strategy)
3. [Recovery Objectives](#recovery-objectives)
4. [Backup Scripts](#backup-scripts)
5. [Restore Procedures](#restore-procedures)
6. [Backup Schedule](#backup-schedule)
7. [Monitoring & Verification](#monitoring--verification)
8. [Disaster Recovery](#disaster-recovery)
9. [Troubleshooting](#troubleshooting)
10. [Best Practices](#best-practices)

---

## Overview

### Purpose

This guide provides comprehensive procedures for backing up and restoring the DMM Backend MongoDB database. It ensures:

- **Data Protection**: Regular automated backups
- **Business Continuity**: Quick recovery from failures
- **Disaster Recovery**: Complete restoration procedures
- **Compliance**: Audit trail and verification

### System Components

- **Database**: MongoDB (NoSQL document database)
- **Backup Tool**: `mongodump` (MongoDB Database Tools)
- **Storage**: Local filesystem with retention policy
- **Automation**: Python scripts for backup/restore
- **Verification**: Checksums and integrity validation

---

## Backup Strategy

### Backup Types

#### 1. **Full Backups** (Daily)
- Complete database dump
- All collections and documents
- Compressed with gzip
- Retention: 30 days

#### 2. **Safety Backups** (Pre-Restore)
- Created automatically before any restore
- Temporary protection during operations
- Kept until restore success confirmed

### Backup Components

```
backups/
├── dmm_backup_20251104_143022.tar.gz      # Full backup
├── dmm_backup_20251104_143022_metadata.json  # Backup metadata
├── dmm_backup_20251103_143022.tar.gz      # Previous backup
├── dmm_backup_20251103_143022_metadata.json
└── dmm_safety_backup_20251104_150000.tar.gz  # Safety backup
```

### Metadata Structure

Each backup includes metadata for tracking and verification:

```json
{
  "backup_name": "dmm_backup_20251104_143022.tar.gz",
  "backup_path": "/path/to/backups/dmm_backup_20251104_143022.tar.gz",
  "timestamp": "2025-11-04T14:30:22.123456",
  "size_bytes": 1048576,
  "size_human": "1.00 MB",
  "compressed": true,
  "checksum": "a1b2c3d4e5f6...",
  "mongodb_uri": "mongodb://user:***@localhost:27017/...",
  "retention_days": 30
}
```

---

## Recovery Objectives

### RTO (Recovery Time Objective)

**Target: < 1 hour**

Complete database restoration time from backup to operational state:

- Backup verification: **5 minutes**
- Safety backup creation: **10 minutes**
- Database restore: **20-30 minutes** (depends on data size)
- Verification and testing: **15 minutes**
- Service restart: **5 minutes**

**Total Maximum: 60 minutes**

### RPO (Recovery Point Objective)

**Target: < 24 hours**

Maximum acceptable data loss in case of failure:

- **Daily backups**: Up to 24 hours of data loss
- **Recommended**: Implement hourly backups for production
- **Critical systems**: Consider continuous replication

### Availability Target

- **Uptime SLA**: 99.9% (8.76 hours downtime/year)
- **Planned maintenance**: 4 hours/quarter
- **Backup window**: 02:00-03:00 AM (low traffic period)

---

## Backup Scripts

### 1. Backup Database Script

**Location**: `dmm_backend/scripts/backup_database.py`

#### Usage

```bash
# Basic backup
python scripts/backup_database.py

# With custom configuration
python scripts/backup_database.py --config backup_config.json

# List existing backups
python scripts/backup_database.py --list
```

#### Configuration File

Create `backup_config.json`:

```json
{
  "backup_dir": "./backups",
  "retention_days": 30,
  "compress": true,
  "notify_email": "admin@example.com"
}
```

#### Environment Variables

```bash
# Required
export MONGODB_URI="mongodb://user:password@localhost:27017/digital_mind_model"

# Optional
export BACKUP_DIR="./backups"
export RETENTION_DAYS="30"
export COMPRESS="true"
export NOTIFY_EMAIL="admin@example.com"
```

#### Features

- ✅ **Automated backup**: mongodump with gzip compression
- ✅ **Compression**: Reduces storage by 70-80%
- ✅ **Retention policy**: Automatic cleanup of old backups
- ✅ **Verification**: Checksum validation
- ✅ **Metadata**: Complete backup tracking
- ✅ **Notifications**: Email alerts (optional)

#### Output Example

```
============================================================
DMM Backend - Database Backup
============================================================
Started at: 2025-11-04T14:30:22.123456
Backup directory: /path/to/backups

[1/5] Creating MongoDB dump...
   ✓ Dump created at: /path/to/backups/dmm_backup_20251104_143022
   2025-11-04T14:30:23.000+0700    writing users to dump
   2025-11-04T14:30:23.500+0700    done dumping (123 documents)

[2/5] Compressing backup...
   ✓ Compressed: 2.50 MB → 0.85 MB
   ✓ Compression ratio: 66.0%

[3/5] Verifying backup...
   ✓ Backup file exists
   ✓ Size: 0.85 MB
   ✓ Valid gzip archive

[4/5] Generating metadata...
   ✓ Metadata saved: dmm_backup_20251104_143022_metadata.json

[5/5] Cleaning up old backups...
   Removing old backup: dmm_backup_20251003_143022.tar.gz (2025-10-03)
   ✓ Removed 1 old backup(s)

============================================================
✅ Backup completed successfully!
============================================================
Backup file: dmm_backup_20251104_143022.tar.gz
Size: 0.85 MB
Checksum: a1b2c3d4e5f6...
Old backups removed: 1
Completed at: 2025-11-04T14:30:45.678901
============================================================
```

---

### 2. Restore Database Script

**Location**: `dmm_backend/scripts/restore_database.py`

#### Usage

```bash
# List available backups
python scripts/restore_database.py --list

# Restore from latest backup (with confirmation)
python scripts/restore_database.py --latest

# Restore from specific backup
python scripts/restore_database.py --backup dmm_backup_20251104_143022.tar.gz

# Restore and drop existing collections (⚠️ DESTRUCTIVE)
python scripts/restore_database.py --latest --drop

# Skip safety backup (NOT RECOMMENDED)
python scripts/restore_database.py --latest --skip-safety

# Auto-confirm (for automation, use with caution)
python scripts/restore_database.py --latest --yes
```

#### Features

- ✅ **Safety first**: Creates safety backup before restore
- ✅ **Verification**: Validates backup integrity (checksum)
- ✅ **Confirmation**: Requires user confirmation (unless --yes)
- ✅ **Progress tracking**: Detailed status updates
- ✅ **Rollback capability**: Safety backup for quick rollback
- ✅ **Drop option**: Can drop existing collections before restore

#### Output Example

```
============================================================
DMM Backend - Database Restore
============================================================
Started at: 2025-11-04T15:00:00.000000
Backup file: dmm_backup_20251104_143022.tar.gz

[Verification] Checking backup integrity...
   ✓ File exists: dmm_backup_20251104_143022.tar.gz
   ✓ Size: 0.85 MB
   Verifying checksum...
   ✓ Checksum verified: a1b2c3d4e5f6...
   ✓ Backup file is valid

============================================================
⚠️  WARNING: This will restore the database from backup!
============================================================

Type 'yes' to continue: yes

[Safety] Creating safety backup before restore...
   ✓ Safety backup created: dmm_safety_backup_20251104_150000.tar.gz
   ✓ Size: 0.82 MB

[Extraction] Extracting backup archive...
   ✓ Extracted to: /tmp/dmm_restore_abc123
   ✓ Backup directory: dmm_backup_20251104_143022

[Restore] Restoring database...
   2025-11-04T15:00:15.000+0700    preparing collections to restore from
   2025-11-04T15:00:16.000+0700    restoring users from dump
   2025-11-04T15:00:17.000+0700    finished restoring (123 documents)
   ✓ Restore completed

============================================================
✅ Restore completed successfully!
============================================================
Backup restored: dmm_backup_20251104_143022.tar.gz
Safety backup: dmm_safety_backup_20251104_150000.tar.gz

💡 To rollback, run:
   python scripts/restore_database.py --backup dmm_safety_backup_20251104_150000.tar.gz
Completed at: 2025-11-04T15:00:30.000000
============================================================
```

---

## Backup Schedule

### Production Schedule

| Frequency | Time (GMT+7) | Retention | Script Command |
|-----------|--------------|-----------|----------------|
| **Daily** | 02:00 AM | 30 days | `python scripts/backup_database.py` |
| **Weekly** | Sunday 03:00 AM | 12 weeks | `python scripts/backup_database.py` |
| **Monthly** | 1st day 04:00 AM | 12 months | `python scripts/backup_database.py` |

### Cron Configuration

Add to crontab (`crontab -e`):

```bash
# Daily backup at 2:00 AM
0 2 * * * cd /path/to/dmm_backend && ./venv/bin/python scripts/backup_database.py >> logs/backup.log 2>&1

# Weekly backup at 3:00 AM on Sundays
0 3 * * 0 cd /path/to/dmm_backend && RETENTION_DAYS=84 ./venv/bin/python scripts/backup_database.py >> logs/backup_weekly.log 2>&1

# Monthly backup at 4:00 AM on the 1st
0 4 1 * * cd /path/to/dmm_backend && RETENTION_DAYS=365 ./venv/bin/python scripts/backup_database.py >> logs/backup_monthly.log 2>&1
```

### Systemd Timer (Alternative)

Create `/etc/systemd/system/dmm-backup.service`:

```ini
[Unit]
Description=DMM Backend Database Backup
After=network.target

[Service]
Type=oneshot
User=dmm
WorkingDirectory=/path/to/dmm_backend
Environment="MONGODB_URI=mongodb://user:password@localhost:27017/digital_mind_model"
ExecStart=/path/to/dmm_backend/venv/bin/python scripts/backup_database.py
StandardOutput=append:/var/log/dmm/backup.log
StandardError=append:/var/log/dmm/backup.log
```

Create `/etc/systemd/system/dmm-backup.timer`:

```ini
[Unit]
Description=DMM Backend Database Backup Timer

[Timer]
OnCalendar=daily
OnCalendar=02:00
Persistent=true

[Install]
WantedBy=timers.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable dmm-backup.timer
sudo systemctl start dmm-backup.timer
sudo systemctl status dmm-backup.timer
```

---

## Restore Procedures

### Standard Restore Procedure

#### Prerequisites

1. ✅ MongoDB Database Tools installed
2. ✅ Access to backup files
3. ✅ Valid MONGODB_URI configured
4. ✅ Sufficient disk space (3x backup size)
5. ✅ Maintenance window scheduled

#### Step-by-Step Restore

**Step 1**: Stop application services

```bash
# Stop backend
pm2 stop dmm-backend

# Or if using systemd
sudo systemctl stop dmm-backend
```

**Step 2**: List available backups

```bash
cd dmm_backend
python scripts/restore_database.py --list
```

**Step 3**: Verify backup to restore

```bash
# Check metadata
cat backups/dmm_backup_YYYYMMDD_HHMMSS_metadata.json
```

**Step 4**: Perform restore

```bash
# Interactive restore (recommended)
python scripts/restore_database.py --backup dmm_backup_YYYYMMDD_HHMMSS.tar.gz

# Or restore latest
python scripts/restore_database.py --latest

# Type 'yes' when prompted
```

**Step 5**: Verify restored data

```bash
# Check MongoDB collections
mongosh "mongodb://localhost:27017/digital_mind_model" --eval "db.stats()"

# Check specific collections
mongosh "mongodb://localhost:27017/digital_mind_model" --eval "db.users.countDocuments()"
```

**Step 6**: Start application services

```bash
# Start backend
pm2 start dmm-backend

# Or if using systemd
sudo systemctl start dmm-backend
```

**Step 7**: Verify application functionality

```bash
# Test API health
curl http://localhost:8000/api/health

# Test authentication
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test"}'
```

---

### Emergency Restore Procedure

For critical failures requiring immediate restoration:

#### Fast Track Restore (15-20 minutes)

```bash
# 1. Stop services (1 min)
pm2 stop all

# 2. Restore latest backup with auto-confirm (10-15 min)
cd dmm_backend
python scripts/restore_database.py --latest --drop --yes

# 3. Start services (1 min)
pm2 start all

# 4. Verify (2-3 min)
curl http://localhost:8000/api/health
```

#### Rollback Procedure

If restore fails or causes issues:

```bash
# Restore from safety backup
python scripts/restore_database.py --backup dmm_safety_backup_YYYYMMDD_HHMMSS.tar.gz --yes
```

---

## Monitoring & Verification

### Automated Monitoring

#### Backup Success Monitoring

Monitor backup logs for failures:

```bash
# Check last backup status
tail -n 50 logs/backup.log | grep -E "(✅|❌)"

# Count successful backups in last 7 days
find backups/ -name "dmm_backup_*.tar.gz" -mtime -7 | wc -l
```

#### Disk Space Monitoring

```bash
# Check backup directory size
du -sh backups/

# Alert if backup directory > 10GB
BACKUP_SIZE=$(du -sb backups/ | cut -f1)
if [ $BACKUP_SIZE -gt 10737418240 ]; then
    echo "⚠️  Backup directory exceeds 10GB: $(du -sh backups/)"
fi
```

### Manual Verification

#### Verify Latest Backup

```bash
# List backups with details
python scripts/backup_database.py --list

# Test restore to temporary database
mongorestore --uri="mongodb://localhost:27017/dmm_test" \
  --gzip \
  --archive=backups/dmm_backup_LATEST.tar.gz

# Verify collections
mongosh "mongodb://localhost:27017/dmm_test" --eval "db.getCollectionNames()"
```

#### Monthly Restore Test

**Schedule**: First Sunday of each month

1. Create test environment
2. Restore latest backup to test database
3. Run application tests
4. Verify data integrity
5. Document results

```bash
# Monthly restore test script
#!/bin/bash
echo "=== Monthly Backup Restore Test ===" >> logs/restore_test.log
echo "Date: $(date)" >> logs/restore_test.log

# Restore to test database
python scripts/restore_database.py --latest --yes --test-db

# Run tests
pytest tests/ -k "integration"

echo "Test completed: $(date)" >> logs/restore_test.log
```

---

## Disaster Recovery

### Disaster Scenarios

#### Scenario 1: Database Corruption

**Symptoms**:
- MongoDB errors on queries
- Data inconsistencies
- Collection access errors

**Recovery Steps**:

1. Identify corruption scope
2. Stop application immediately
3. Restore from latest valid backup
4. Verify data integrity
5. Resume operations

**Estimated Time**: 30-45 minutes

---

#### Scenario 2: Complete Data Loss

**Symptoms**:
- All collections empty/missing
- Database doesn't exist
- Accidental drop database

**Recovery Steps**:

1. Stop panic, don't make it worse
2. Check if backups exist
3. Restore from latest backup
4. Verify completeness
5. Resume operations

**Estimated Time**: 45-60 minutes

---

#### Scenario 3: Server Failure

**Symptoms**:
- Server unreachable
- Hardware failure
- Disk failure

**Recovery Steps**:

1. Provision new server
2. Install MongoDB and dependencies
3. Copy backups to new server
4. Restore latest backup
5. Reconfigure application
6. Update DNS/load balancer
7. Resume operations

**Estimated Time**: 2-4 hours

---

### Disaster Recovery Checklist

- [ ] Identify disaster type and scope
- [ ] Notify stakeholders (team, users if needed)
- [ ] Stop affected services immediately
- [ ] Assess backup availability
- [ ] Initiate restore procedure
- [ ] Verify data integrity post-restore
- [ ] Run application tests
- [ ] Resume services
- [ ] Monitor for issues
- [ ] Document incident
- [ ] Review and improve processes

---

## Troubleshooting

### Common Issues

#### Issue 1: mongodump/mongorestore Not Found

**Error**:
```
FileNotFoundError: mongodump not found
```

**Solution**:

```bash
# macOS
brew install mongodb-database-tools

# Ubuntu/Debian
sudo apt-get install mongodb-database-tools

# Verify installation
mongodump --version
mongorestore --version
```

---

#### Issue 2: Permission Denied

**Error**:
```
PermissionError: [Errno 13] Permission denied: '/path/to/backups'
```

**Solution**:

```bash
# Fix directory permissions
sudo chown -R $USER:$USER backups/
chmod 755 backups/

# Or use sudo (not recommended)
sudo python scripts/backup_database.py
```

---

#### Issue 3: Disk Space Full

**Error**:
```
OSError: [Errno 28] No space left on device
```

**Solution**:

```bash
# Check disk space
df -h

# Clean old backups manually
rm backups/dmm_backup_202510*.tar.gz

# Or reduce retention period
export RETENTION_DAYS=7
python scripts/backup_database.py
```

---

#### Issue 4: Checksum Mismatch

**Error**:
```
✗ Checksum mismatch!
  Expected: a1b2c3d4...
  Actual:   x9y8z7w6...
```

**Solution**:

```bash
# Backup file may be corrupted
# Try previous backup
python scripts/restore_database.py --backup dmm_backup_PREVIOUS_DATE.tar.gz

# If all backups corrupted, check disk integrity
sudo fsck /dev/sda1
```

---

#### Issue 5: MongoDB Connection Failed

**Error**:
```
pymongo.errors.ServerSelectionTimeoutError: localhost:27017: [Errno 61] Connection refused
```

**Solution**:

```bash
# Check MongoDB is running
sudo systemctl status mongod

# Start MongoDB if stopped
sudo systemctl start mongod

# Verify connection
mongosh "mongodb://localhost:27017" --eval "db.serverStatus()"

# Check MONGODB_URI
echo $MONGODB_URI
```

---

## Best Practices

### Backup Best Practices

1. **✅ Regular Testing**
   - Test restore monthly
   - Verify data integrity
   - Document test results

2. **✅ Off-Site Backups**
   - Copy backups to remote storage
   - Use cloud storage (S3, Google Cloud Storage)
   - Keep 3-2-1 rule: 3 copies, 2 different media, 1 off-site

3. **✅ Encryption**
   - Encrypt backups at rest
   - Use secure transfer protocols
   - Rotate encryption keys

4. **✅ Monitoring**
   - Alert on backup failures
   - Track backup sizes and trends
   - Monitor disk space usage

5. **✅ Documentation**
   - Keep runbooks updated
   - Document restore procedures
   - Train team members

### Security Best Practices

1. **✅ Access Control**
   - Restrict backup directory access
   - Use IAM roles for cloud storage
   - Audit access logs

2. **✅ Secrets Management**
   - Never commit MONGODB_URI to git
   - Use environment variables
   - Rotate credentials regularly

3. **✅ Backup Verification**
   - Always verify checksums
   - Test random backups
   - Automate verification

### Operational Best Practices

1. **✅ Change Management**
   - Backup before major changes
   - Test in staging first
   - Have rollback plan ready

2. **✅ Capacity Planning**
   - Monitor backup growth
   - Plan disk space needs
   - Set up alerts for thresholds

3. **✅ Incident Response**
   - Have DR plan documented
   - Practice disaster scenarios
   - Keep contact list updated

---

## Appendix

### A. Backup Configuration Reference

| Parameter | Default | Description |
|-----------|---------|-------------|
| `backup_dir` | `./backups` | Backup storage directory |
| `retention_days` | `30` | Days to keep backups |
| `compress` | `true` | Enable gzip compression |
| `notify_email` | `null` | Email for notifications |

### B. Script Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | General error |
| `2` | Invalid arguments |
| `3` | MongoDB connection failed |
| `4` | Backup verification failed |
| `5` | Disk space insufficient |

### C. Useful Commands

```bash
# Check MongoDB version
mongod --version

# Check database size
mongosh --eval "db.stats(1024*1024)"  # Size in MB

# Export single collection
mongodump --uri="$MONGODB_URI" --collection=users --out=./user_backup

# Import single collection
mongorestore --uri="$MONGODB_URI" --collection=users ./user_backup/digital_mind_model/users.bson

# Create database snapshot (if using MongoDB Atlas)
# Use MongoDB Atlas UI or API
```

### D. Contact Information

| Role | Contact | Availability |
|------|---------|--------------|
| **Database Admin** | dba@example.com | 24/7 |
| **DevOps Team** | devops@example.com | Business hours |
| **On-Call Engineer** | oncall@example.com | 24/7 |

---

## Revision History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-11-04 | Initial release | DMM Team |

---

**Document Owner**: DevOps Team  
**Review Cycle**: Quarterly  
**Next Review**: 2025-02-04

---

✅ **Phase 4 Complete: Database Backup & Restore System**

This comprehensive guide provides all necessary procedures and best practices for database backup and restore operations in the DMM Backend system.
