# Monitoring & Logging Guide

**DMM Backend - Production Monitoring**  
**Version**: 1.4.0  
**Last Updated**: 4 November 2568 (2025)

---

## Table of Contents

1. [Overview](#overview)
2. [Health Check Endpoint](#health-check-endpoint)
3. [Metrics Collection](#metrics-collection)
4. [Prometheus Integration](#prometheus-integration)
5. [Grafana Dashboards](#grafana-dashboards)
6. [Log Management](#log-management)
7. [Alerting](#alerting)
8. [Performance Monitoring](#performance-monitoring)
9. [Database Monitoring](#database-monitoring)
10. [Security Monitoring](#security-monitoring)
11. [Troubleshooting](#troubleshooting)
12. [Best Practices](#best-practices)

---

## Overview

### Monitoring Strategy

The DMM Backend implements comprehensive monitoring across multiple layers:

- **Health Checks**: HTTP endpoint for service health verification
- **Metrics**: Prometheus-compatible metrics for system and application monitoring
- **Logging**: Structured JSON logging for analysis and troubleshooting
- **Alerting**: Automated alerts for critical issues
- **Tracing**: Request ID tracking for distributed tracing

### Monitoring Stack

```
┌─────────────────────────────────────────┐
│         DMM Backend Application          │
│  ┌──────────┐  ┌──────────┐  ┌────────┐│
│  │  Health  │  │ Metrics  │  │  Logs  ││
│  │  /health │  │ /metrics │  │  JSON  ││
│  └──────────┘  └──────────┘  └────────┘│
└──────┬──────────────┬───────────┬───────┘
       │              │           │
       ▼              ▼           ▼
┌──────────┐   ┌──────────┐  ┌──────────┐
│ Uptime   │   │Prometheus│  │   ELK    │
│  Robot   │   │          │  │  Stack   │
└──────────┘   └─────┬────┘  └──────────┘
                     │
                     ▼
               ┌──────────┐
               │ Grafana  │
               │Dashboard │
               └─────┬────┘
                     │
                     ▼
               ┌──────────┐
               │ Alerting │
               │PagerDuty │
               └──────────┘
```

### Key Metrics

| Metric | Purpose | Alert Threshold |
|--------|---------|-----------------|
| **Service Uptime** | Service availability | < 99.9% |
| **Response Time** | API performance | > 500ms (p95) |
| **Error Rate** | Application errors | > 1% |
| **CPU Usage** | System resources | > 80% |
| **Memory Usage** | System resources | > 85% |
| **Disk Usage** | Storage capacity | > 80% |
| **DB Response Time** | Database performance | > 100ms |
| **Request Rate** | Traffic patterns | Sudden spikes/drops |

---

## Health Check Endpoint

### Endpoint Details

**URL**: `GET /health`  
**Authentication**: None (public endpoint)  
**Response Format**: JSON

### Response Schema

```json
{
  "status": "healthy|degraded|unhealthy",
  "timestamp": "2025-11-04T10:30:00.000Z",
  "version": "1.4.0",
  "environment": {
    "debug_mode": false,
    "api_title": "Digital Mind API"
  },
  "uptime": {
    "seconds": 86400.15,
    "formatted": "24h 0m 0s"
  },
  "system": {
    "cpu_percent": 35.2,
    "memory_percent": 62.1,
    "disk_percent": 45.8
  },
  "database": {
    "connected": true,
    "response_time_ms": 12.5,
    "database_name": "digital_mind_model",
    "collections_count": 25,
    "collections": ["DigitalMindModel", "KammaLogEntry", ...],
    "document_counts": {
      "DigitalMindModel": 150,
      "KammaLogEntry": 5000,
      "TrainingLog": 250
    }
  }
}
```

### Health Status Levels

**Healthy** ✅
- Database connected
- CPU usage < 80%
- Memory usage < 80%
- All critical services operational

**Degraded** ⚠️
- Database connected but slow (> 100ms)
- CPU usage 80-90%
- Memory usage 80-90%
- Non-critical service issues

**Unhealthy** ❌
- Database disconnected
- CPU usage > 90%
- Memory usage > 90%
- Critical service failures

### Usage Examples

**cURL**:
```bash
curl https://api.yourdomain.com/health | jq
```

**Python**:
```python
import requests

response = requests.get("https://api.yourdomain.com/health")
health = response.json()

if health["status"] == "healthy":
    print("✅ Service is healthy")
elif health["status"] == "degraded":
    print("⚠️  Service degraded:", health)
else:
    print("❌ Service unhealthy:", health)
```

**Health Check Script** (`scripts/check_health.sh`):
```bash
#!/bin/bash
# Health check script for monitoring

API_URL="${1:-http://localhost:8000}"

response=$(curl -s -w "\n%{http_code}" "$API_URL/health")
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n-1)

if [ "$http_code" != "200" ]; then
    echo "❌ Health check failed (HTTP $http_code)"
    exit 1
fi

status=$(echo "$body" | jq -r '.status')

case $status in
    "healthy")
        echo "✅ Service is healthy"
        exit 0
        ;;
    "degraded")
        echo "⚠️  Service is degraded"
        echo "$body" | jq '.'
        exit 1
        ;;
    "unhealthy")
        echo "❌ Service is unhealthy"
        echo "$body" | jq '.'
        exit 2
        ;;
    *)
        echo "❓ Unknown status: $status"
        exit 3
        ;;
esac
```

**Usage**:
```bash
# Local health check
./scripts/check_health.sh http://localhost:8000

# Production health check
./scripts/check_health.sh https://api.yourdomain.com
```

---

## Metrics Collection

### Available Metrics

#### HTTP Request Metrics

**`http_requests_total`** (Counter)
- Description: Total number of HTTP requests
- Labels: `method`, `path`, `status`
- Example:
  ```
  http_requests_total{method="GET",path="/health",status="200"} 1500
  http_requests_total{method="POST",path="/api/models",status="201"} 50
  ```

**`http_request_duration_seconds`** (Histogram)
- Description: HTTP request duration in seconds
- Labels: `method`, `path`
- Buckets: 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10
- Example:
  ```
  http_request_duration_seconds_bucket{method="GET",path="/api/models",le="0.1"} 450
  http_request_duration_seconds_sum{method="GET",path="/api/models"} 23.5
  http_request_duration_seconds_count{method="GET",path="/api/models"} 500
  ```

#### System Resource Metrics

**`system_cpu_percent`** (Gauge)
- Description: System CPU usage percentage
- Updated: Every 30 seconds
- Example: `system_cpu_percent 45.2`

**`system_memory_percent`** (Gauge)
- Description: System memory usage percentage
- Updated: Every 30 seconds
- Example: `system_memory_percent 62.1`

**`system_disk_percent`** (Gauge)
- Description: System disk usage percentage
- Updated: Every 30 seconds
- Example: `system_disk_percent 73.5`

#### Database Metrics

**`db_response_time_ms`** (Gauge)
- Description: Database ping response time in milliseconds
- Updated: Every 30 seconds
- Example: `db_response_time_ms 12.5`

**`db_connected`** (Gauge)
- Description: Database connection status (1=connected, 0=disconnected)
- Updated: Every 30 seconds
- Example: `db_connected 1`

**`db_collection_count`** (Gauge)
- Description: Number of database collections
- Updated: Every 30 seconds
- Example: `db_collection_count 25`

#### Application Metrics

**`app_uptime_seconds`** (Gauge)
- Description: Application uptime in seconds
- Updated: Every 30 seconds
- Example: `app_uptime_seconds 86400.5`

### Accessing Metrics

**Endpoint**: `GET /metrics`  
**Format**: Prometheus text format  
**Authentication**: None (should be restricted in production)

**Example**:
```bash
curl http://localhost:8000/metrics
```

**Output**:
```prometheus
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="GET",path="/health",status="200"} 1500.0

# HELP http_request_duration_seconds Request latency
# TYPE http_request_duration_seconds histogram
http_request_duration_seconds_bucket{method="GET",path="/health",le="0.005"} 1200.0
http_request_duration_seconds_bucket{method="GET",path="/health",le="0.01"} 1450.0
http_request_duration_seconds_sum{method="GET",path="/health"} 7.5
http_request_duration_seconds_count{method="GET",path="/health"} 1500.0

# HELP system_cpu_percent System CPU usage percentage
# TYPE system_cpu_percent gauge
system_cpu_percent 45.2

# HELP system_memory_percent System memory usage percentage
# TYPE system_memory_percent gauge
system_memory_percent 62.1

# HELP db_response_time_ms Database response time in milliseconds
# TYPE db_response_time_ms gauge
db_response_time_ms 12.5

# HELP db_connected Database connection status (1=connected, 0=disconnected)
# TYPE db_connected gauge
db_connected 1.0
```

---

## Prometheus Integration

### Prometheus Setup

#### Installation

**Ubuntu/Debian**:
```bash
# Download Prometheus
cd /tmp
wget https://github.com/prometheus/prometheus/releases/download/v2.45.0/prometheus-2.45.0.linux-amd64.tar.gz
tar xvfz prometheus-*.tar.gz
sudo mv prometheus-2.45.0.linux-amd64 /opt/prometheus
cd /opt/prometheus

# Create Prometheus user
sudo useradd --no-create-home --shell /bin/false prometheus
sudo chown -R prometheus:prometheus /opt/prometheus
```

**macOS**:
```bash
brew install prometheus
```

#### Configuration

**`/opt/prometheus/prometheus.yml`**:
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: 'dmm-production'
    environment: 'production'

# Alerting configuration
alerting:
  alertmanagers:
    - static_configs:
        - targets: ['localhost:9093']

# Load alerting rules
rule_files:
  - "alerts.yml"

# Scrape configurations
scrape_configs:
  # DMM Backend
  - job_name: 'dmm-backend'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
    scrape_interval: 30s
    scrape_timeout: 10s

  # Prometheus self-monitoring
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  # Node Exporter (system metrics)
  - job_name: 'node'
    static_configs:
      - targets: ['localhost:9100']
```

#### Alert Rules

**`/opt/prometheus/alerts.yml`**:
```yaml
groups:
  - name: dmm_backend_alerts
    interval: 30s
    rules:
      # Service down
      - alert: DMM_Backend_Down
        expr: up{job="dmm-backend"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "DMM Backend is down"
          description: "DMM Backend has been down for more than 1 minute"

      # High error rate
      - alert: High_Error_Rate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.01
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High 5xx error rate"
          description: "Error rate is {{ $value }} errors/second"

      # Slow response time
      - alert: Slow_Response_Time
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 0.5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Slow API response time"
          description: "95th percentile response time is {{ $value }}s"

      # High CPU usage
      - alert: High_CPU_Usage
        expr: system_cpu_percent > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage"
          description: "CPU usage is {{ $value }}%"

      # High memory usage
      - alert: High_Memory_Usage
        expr: system_memory_percent > 85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage"
          description: "Memory usage is {{ $value }}%"

      # Database disconnected
      - alert: Database_Disconnected
        expr: db_connected == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Database disconnected"
          description: "MongoDB connection lost"

      # Slow database
      - alert: Slow_Database_Response
        expr: db_response_time_ms > 100
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Slow database response"
          description: "Database response time is {{ $value }}ms"

      # Disk space
      - alert: Low_Disk_Space
        expr: system_disk_percent > 80
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Low disk space"
          description: "Disk usage is {{ $value }}%"

      # Critical disk space
      - alert: Critical_Disk_Space
        expr: system_disk_percent > 90
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Critical disk space"
          description: "Disk usage is {{ $value }}%"
```

#### Start Prometheus

**systemd Service** (`/etc/systemd/system/prometheus.service`):
```ini
[Unit]
Description=Prometheus Monitoring System
After=network.target

[Service]
Type=simple
User=prometheus
Group=prometheus
ExecStart=/opt/prometheus/prometheus \
  --config.file=/opt/prometheus/prometheus.yml \
  --storage.tsdb.path=/opt/prometheus/data \
  --web.console.templates=/opt/prometheus/consoles \
  --web.console.libraries=/opt/prometheus/console_libraries
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Start and enable**:
```bash
sudo systemctl daemon-reload
sudo systemctl enable prometheus
sudo systemctl start prometheus
sudo systemctl status prometheus
```

**Access Prometheus**:
- Web UI: http://localhost:9090
- Targets: http://localhost:9090/targets
- Alerts: http://localhost:9090/alerts

---

## Grafana Dashboards

### Grafana Setup

#### Installation

**Ubuntu/Debian**:
```bash
# Add Grafana repository
sudo apt-get install -y software-properties-common
sudo add-apt-repository "deb https://packages.grafana.com/oss/deb stable main"
wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
sudo apt-get update
sudo apt-get install grafana

# Start Grafana
sudo systemctl enable grafana-server
sudo systemctl start grafana-server
```

**macOS**:
```bash
brew install grafana
brew services start grafana
```

**Access**: http://localhost:3000  
**Default credentials**: admin / admin

#### Add Prometheus Data Source

1. Go to Configuration → Data Sources
2. Click "Add data source"
3. Select "Prometheus"
4. Set URL: `http://localhost:9090`
5. Click "Save & Test"

### DMM Backend Dashboard

#### Dashboard JSON

**File**: `monitoring/grafana-dashboard-dmm-backend.json`

```json
{
  "dashboard": {
    "title": "DMM Backend Monitoring",
    "tags": ["dmm", "backend", "api"],
    "timezone": "browser",
    "panels": [
      {
        "title": "Request Rate",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{method}} {{path}}"
          }
        ],
        "type": "graph"
      },
      {
        "title": "Response Time (95th percentile)",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "{{method}} {{path}}"
          }
        ],
        "type": "graph"
      },
      {
        "title": "Error Rate",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~\"5..\"}[5m])",
            "legendFormat": "5xx errors"
          }
        ],
        "type": "graph"
      },
      {
        "title": "System CPU Usage",
        "targets": [
          {
            "expr": "system_cpu_percent",
            "legendFormat": "CPU %"
          }
        ],
        "type": "graph"
      },
      {
        "title": "System Memory Usage",
        "targets": [
          {
            "expr": "system_memory_percent",
            "legendFormat": "Memory %"
          }
        ],
        "type": "graph"
      },
      {
        "title": "Database Response Time",
        "targets": [
          {
            "expr": "db_response_time_ms",
            "legendFormat": "DB Response (ms)"
          }
        ],
        "type": "graph"
      },
      {
        "title": "Database Status",
        "targets": [
          {
            "expr": "db_connected",
            "legendFormat": "Connected"
          }
        ],
        "type": "stat"
      },
      {
        "title": "Application Uptime",
        "targets": [
          {
            "expr": "app_uptime_seconds / 3600",
            "legendFormat": "Uptime (hours)"
          }
        ],
        "type": "stat"
      }
    ]
  }
}
```

#### Key Dashboard Panels

| Panel | Query | Purpose |
|-------|-------|---------|
| **Request Rate** | `rate(http_requests_total[5m])` | Traffic patterns |
| **Response Time (p95)** | `histogram_quantile(0.95, ...)` | Performance |
| **Error Rate** | `rate(http_requests_total{status=~"5.."}[5m])` | Reliability |
| **CPU Usage** | `system_cpu_percent` | Resource usage |
| **Memory Usage** | `system_memory_percent` | Resource usage |
| **DB Response Time** | `db_response_time_ms` | Database performance |
| **DB Status** | `db_connected` | Database health |
| **Uptime** | `app_uptime_seconds / 3600` | Service availability |

### Import Dashboard

1. Go to Dashboards → Import
2. Upload `grafana-dashboard-dmm-backend.json`
3. Select Prometheus data source
4. Click "Import"

---

## Log Management

### Logging Configuration

#### Log Levels

| Level | Usage | Example |
|-------|-------|---------|
| **DEBUG** | Development debugging | Variable values, detailed flow |
| **INFO** | Normal operations | Request received, action completed |
| **WARNING** | Recoverable issues | Deprecation, rate limit approaching |
| **ERROR** | Application errors | Failed to process request |
| **CRITICAL** | System failures | Database down, service crash |

#### Environment Configuration

**`.env`**:
```bash
# Development
LOG_LEVEL=DEBUG
LOG_FILE=logs/app.log

# Staging
LOG_LEVEL=INFO
LOG_FILE=/var/log/dmm/app.log

# Production
LOG_LEVEL=INFO
LOG_FILE=/var/log/dmm/app.log
```

### Structured JSON Logging

**Log Format**:
```json
{
  "timestamp": "2025-11-04T10:30:00.000Z",
  "level": "INFO",
  "logger": "dmm_backend.main",
  "message": "Request processed successfully",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "method": "POST",
  "path": "/api/models",
  "status_code": 201,
  "duration_ms": 45.2,
  "user_id": "user123",
  "ip_address": "192.168.1.100"
}
```

### Log Rotation

**logrotate** (`/etc/logrotate.d/dmm-backend`):
```
/var/log/dmm/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0644 dmm dmm
    sharedscripts
    postrotate
        systemctl reload dmm-backend
    endscript
}
```

### Centralized Logging (ELK Stack)

#### Filebeat Configuration

**`/etc/filebeat/filebeat.yml`**:
```yaml
filebeat.inputs:
  - type: log
    enabled: true
    paths:
      - /var/log/dmm/app.log
    json.keys_under_root: true
    json.add_error_key: true

output.elasticsearch:
  hosts: ["localhost:9200"]
  index: "dmm-backend-%{+yyyy.MM.dd}"

setup.kibana:
  host: "localhost:5601"
```

#### Kibana Queries

**Search for errors**:
```
level: ERROR OR level: CRITICAL
```

**Search by request ID**:
```
request_id: "550e8400-e29b-41d4-a716-446655440000"
```

**Slow requests (> 1 second)**:
```
duration_ms: >1000
```

**Failed authentication**:
```
message: "authentication failed" OR status_code: 401
```

---

## Alerting

### Alert Channels

#### Slack Integration

**Alertmanager Configuration** (`/opt/prometheus/alertmanager.yml`):
```yaml
global:
  slack_api_url: 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK'

route:
  receiver: 'slack-notifications'
  group_by: ['alertname', 'severity']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h

receivers:
  - name: 'slack-notifications'
    slack_configs:
      - channel: '#alerts'
        title: '{{ .GroupLabels.alertname }}'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'
        send_resolved: true
```

#### Email Alerts

```yaml
receivers:
  - name: 'email-notifications'
    email_configs:
      - to: 'ops@yourdomain.com'
        from: 'alerts@yourdomain.com'
        smarthost: 'smtp.gmail.com:587'
        auth_username: 'alerts@yourdomain.com'
        auth_password: 'your-password'
        headers:
          Subject: 'DMM Alert: {{ .GroupLabels.alertname }}'
```

#### PagerDuty Integration

```yaml
receivers:
  - name: 'pagerduty-critical'
    pagerduty_configs:
      - service_key: 'YOUR_PAGERDUTY_SERVICE_KEY'
        description: '{{ .CommonAnnotations.description }}'
```

### Alert Severity Levels

| Severity | Response Time | Notification | Example |
|----------|---------------|--------------|---------|
| **Critical** | Immediate | PagerDuty + Phone | Service down, DB down |
| **High** | < 15 minutes | PagerDuty + SMS | High error rate, critical resource |
| **Medium** | < 1 hour | Slack + Email | Performance degradation |
| **Low** | < 4 hours | Email | Minor issues, warnings |

---

## Performance Monitoring

### Key Performance Indicators (KPIs)

#### Response Time Targets

| Endpoint Type | Target (p50) | Target (p95) | Target (p99) |
|---------------|--------------|--------------|--------------|
| **Health Check** | < 10ms | < 50ms | < 100ms |
| **Read Operations** | < 50ms | < 200ms | < 500ms |
| **Write Operations** | < 100ms | < 300ms | < 1000ms |
| **Complex Queries** | < 500ms | < 2000ms | < 5000ms |

#### Query Examples

**Average response time (last 5 minutes)**:
```promql
rate(http_request_duration_seconds_sum[5m]) / rate(http_request_duration_seconds_count[5m])
```

**95th percentile response time**:
```promql
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```

**Requests per second**:
```promql
rate(http_requests_total[1m])
```

**Error rate percentage**:
```promql
(rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])) * 100
```

### Performance Testing

**Apache Bench** (Simple load test):
```bash
ab -n 1000 -c 10 https://api.yourdomain.com/health
```

**Locust** (Advanced load test):
```python
# locustfile.py
from locust import HttpUser, task, between

class DMM_User(HttpUser):
    wait_time = between(1, 3)
    
    @task(10)
    def health_check(self):
        self.client.get("/health")
    
    @task(5)
    def get_models(self):
        self.client.get("/api/models", 
                       headers={"X-API-Key": "your-api-key"})
    
    @task(2)
    def create_model(self):
        self.client.post("/api/models",
                        json={"name": "Test Model"},
                        headers={"X-API-Key": "your-api-key"})
```

**Run Locust**:
```bash
locust -f locustfile.py --host=https://api.yourdomain.com
# Open http://localhost:8089
```

---

## Database Monitoring

### MongoDB Monitoring

#### Key Metrics

| Metric | Command | Target |
|--------|---------|--------|
| **Operations/sec** | `db.serverStatus().opcounters` | < 10,000 |
| **Connections** | `db.serverStatus().connections` | < 80% of max |
| **Lock %** | `db.serverStatus().locks` | < 10% |
| **Query Time** | `db.currentOp()` | < 100ms |

#### MongoDB Monitoring Commands

**Server status**:
```javascript
db.serverStatus()
```

**Database stats**:
```javascript
db.stats()
```

**Collection stats**:
```javascript
db.DigitalMindModel.stats()
```

**Current operations**:
```javascript
db.currentOp()
```

**Slow queries** (> 100ms):
```javascript
db.system.profile.find({ millis: { $gt: 100 } }).sort({ ts: -1 }).limit(10)
```

#### Enable Profiling

```javascript
// Enable profiling for slow queries
db.setProfilingLevel(1, { slowms: 100 })

// Enable profiling for all queries
db.setProfilingLevel(2)

// Check profiling status
db.getProfilingStatus()
```

### MongoDB Exporter for Prometheus

**Installation**:
```bash
# Download MongoDB Exporter
wget https://github.com/percona/mongodb_exporter/releases/download/v0.40.0/mongodb_exporter-0.40.0.linux-amd64.tar.gz
tar xvfz mongodb_exporter-*.tar.gz
sudo mv mongodb_exporter /usr/local/bin/

# Create systemd service
sudo tee /etc/systemd/system/mongodb-exporter.service << EOF
[Unit]
Description=MongoDB Exporter
After=network.target

[Service]
Type=simple
User=mongodb-exporter
ExecStart=/usr/local/bin/mongodb_exporter \
  --mongodb.uri=mongodb://monitor:PASSWORD@localhost:27017 \
  --web.listen-address=:9216
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable mongodb-exporter
sudo systemctl start mongodb-exporter
```

**Add to Prometheus** (`prometheus.yml`):
```yaml
scrape_configs:
  - job_name: 'mongodb'
    static_configs:
      - targets: ['localhost:9216']
```

---

## Security Monitoring

### Security Metrics

#### Failed Authentication Attempts

**Monitor**:
```promql
rate(http_requests_total{path="/api/auth/login",status="401"}[5m])
```

**Alert**:
```yaml
- alert: High_Failed_Login_Rate
  expr: rate(http_requests_total{path="/api/auth/login",status="401"}[5m]) > 10
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "High rate of failed login attempts"
```

#### Suspicious Activity

**Rate Limiting Violations**:
```promql
rate(http_requests_total{status="429"}[5m])
```

**Unauthorized Access Attempts**:
```promql
rate(http_requests_total{status="403"}[5m])
```

### Security Logging

**Log security events**:
```python
logger.warning("Failed authentication attempt", extra={
    "event_type": "auth_failed",
    "ip_address": request.client.host,
    "username": username,
    "user_agent": request.headers.get("user-agent")
})
```

### Intrusion Detection

**Fail2Ban Configuration** (`/etc/fail2ban/jail.local`):
```ini
[dmm-backend]
enabled = true
port = http,https
filter = dmm-backend
logpath = /var/log/dmm/app.log
maxretry = 5
bantime = 3600
findtime = 600
```

**Filter** (`/etc/fail2ban/filter.d/dmm-backend.conf`):
```ini
[Definition]
failregex = .*"event_type": "auth_failed".*"ip_address": "<HOST>"
ignoreregex =
```

---

## Troubleshooting

### Common Issues

#### Issue 1: High Memory Usage

**Symptoms**:
- `system_memory_percent > 85%`
- Slow response times
- Out of memory errors

**Diagnosis**:
```bash
# Check memory usage
free -h
ps aux --sort=-%mem | head -10

# Check application memory
systemctl status dmm-backend
journalctl -u dmm-backend -n 100
```

**Solutions**:
1. Restart application: `sudo systemctl restart dmm-backend`
2. Increase worker count in `.env`: `WORKERS=4` → `WORKERS=2`
3. Add more RAM
4. Optimize database queries
5. Implement caching

---

#### Issue 2: Database Connection Issues

**Symptoms**:
- `db_connected == 0`
- 500 errors
- "Database connection lost" in logs

**Diagnosis**:
```bash
# Check MongoDB status
sudo systemctl status mongod
mongosh --eval "db.adminCommand('ping')"

# Check connections
mongosh --eval "db.serverStatus().connections"
```

**Solutions**:
1. Restart MongoDB: `sudo systemctl restart mongod`
2. Check MongoDB logs: `sudo journalctl -u mongod -n 100`
3. Verify credentials in `.env`
4. Check network connectivity
5. Increase connection pool size

---

#### Issue 3: High CPU Usage

**Symptoms**:
- `system_cpu_percent > 80%`
- Slow response times
- Request timeouts

**Diagnosis**:
```bash
# Check CPU usage
top
htop

# Check application CPU
ps aux --sort=-%cpu | head -10

# Check slow queries
mongosh --eval "db.system.profile.find({millis: {\$gt: 100}}).sort({ts: -1}).limit(10)"
```

**Solutions**:
1. Optimize slow queries
2. Add database indexes
3. Reduce worker count
4. Scale horizontally (add more servers)
5. Implement caching

---

#### Issue 4: Slow Response Times

**Symptoms**:
- p95 response time > 500ms
- User complaints
- Timeout errors

**Diagnosis**:
```bash
# Check response times
curl -w "@curl-format.txt" -o /dev/null -s https://api.yourdomain.com/health

# Check database response time
mongosh --eval "db.runCommand({ping: 1})"

# Check slow queries
mongosh --eval "db.system.profile.find({millis: {\$gt: 100}}).sort({ts: -1}).limit(10)"
```

**curl-format.txt**:
```
time_namelookup:  %{time_namelookup}s\n
time_connect:     %{time_connect}s\n
time_appconnect:  %{time_appconnect}s\n
time_pretransfer: %{time_pretransfer}s\n
time_redirect:    %{time_redirect}s\n
time_starttransfer: %{time_starttransfer}s\n
----------\n
time_total:       %{time_total}s\n
```

**Solutions**:
1. Add database indexes
2. Optimize queries
3. Implement caching (Redis)
4. Use CDN for static assets
5. Scale horizontally

---

## Best Practices

### Monitoring Best Practices

#### 1. Define SLOs (Service Level Objectives)

**Availability**: 99.9% uptime (43 minutes downtime/month)
**Response Time**: 95% of requests < 500ms
**Error Rate**: < 1% of requests fail

#### 2. Alert Fatigue Prevention

- Set appropriate thresholds
- Use alert grouping
- Implement escalation policies
- Regular alert review and tuning

#### 3. Regular Health Checks

**External Monitoring**:
- UptimeRobot: https://uptimerobot.com
- Pingdom: https://www.pingdom.com
- StatusCake: https://www.statuscake.com

**Frequency**:
- Health checks: Every 1 minute
- Metrics scraping: Every 30 seconds
- Log aggregation: Real-time

#### 4. Capacity Planning

**Review Monthly**:
- Resource usage trends
- Growth projections
- Scaling requirements

**Thresholds**:
- CPU: Plan scaling at 70% sustained
- Memory: Plan scaling at 75% sustained
- Disk: Plan expansion at 70% usage

#### 5. Documentation

- Document all alerts
- Maintain runbooks
- Update dashboards
- Regular review meetings

### Logging Best Practices

#### 1. Structured Logging

**Good**:
```python
logger.info("User created", extra={
    "user_id": user.id,
    "username": user.username,
    "ip_address": request.client.host
})
```

**Bad**:
```python
logger.info(f"User {user.username} created from {request.client.host}")
```

#### 2. Correlation IDs

**Include request ID in all logs**:
```python
logger.info("Processing request", extra={
    "request_id": request.headers.get("X-Request-ID"),
    "endpoint": request.url.path
})
```

#### 3. Sensitive Data

**Never log**:
- Passwords
- API keys
- JWT tokens
- Credit card numbers
- Personal identifiable information (PII)

**Mask if necessary**:
```python
masked_email = email[:2] + "***@" + email.split("@")[1]
logger.info("Password reset requested", extra={"email": masked_email})
```

#### 4. Log Retention

| Environment | Retention | Reason |
|-------------|-----------|--------|
| **Development** | 7 days | Debugging |
| **Staging** | 30 days | Testing |
| **Production** | 90 days | Compliance, debugging |
| **Audit Logs** | 1 year | Compliance |

---

## Summary

### Monitoring Checklist

**Health Checks** ✅
- [x] `/health` endpoint implemented
- [x] System metrics included
- [x] Database status included
- [x] Response time tracking

**Metrics** ✅
- [x] Prometheus integration
- [x] HTTP request metrics
- [x] System resource metrics
- [x] Database metrics
- [x] Application metrics

**Logging** ✅
- [x] Structured JSON logging
- [x] Log levels configured
- [x] Log rotation setup
- [x] Centralized logging (optional)

**Alerting** ✅
- [x] Alert rules defined
- [x] Notification channels configured
- [x] Escalation policies
- [x] On-call rotation

**Dashboards** ✅
- [x] Grafana dashboard created
- [x] Key metrics visualized
- [x] Real-time monitoring
- [x] Historical data

### Next Steps

1. **Set up Prometheus** (30 minutes)
2. **Configure Grafana** (30 minutes)
3. **Set up alerting** (1 hour)
4. **Test alerts** (30 minutes)
5. **Create runbooks** (2 hours)
6. **Regular review** (monthly)

---

**Document Owner**: DevOps Team  
**Last Reviewed**: 4 November 2568 (2025)  
**Next Review**: 4 December 2568 (2025)
