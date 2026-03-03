# Configuration Reference

**DMM Backend - Complete Configuration Guide**

Version: 1.4.0  
Last Updated: 4 November 2568 (2025)  
Status: ✅ Production Ready

---

## Table of Contents

1. [Overview](#overview)
2. [Environment Variables](#environment-variables)
3. [Application Settings](#application-settings)
4. [Database Configuration](#database-configuration)
5. [Security Configuration](#security-configuration)
6. [CORS Configuration](#cors-configuration)
7. [Logging Configuration](#logging-configuration)
8. [Backup Configuration](#backup-configuration)
9. [Server Configuration](#server-configuration)
10. [Environment Examples](#environment-examples)

---

## Overview

This document provides a complete reference for all configuration options in the DMM Backend application. Configuration is managed through:

- **Environment Variables**: Primary configuration method (`.env` file)
- **Settings Class**: `config.py` - Pydantic settings with validation
- **Default Values**: Sensible defaults for development

### Configuration Priority

1. **Environment Variables** (highest priority)
2. **`.env` File**
3. **Default Values** (lowest priority)

### Configuration File Location

```
dmm_backend/
├── .env                    # Main configuration file (not in git)
├── .env.example           # Example template (in git)
├── config.py              # Settings class definition
└── docs/
    └── CONFIG.md          # This file
```

---

## Environment Variables

### Complete List

| Variable | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| **Application** |
| `API_TITLE` | string | No | "Digital Mind API" | API title for documentation |
| `API_DESCRIPTION` | string | No | "API for..." | API description |
| `API_VERSION` | string | No | "1.4.0" | API version number |
| `DEBUG_MODE` | boolean | No | `false` | Enable debug mode |
| `API_KEY` | string | **Yes** | - | API security key |
| **Database** |
| `MONGO_URI` | string | **Yes** | - | MongoDB connection string |
| `MONGODB_URI` | string | No | - | Alias for MONGO_URI |
| `MONGO_DB_NAME` | string | No | "digital_mind_model" | Database name |
| `DATABASE_NAME` | string | No | - | Alias for MONGO_DB_NAME |
| `MONGODB_URL` | string | No | - | Deprecated alias |
| **Security** |
| `JWT_SECRET_KEY` | string | **Yes** | - | JWT signing secret (min 32 chars) |
| `JWT_ALGORITHM` | string | No | "HS256" | JWT signing algorithm |
| `JWT_EXPIRATION_MINUTES` | integer | No | 60 | Token expiration time |
| **CORS** |
| `CORS_ORIGINS` | string | No | localhost URLs | Comma-separated allowed origins |
| **Database Features** |
| `KAMMA_TTL_SECONDS` | integer | No | `null` | TTL for kamma records (seconds) |
| `UNIQUE_TIMELINE_PER_MODEL` | boolean | No | `false` | Enforce unique timeline per model |
| **Backup** |
| `BACKUP_DIR` | string | No | "./backups" | Backup storage directory |
| `RETENTION_DAYS` | integer | No | 30 | Backup retention period |
| `COMPRESS` | boolean | No | `true` | Enable backup compression |
| `NOTIFY_EMAIL` | string | No | - | Email for backup notifications |
| **Logging** |
| `LOG_LEVEL` | string | No | "INFO" | Logging level |
| `LOG_FILE` | string | No | - | Log file path |
| **Server** |
| `HOST` | string | No | "127.0.0.1" | Server bind address |
| `PORT` | integer | No | 8000 | Server port |
| `WORKERS` | integer | No | 4 | Number of worker processes |

---

## Application Settings

### API_TITLE

**Type**: `string`  
**Default**: `"Digital Mind API"`  
**Required**: No

API title displayed in OpenAPI documentation and API responses.

**Example**:
```bash
API_TITLE="Digital Mind Model API - Production"
```

**Usage**:
- Shown in `/docs` (Swagger UI)
- Shown in `/redoc` (ReDoc)
- Included in OpenAPI schema

---

### API_DESCRIPTION

**Type**: `string`  
**Default**: `"API for simulating and interacting with a Digital Mind Model."`  
**Required**: No

Detailed description of the API functionality.

**Example**:
```bash
API_DESCRIPTION="Production API for Digital Mind Model simulation and interaction. Provides endpoints for model management, timeline operations, and kamma tracking."
```

---

### API_VERSION

**Type**: `string`  
**Default**: `"1.4.0"`  
**Required**: No

API version number (semantic versioning recommended).

**Example**:
```bash
API_VERSION="1.4.0"
```

**Best Practice**:
- Use semantic versioning (MAJOR.MINOR.PATCH)
- Update on breaking changes
- Document changes in CHANGELOG.md

---

### DEBUG_MODE

**Type**: `boolean`  
**Default**: `false`  
**Required**: No

Enable debug mode for development.

**Example**:
```bash
# Development
DEBUG_MODE=true

# Production
DEBUG_MODE=false
```

**When Enabled**:
- Detailed error messages
- Verbose logging
- Hot reload (if supported)
- Performance impact

**⚠️ Warning**: Never enable in production - exposes sensitive information!

---

### API_KEY

**Type**: `string`  
**Required**: **Yes**  
**Minimum Length**: 32 characters

API security key for authentication and authorization.

**Generation**:
```bash
# Generate secure API key (recommended)
python3 -c "import secrets; import base64; print(base64.urlsafe_b64encode(secrets.token_bytes(32)).decode())"

# Or use openssl
openssl rand -base64 32
```

**Example**:
```bash
API_KEY="ONtqp8VVF0JP0WBqII4JYjN3g58nXnT7gvM_0Qh4tDg"
```

**Security Best Practices**:
- ✅ Use cryptographically random values
- ✅ Minimum 32 characters
- ✅ Rotate regularly (every 90 days)
- ✅ Never commit to version control
- ✅ Different key per environment
- ❌ Never use default or weak values

---

## Database Configuration

### MONGO_URI / MONGODB_URI

**Type**: `string`  
**Required**: **Yes**  
**Format**: MongoDB connection string

Primary MongoDB connection URI.

**Format**:
```
mongodb://[username:password@]host[:port][/database][?options]
```

**Examples**:

**Development** (no authentication):
```bash
MONGO_URI="mongodb://localhost:27017/digital_mind_model"
```

**Production** (with authentication):
```bash
MONGO_URI="mongodb://dmm_user:STRONG_PASSWORD@localhost:27017/digital_mind_model?authSource=admin"
```

**MongoDB Atlas** (cloud):
```bash
MONGO_URI="mongodb+srv://username:password@cluster0.mongodb.net/digital_mind_model?retryWrites=true&w=majority"
```

**Replica Set**:
```bash
MONGO_URI="mongodb://user:pass@host1:27017,host2:27017,host3:27017/digital_mind_model?replicaSet=rs0"
```

**Connection Options**:
- `authSource=admin` - Authentication database
- `retryWrites=true` - Enable retry writes
- `w=majority` - Write concern
- `maxPoolSize=50` - Connection pool size
- `connectTimeoutMS=10000` - Connection timeout
- `serverSelectionTimeoutMS=5000` - Server selection timeout

**Security**:
- ⚠️ Never commit connection string with credentials
- ⚠️ Use strong passwords (min 16 chars, mixed case, numbers, symbols)
- ⚠️ Restrict database user permissions (readWrite only)
- ⚠️ Use TLS/SSL in production (`ssl=true`)

---

### MONGO_DB_NAME / DATABASE_NAME

**Type**: `string`  
**Default**: `"digital_mind_model"`  
**Required**: No

Name of the MongoDB database to use.

**Example**:
```bash
# Development
MONGO_DB_NAME="digital_mind_model_dev"

# Staging
MONGO_DB_NAME="digital_mind_model_staging"

# Production
MONGO_DB_NAME="digital_mind_model"
```

**Best Practice**:
- Use different databases per environment
- Include environment suffix for clarity
- Keep production database name simple

---

### KAMMA_TTL_SECONDS

**Type**: `integer`  
**Default**: `null` (no TTL)  
**Required**: No

Time-to-live (TTL) for kamma records in seconds. After this time, records are automatically deleted.

**Examples**:
```bash
# 30 days
KAMMA_TTL_SECONDS=2592000

# 90 days
KAMMA_TTL_SECONDS=7776000

# No TTL (keep forever)
# KAMMA_TTL_SECONDS=  # Leave empty or comment out
```

**Use Cases**:
- Compliance with data retention policies
- Automatic cleanup of old data
- Storage optimization

**⚠️ Warning**: 
- TTL deletion is irreversible
- Ensure backups before enabling
- Test with non-production data first

---

### UNIQUE_TIMELINE_PER_MODEL

**Type**: `boolean`  
**Default**: `false`  
**Required**: No

Enforce unique timeline per model (one active timeline per model).

**Example**:
```bash
# Enforce unique timeline
UNIQUE_TIMELINE_PER_MODEL=true

# Allow multiple timelines (default)
UNIQUE_TIMELINE_PER_MODEL=false
```

**When Enabled**:
- Only one active timeline per model allowed
- Attempts to create additional timelines return error
- Useful for single-timeline simulations

**When Disabled**:
- Multiple timelines per model allowed
- Useful for parallel simulations
- More flexible but requires careful management

---

## Security Configuration

### JWT_SECRET_KEY

**Type**: `string`  
**Required**: **Yes**  
**Minimum Length**: 32 characters

Secret key for signing JWT tokens.

**Generation**:
```bash
# Generate 64-character hex key (recommended)
python3 -c "import secrets; print(secrets.token_hex(32))"

# Or use openssl
openssl rand -hex 32
```

**Example**:
```bash
JWT_SECRET_KEY="b2ace8e38ce5b7cef4e3438ac2dc6851b61d50a952fbfed004acd63a35181bfd"
```

**Security Best Practices**:
- ✅ Use cryptographically random values
- ✅ Minimum 64 characters (hex) or 32 bytes
- ✅ Rotate regularly (every 90-180 days)
- ✅ Never commit to version control
- ✅ Different key per environment
- ✅ Store in secrets manager (production)
- ❌ Never reuse keys across environments

**Token Rotation**:
When rotating JWT secret:
1. Generate new secret
2. Update `.env` file
3. Restart application
4. All existing tokens become invalid
5. Users must re-authenticate

---

### JWT_ALGORITHM

**Type**: `string`  
**Default**: `"HS256"`  
**Required**: No

Algorithm used for JWT signing.

**Supported Algorithms**:
- `HS256` (HMAC-SHA256) - Symmetric, recommended for most use cases
- `HS384` (HMAC-SHA384) - Stronger symmetric
- `HS512` (HMAC-SHA512) - Strongest symmetric
- `RS256` (RSA-SHA256) - Asymmetric, requires key pair
- `RS384`, `RS512` - Stronger RSA variants
- `ES256`, `ES384`, `ES512` - ECDSA variants

**Example**:
```bash
# Default (recommended)
JWT_ALGORITHM="HS256"

# Stronger HMAC
JWT_ALGORITHM="HS512"

# Asymmetric (requires RSA keys)
JWT_ALGORITHM="RS256"
```

**Recommendation**:
- Use `HS256` for simplicity and performance
- Use `RS256` if you need public key verification
- Avoid weaker algorithms (HS256 is secure with strong secret)

---

### JWT_EXPIRATION_MINUTES

**Type**: `integer`  
**Default**: `60` (1 hour)  
**Required**: No

JWT token expiration time in minutes.

**Examples**:
```bash
# 15 minutes (high security)
JWT_EXPIRATION_MINUTES=15

# 1 hour (recommended)
JWT_EXPIRATION_MINUTES=60

# 24 hours (convenience, lower security)
JWT_EXPIRATION_MINUTES=1440

# 7 days (not recommended for production)
JWT_EXPIRATION_MINUTES=10080
```

**Security vs Convenience**:
| Duration | Security | User Experience | Use Case |
|----------|----------|-----------------|----------|
| 15 min | Very High | Frequent re-auth | Financial apps |
| 1 hour | High | Balanced | **Recommended** |
| 24 hours | Medium | Convenient | Internal tools |
| 7+ days | Low | Very convenient | ❌ Not recommended |

**Best Practice**:
- Production: 15-60 minutes
- Implement refresh tokens for longer sessions
- Consider implementing "remember me" separately
- Shorter expiration for admin tokens

---

## CORS Configuration

### CORS_ORIGINS

**Type**: `string` (comma-separated)  
**Default**: Localhost URLs  
**Required**: No

Allowed origins for Cross-Origin Resource Sharing (CORS).

**Format**:
```
CORS_ORIGINS="origin1,origin2,origin3"
```

**Examples**:

**Development**:
```bash
CORS_ORIGINS="http://localhost:3000,http://localhost:5173,http://127.0.0.1:5173"
```

**Production**:
```bash
CORS_ORIGINS="https://yourdomain.com,https://www.yourdomain.com,https://app.yourdomain.com"
```

**Multiple Environments**:
```bash
CORS_ORIGINS="https://yourdomain.com,https://staging.yourdomain.com,https://dev.yourdomain.com"
```

**Security Best Practices**:
- ✅ Only list necessary origins
- ✅ Use specific domains (avoid wildcards in production)
- ✅ Include protocol (http/https)
- ✅ Different per environment
- ❌ Never use `*` in production
- ❌ Don't include unnecessary origins

**Default Value**:
```python
CORS_ORIGINS = (
    "http://localhost:3000,http://localhost:5173,http://localhost:5178,"
    "http://localhost:8000,http://127.0.0.1:5173,http://127.0.0.1:5178,"
    "http://127.0.0.1:4173,http://127.0.0.1:3000,http://127.0.0.1:5181,"
    "http://127.0.0.1:5182,http://localhost:5181,http://localhost:5182"
)
```

**Testing CORS**:
```bash
# Test from browser console
fetch('https://api.yourdomain.com/health', {
  method: 'GET',
  headers: {
    'Origin': 'https://yourdomain.com'
  }
}).then(r => console.log(r.headers.get('Access-Control-Allow-Origin')))

# Test with curl
curl -H "Origin: https://yourdomain.com" -I https://api.yourdomain.com/health
```

---

## Logging Configuration

### LOG_LEVEL

**Type**: `string`  
**Default**: `"INFO"`  
**Required**: No

Logging level for application logs.

**Available Levels** (from most to least verbose):
- `DEBUG` - Detailed debugging information
- `INFO` - General informational messages
- `WARNING` - Warning messages
- `ERROR` - Error messages
- `CRITICAL` - Critical errors

**Examples**:
```bash
# Development
LOG_LEVEL="DEBUG"

# Staging
LOG_LEVEL="INFO"

# Production
LOG_LEVEL="WARNING"
```

**Level Details**:

**DEBUG**:
- All SQL queries, API calls, function calls
- Performance: Slowest
- Disk usage: Highest
- Use case: Development, troubleshooting

**INFO** (recommended):
- Application startup/shutdown
- Important state changes
- API requests (summary)
- Performance: Good
- Disk usage: Moderate
- Use case: Production, general monitoring

**WARNING**:
- Recoverable errors
- Deprecated feature usage
- Performance: Better
- Disk usage: Low
- Use case: Stable production

**ERROR**:
- Errors that need attention
- Failed operations
- Use case: Minimal logging

**CRITICAL**:
- System failures
- Use case: Emergency only

**⚠️ Production Recommendation**: `INFO` or `WARNING`

---

### LOG_FILE

**Type**: `string`  
**Default**: `null` (stdout only)  
**Required**: No

Path to log file for persistent logging.

**Examples**:
```bash
# Relative path
LOG_FILE="./logs/app.log"

# Absolute path
LOG_FILE="/var/log/dmm/backend.log"

# Separate error logs
LOG_FILE="/var/log/dmm/app.log"
ERROR_LOG_FILE="/var/log/dmm/error.log"
```

**Best Practices**:
- Use absolute paths in production
- Ensure directory exists and is writable
- Implement log rotation (logrotate)
- Monitor disk space
- Separate error logs if needed

**Log Rotation** (logrotate config):
```bash
# /etc/logrotate.d/dmm-backend
/var/log/dmm/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 dmm dmm
    sharedscripts
    postrotate
        systemctl reload dmm-backend
    endscript
}
```

---

## Backup Configuration

### BACKUP_DIR

**Type**: `string`  
**Default**: `"./backups"`  
**Required**: No

Directory for storing database backups.

**Examples**:
```bash
# Relative path (development)
BACKUP_DIR="./backups"

# Absolute path (production)
BACKUP_DIR="/var/backups/dmm"

# Network mount
BACKUP_DIR="/mnt/backups/dmm"
```

**Requirements**:
- Directory must exist or be creatable
- Write permissions required
- Sufficient disk space
- Consider SSD for performance

**Disk Space Planning**:
```bash
# Estimate backup size
Database Size: 1 GB
Compression Ratio: 70%
Compressed Size: 300 MB
Retention: 30 days
Total Space: 30 × 300 MB = 9 GB minimum
Recommended: 15-20 GB (with buffer)
```

---

### RETENTION_DAYS

**Type**: `integer`  
**Default**: `30`  
**Required**: No

Number of days to retain backups before automatic deletion.

**Examples**:
```bash
# Short retention (7 days)
RETENTION_DAYS=7

# Standard (30 days)
RETENTION_DAYS=30

# Extended (90 days)
RETENTION_DAYS=90

# Long-term (365 days)
RETENTION_DAYS=365
```

**Retention Strategy**:
| Type | Retention | Frequency | Purpose |
|------|-----------|-----------|---------|
| Daily | 7 days | Daily | Recent recovery |
| Weekly | 4 weeks | Weekly | Short-term recovery |
| Monthly | 12 months | Monthly | Long-term compliance |

**Best Practice**:
- Match retention to compliance requirements
- Consider storage costs
- Implement 3-2-1 backup rule:
  * 3 copies of data
  * 2 different media types
  * 1 off-site copy

---

### COMPRESS

**Type**: `boolean`  
**Default**: `true`  
**Required**: No

Enable gzip compression for backups.

**Examples**:
```bash
# Enable compression (recommended)
COMPRESS=true

# Disable compression
COMPRESS=false
```

**Compression Benefits**:
- **Storage Savings**: 60-80% reduction
- **Transfer Speed**: Faster uploads to cloud storage
- **Cost**: Lower storage costs

**Compression Trade-offs**:
- **CPU Usage**: Slight increase during backup
- **Time**: Backup takes 10-20% longer
- **Restore**: Must decompress first

**Recommendation**: Enable unless CPU is severely constrained

**Typical Compression Ratios**:
- JSON/Text data: 70-80% reduction
- Binary data: 30-50% reduction
- Mixed data: 50-70% reduction

---

### NOTIFY_EMAIL

**Type**: `string`  
**Default**: `null` (no notifications)  
**Required**: No

Email address for backup notifications.

**Example**:
```bash
NOTIFY_EMAIL="admin@yourdomain.com"
```

**Notifications Sent**:
- ✅ Backup success
- ❌ Backup failure
- ⚠️ Low disk space
- ⚠️ Backup verification failed

**⚠️ Note**: Email functionality requires SMTP configuration (currently placeholder)

**Future Implementation**:
```bash
# SMTP settings (to be added)
SMTP_HOST="smtp.gmail.com"
SMTP_PORT=587
SMTP_USER="your-email@gmail.com"
SMTP_PASSWORD="app-password"
SMTP_FROM="noreply@yourdomain.com"
```

---

## Server Configuration

### HOST

**Type**: `string`  
**Default**: `"127.0.0.1"`  
**Required**: No

Server bind address.

**Examples**:
```bash
# Localhost only (recommended with reverse proxy)
HOST="127.0.0.1"

# All interfaces (direct access, no reverse proxy)
HOST="0.0.0.0"

# Specific interface
HOST="192.168.1.100"
```

**Security**:
- ✅ `127.0.0.1`: Most secure, requires reverse proxy
- ⚠️ `0.0.0.0`: Exposes to all interfaces, use with firewall
- ⚠️ Specific IP: Expose to specific network only

**Recommendation**: Use `127.0.0.1` with Nginx reverse proxy in production

---

### PORT

**Type**: `integer`  
**Default**: `8000`  
**Required**: No

Server port number.

**Examples**:
```bash
# Default
PORT=8000

# Alternative
PORT=8080

# Custom
PORT=3000
```

**Port Selection**:
- `80`: HTTP (requires root, use reverse proxy instead)
- `443`: HTTPS (requires root, use reverse proxy instead)
- `1024-49151`: Registered ports (some may conflict)
- `49152-65535`: Dynamic/private ports (safest)

**Best Practice**:
- Use port 8000-8999 for backend services
- Use reverse proxy for ports 80/443
- Document port assignments

---

### WORKERS

**Type**: `integer`  
**Default**: `4`  
**Required**: No

Number of Uvicorn worker processes.

**Calculation**:
```bash
# Formula: (CPU cores × 2) + 1
# 2 cores: 5 workers
# 4 cores: 9 workers
# 8 cores: 17 workers

# Conservative: CPU cores
WORKERS=4

# Recommended: (CPU cores × 2) + 1
WORKERS=9

# Maximum: Don't exceed (CPU cores × 4)
```

**Examples**:
```bash
# Development (single worker for debugging)
WORKERS=1

# Production (4 CPU cores)
WORKERS=9

# High-load production (8 CPU cores)
WORKERS=17
```

**Considerations**:
- More workers = better concurrency
- More workers = more memory usage
- Optimal = (2 × cores) + 1
- Monitor CPU and memory usage
- Adjust based on workload

**Trade-offs**:
| Workers | CPU Usage | Memory Usage | Concurrency | Use Case |
|---------|-----------|--------------|-------------|----------|
| 1 | Low | Low | Low | Development |
| 4 | Medium | Medium | Good | Small production |
| 9 | High | High | Excellent | Standard production |
| 17+ | Very High | Very High | Maximum | High-load production |

---

## Environment Examples

### Development Environment

**`.env.development`**:
```bash
# Application
API_TITLE="Digital Mind API - Development"
API_VERSION="1.4.0-dev"
DEBUG_MODE=true
API_KEY="dev-api-key-not-secure"

# Database
MONGO_URI="mongodb://localhost:27017/digital_mind_model_dev"
MONGO_DB_NAME="digital_mind_model_dev"

# Security
JWT_SECRET_KEY="dev-jwt-secret-not-for-production"
JWT_ALGORITHM="HS256"
JWT_EXPIRATION_MINUTES=1440  # 24 hours for convenience

# CORS
CORS_ORIGINS="http://localhost:3000,http://localhost:5173,http://127.0.0.1:5173"

# Logging
LOG_LEVEL="DEBUG"
LOG_FILE="./logs/dev.log"

# Backup
BACKUP_DIR="./backups/dev"
RETENTION_DAYS=7
COMPRESS=true

# Server
HOST="127.0.0.1"
PORT=8000
WORKERS=1  # Single worker for debugging
```

---

### Staging Environment

**`.env.staging`**:
```bash
# Application
API_TITLE="Digital Mind API - Staging"
API_VERSION="1.4.0-staging"
DEBUG_MODE=false
API_KEY="staging-secure-api-key-change-this"

# Database
MONGO_URI="mongodb://dmm_staging:STAGING_PASSWORD@localhost:27017/digital_mind_model_staging?authSource=admin"
MONGO_DB_NAME="digital_mind_model_staging"

# Security
JWT_SECRET_KEY="staging-jwt-secret-64-chars-min-change-this-value"
JWT_ALGORITHM="HS256"
JWT_EXPIRATION_MINUTES=60

# CORS
CORS_ORIGINS="https://staging.yourdomain.com,https://staging-admin.yourdomain.com"

# Database Features
KAMMA_TTL_SECONDS=2592000  # 30 days
UNIQUE_TIMELINE_PER_MODEL=false

# Logging
LOG_LEVEL="INFO"
LOG_FILE="/var/log/dmm/staging.log"

# Backup
BACKUP_DIR="/var/backups/dmm/staging"
RETENTION_DAYS=14
COMPRESS=true
NOTIFY_EMAIL="staging-alerts@yourdomain.com"

# Server
HOST="127.0.0.1"
PORT=8000
WORKERS=4
```

---

### Production Environment

**`.env.production`**:
```bash
# Application
API_TITLE="Digital Mind API"
API_VERSION="1.4.0"
DEBUG_MODE=false
API_KEY="prod-VERY-SECURE-api-key-32-plus-chars-random"

# Database
MONGO_URI="mongodb://dmm_prod:VERY_STRONG_PASSWORD@localhost:27017/digital_mind_model?authSource=admin&ssl=true"
MONGO_DB_NAME="digital_mind_model"

# Security
JWT_SECRET_KEY="prod-jwt-secret-64-chars-minimum-cryptographically-secure-random"
JWT_ALGORITHM="HS256"
JWT_EXPIRATION_MINUTES=60

# CORS
CORS_ORIGINS="https://yourdomain.com,https://www.yourdomain.com,https://app.yourdomain.com"

# Database Features
KAMMA_TTL_SECONDS=7776000  # 90 days
UNIQUE_TIMELINE_PER_MODEL=false

# Logging
LOG_LEVEL="INFO"
LOG_FILE="/var/log/dmm/app.log"

# Backup
BACKUP_DIR="/var/backups/dmm"
RETENTION_DAYS=30
COMPRESS=true
NOTIFY_EMAIL="production-alerts@yourdomain.com"

# Server
HOST="127.0.0.1"
PORT=8000
WORKERS=9  # (4 cores × 2) + 1
```

---

## Configuration Validation

### Validation Script

Create `scripts/validate_config.py`:

```python
#!/usr/bin/env python3
"""Validate configuration before deployment."""

import os
import sys
from pathlib import Path

def validate_config():
    """Validate all required configuration."""
    errors = []
    warnings = []
    
    # Required variables
    required = ['API_KEY', 'MONGO_URI', 'JWT_SECRET_KEY']
    for var in required:
        if not os.getenv(var):
            errors.append(f"Missing required variable: {var}")
    
    # Validate JWT_SECRET_KEY length
    jwt_secret = os.getenv('JWT_SECRET_KEY', '')
    if len(jwt_secret) < 32:
        errors.append(f"JWT_SECRET_KEY too short: {len(jwt_secret)} < 32 chars")
    
    # Validate DEBUG_MODE
    debug_mode = os.getenv('DEBUG_MODE', 'false').lower()
    if debug_mode == 'true':
        warnings.append("DEBUG_MODE=true in production is dangerous!")
    
    # Validate backup directory
    backup_dir = Path(os.getenv('BACKUP_DIR', './backups'))
    if not backup_dir.exists():
        warnings.append(f"Backup directory does not exist: {backup_dir}")
    
    # Print results
    if errors:
        print("❌ Configuration Errors:")
        for error in errors:
            print(f"  - {error}")
    
    if warnings:
        print("\n⚠️  Configuration Warnings:")
        for warning in warnings:
            print(f"  - {warning}")
    
    if not errors and not warnings:
        print("✅ Configuration is valid!")
        return 0
    
    return 1 if errors else 0

if __name__ == '__main__':
    sys.exit(validate_config())
```

**Usage**:
```bash
# Load .env and validate
source .env && python scripts/validate_config.py
```

---

## Summary

This configuration reference provides complete documentation for all DMM Backend configuration options:

- ✅ **Complete Variable List**: All environment variables documented
- ✅ **Type Information**: Types, defaults, and requirements
- ✅ **Examples**: Development, staging, and production examples
- ✅ **Security Guidelines**: Best practices for secrets and security
- ✅ **Validation**: Tools to verify configuration

### Key Takeaways

1. **Required Variables**: `API_KEY`, `MONGO_URI`, `JWT_SECRET_KEY`
2. **Security**: Use strong, random values for all secrets
3. **Environment-Specific**: Different configuration per environment
4. **Validation**: Always validate before deployment
5. **Documentation**: Keep this document updated with changes

### Quick Reference

**Most Important Settings**:
```bash
API_KEY=<32+ char random>
MONGO_URI=<mongodb connection string>
JWT_SECRET_KEY=<64+ char random>
CORS_ORIGINS=<your domains>
DEBUG_MODE=false  # Production
```

**Next Steps**:
- Review DEPLOYMENT.md for deployment procedures
- Review DEPLOY_STEPS.md for step-by-step guide
- Generate secure secrets for production
- Create environment-specific .env files

---

**Document Owner**: DevOps Team  
**Review Cycle**: Quarterly  
**Next Review**: 2025-02-04
