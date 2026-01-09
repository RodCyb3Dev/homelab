# Monitoring Stack Verification

## Overview
This document verifies that the monitoring stack is properly configured to collect logs, metrics, and telemetry data in Grafana.

## Components

### 1. Prometheus (Metrics Collection)
**Network:** `grafana-monitoring`  
**Port:** 9090  
**Configuration:** `config/prometheus/prometheus.yml`

#### Scrape Targets Configured:
- ✅ **Prometheus** (self-monitoring) - `localhost:9090`
- ✅ **CrowdSec** - `crowdsec:6060` (on both `caddy-proxy` and `grafana-monitoring` networks)
- ✅ **Authelia** - `authelia:9959` (metrics endpoint exposed, on both networks)
- ✅ **Node Exporter** - `node-exporter:9100` (system metrics)
- ✅ **cAdvisor** - `cadvisor:8080` (container metrics)
- ✅ **Grafana** - `grafana:3000` (Grafana metrics)
- ✅ **Loki** - `loki:3100` (Loki metrics)

#### Network Connectivity:
- Prometheus can reach all targets via `grafana-monitoring` network
- CrowdSec and Authelia are on both `caddy-proxy` and `grafana-monitoring` networks

### 2. Loki (Log Aggregation)
**Network:** `grafana-monitoring`  
**Port:** 3100  
**Configuration:** `config/loki/loki-config.yml`

**Features:**
- ✅ Log retention: 30 days (720h)
- ✅ Filesystem storage backend
- ✅ Metrics endpoint exposed for Prometheus

### 3. Promtail (Log Shipper)
**Network:** `grafana-monitoring`  
**Port:** 9080  
**Configuration:** `config/promtail/promtail-config.yml`

#### Log Sources:
- ✅ **Docker Container Logs** - Via Docker socket (`/var/run/docker.sock`)
  - Automatically discovers all containers
  - Labels: `container`, `stream`, `service`
- ✅ **System Logs** - `/var/log/*.log`
- ✅ **Syslog** - `/var/log/syslog` (SSH, auth, etc.)

**Target:** Ships logs to `http://loki:3100/loki/api/v1/push`

### 4. Grafana (Visualization)
**Network:** `grafana-monitoring` and `caddy-proxy`  
**Port:** 3000  
**Configuration:** `config/grafana/provisioning/`

#### Data Sources (Auto-provisioned):
- ✅ **Prometheus** - `http://prometheus:9090`
  - Default datasource
  - Query timeout: 60s
  - Time interval: 30s
- ✅ **Loki** - `http://loki:3100`
  - Max lines: 1000
  - Derived fields for trace correlation

#### Dashboard Provisioning:
- ✅ Dashboards folder: `/etc/grafana/provisioning/dashboards/json`
- ✅ Security dashboards folder: `/etc/grafana/provisioning/dashboards/security`
- ✅ Auto-update enabled (30s interval)

### 5. Node Exporter (System Metrics)
**Network:** `grafana-monitoring`  
**Port:** 9100

**Metrics Collected:**
- CPU usage
- Memory usage
- Disk I/O
- Network I/O
- Filesystem metrics
- System load

### 6. cAdvisor (Container Metrics)
**Network:** `grafana-monitoring`  
**Port:** 8080

**Metrics Collected:**
- Container CPU usage
- Container memory usage
- Container network I/O
- Container filesystem usage
- Container process counts

## Data Flow

```
┌─────────────────┐
│  Applications   │
│  (Docker)       │
└────────┬────────┘
         │ stdout/stderr logs
         ▼
┌─────────────────┐     ┌──────────────┐     ┌──────────┐
│    Promtail     │────▶│     Loki     │────▶│ Grafana  │
│  (Log Shipper)  │     │ (Log Store) │     │(Logs UI) │
└─────────────────┘     └──────────────┘     └──────────┘

┌─────────────────┐     ┌──────────────┐     ┌──────────┐
│ Node Exporter   │     │              │     │          │
│   cAdvisor      │────▶│  Prometheus  │────▶│ Grafana  │
│   CrowdSec      │     │  (Metrics)   │     │(Metrics) │
│   Authelia      │     │              │     │          │
└─────────────────┘     └──────────────┘     └──────────┘
```

## Verification Checklist

### Metrics Collection
- [x] Prometheus scraping Prometheus itself
- [x] Prometheus scraping CrowdSec (port 6060)
- [x] Prometheus scraping Authelia (port 9959)
- [x] Prometheus scraping Node Exporter (port 9100)
- [x] Prometheus scraping cAdvisor (port 8080)
- [x] Prometheus scraping Grafana (port 3000)
- [x] Prometheus scraping Loki (port 3100)

### Log Collection
- [x] Promtail discovering Docker containers via socket
- [x] Promtail shipping to Loki
- [x] System logs being collected
- [x] Syslog being collected

### Visualization
- [x] Grafana has Prometheus datasource configured
- [x] Grafana has Loki datasource configured
- [x] Dashboard provisioning configured

### Network Connectivity
- [x] All monitoring services on `grafana-monitoring` network
- [x] CrowdSec and Authelia accessible from Prometheus
- [x] Promtail can access Docker socket
- [x] Promtail can reach Loki

## Accessing Monitoring

### Grafana
- **URL:** `https://grafana.rodneyops.com`
- **Authentication:** Authelia (2FA required)
- **Default Datasources:** Prometheus and Loki

### Prometheus
- **URL:** Accessible via Grafana or directly at `http://prometheus:9090` (internal)
- **Targets:** Check `/targets` endpoint to verify all scrape targets are UP

### Loki
- **URL:** Accessible via Grafana or directly at `http://loki:3100` (internal)
- **Query API:** `/loki/api/v1/query`

## Next Steps

1. **Import Dashboards:**
   - Import Node Exporter dashboard (ID: 1860)
   - Import Docker dashboard (ID: 179)
   - Import Loki dashboard (ID: 13639)
   - Create custom dashboards for CrowdSec and Authelia

2. **Enable Alerting (Optional):**
   - Configure Alertmanager
   - Set up alert rules in Prometheus
   - Configure notification channels in Grafana

3. **Caddy Metrics (Optional):**
   - Install Caddy metrics plugin
   - Add Caddy scrape target to Prometheus

4. **Docker Metrics (Optional):**
   - Enable Docker metrics in `/etc/docker/daemon.json`:
     ```json
     {
       "metrics-addr": "0.0.0.0:9323",
       "experimental": true
     }
     ```
   - Uncomment Docker scrape target in Prometheus config

## Troubleshooting

### No Metrics in Grafana
1. Check Prometheus targets: `http://prometheus:9090/targets`
2. Verify network connectivity: `docker network inspect homelab_grafana-monitoring`
3. Check service logs: `docker logs prometheus`

### No Logs in Grafana
1. Check Promtail logs: `docker logs promtail`
2. Verify Loki is receiving logs: `docker logs loki`
3. Check Docker socket access: `docker exec promtail ls -la /var/run/docker.sock`

### Services Not Discoverable
1. Verify services are on correct networks
2. Check service names match Prometheus config
3. Verify ports are exposed/accessible

