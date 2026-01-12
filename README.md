# Secure Homelab Infrastructure

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Docker](https://img.shields.io/badge/docker-required-blue)
![Security](https://img.shields.io/badge/security-hardened-brightgreen)

A production-ready, maximum-security homelab infrastructure with defense-in-depth architecture, zero-trust access controls, and full observability.

## 🎯 Features

### Security

- ✅ **6-Layer Defense-in-Depth** - Cloudflare WAF, Caddy, CrowdSec, Authelia, Fail2ban, Tailscale
- ✅ **Zero-Trust Access Control** - SSO with 2FA for all services
- ✅ **Automated Threat Detection** - CrowdSec IDS/IPS with community blocklists
- ✅ **TLS 1.3 Encryption** - Automatic SSL certificates via Let's Encrypt
- ✅ **Security Scanning** - Automated vulnerability scans via GitHub Actions

### Infrastructure

- ✅ **Docker-based** - Containerized services with resource limits
- ✅ **Network Segmentation** - Isolated networks for public/private/monitoring
- ✅ **High Availability** - Health checks and automatic restarts
- ✅ **Resource Optimized** - Runs on 4GB RAM Hetzner server
- ✅ **Hetzner Storage Box** - Mounted network storage for media

### Observability

- ✅ **Full Metrics Stack** - Prometheus + Grafana + cAdvisor
- ✅ **Centralized Logging** - Loki + Promtail for log aggregation
- ✅ **Real-time Alerts** - Gotify push notifications
- ✅ **Service Monitoring** - Uptime Kuma for availability tracking

### Automation

- ✅ **CI/CD Pipeline** - Automated deployments via GitHub Actions
- ✅ **Automated Backups** - Daily backups to Storage Box
- ✅ **Zero-Downtime Updates** - Rolling deployments
- ✅ **Automated Security Scans** - Weekly vulnerability checks
- ✅ **Python CLI Tools** - Modular homelab management tools for storage, backups, health checks, and performance monitoring

<!-- AUTO-GENERATED STATS - DO NOT EDIT MANUALLY -->
<!-- AUTO-GENERATED STATS - DO NOT EDIT MANUALLY -->
<!-- AUTO-GENERATED STATS - DO NOT EDIT MANUALLY -->
<!-- AUTO-GENERATED STATS - DO NOT EDIT MANUALLY -->
<!-- STATS_START -->

**Last Updated**: 2026-01-12 12:04:32 UTC | **Commit**: [0769922](https://github.com/RodCyb3Dev/homelab/commit/0769922) | **Branch**: main

## 📊 Quick Statistics

| **Metric**        | **Count** | **Details**                                              |
| ----------------- | --------- | ------------------------------------------------------------- |
| **Total Files**   | 156       | [📈 Full Analysis](../../wiki/Project-Statistics)             |
| **Code Lines**    | 18495+   | [🏗️ Architecture Overview](../../wiki/Architecture-Overview) |
| **Python**        | 39 files | 4552 lines                                                  |
| **YAML**          | 45 files  | 7419 lines                                                   |
| **Shell Scripts** | 4 files | 357 lines                                                  |
| **Documentation** | 20 files  | [📚 Documentation Index](../../wiki/Documentation-Index)      |
| **Docker Services** | 0 services | 7 compose files |

### 🚀 Key Components

| **Component**        | **Files** | **Purpose**         |
| -------------------- | --------- | ------------------- |
| **Python Tools**     | 39       | CLI & automation     |
| **Ansible Playbooks** | 19       | Infrastructure as code   |
| **Config Directories**   | 32        | Service configurations |

---

📚 **[View Complete Analytics in Wiki →](../../wiki/Home)**  
🔍 **[Detailed Statistics →](../../wiki/Project-Statistics)**  
🏗️ **[Architecture Overview →](../../wiki/Architecture-Overview)**

<!-- STATS_END -->

## 📋 Table of Contents

- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Services](#services)
- [Configuration](#configuration)
- [Deployment](#deployment)
- [Jellyfin Performance Optimization](#-jellyfin-performance-optimization)
- [Monitoring](#monitoring)
- [Security](#security)
- [Maintenance](#maintenance)
- [Troubleshooting](#troubleshooting)
- [Documentation](#-documentation)

## 🏗 Architecture

```
Internet
    ↓
Cloudflare CDN/WAF (Layer 1)
    ↓
Caddy Reverse Proxy (Layer 2)
    ↓
CrowdSec IDS/IPS (Layer 3)
    ↓
Authelia SSO + 2FA (Layer 4)
    ↓
┌────────────────────────────┬─────────────────────────────┐
│   Public Services          │   Private Services          │
│   (HTTPS + Auth)           │   (Tailscale Only)          │
├────────────────────────────┼─────────────────────────────┤
│ • Grafana (Monitoring)     │ • Jellyfin (Media Server)   │
│ • Caddy Admin (if enabled)  │ • Sonarr, Radarr (TV/Movies)│
│ • Gotify (Notifications)   │ • Prowlarr (Indexers)       │
│ • Status Page              │ • qBittorrent (Downloads)   │
│                            │ • Portainer (Management)    │
│                            │ • Homarr (Dashboard)        │
└────────────────────────────┴─────────────────────────────┘
         ↓                              ↓
    Monitoring Stack            Hetzner Storage Box
    (Prometheus/Loki)           (1TB Network Storage)
```

### Network Topology

- **Public Network** (`172.20.0.0/24`) - Internet-facing services
- **Private Network** (`172.21.0.0/24`) - Tailscale-only services
- **Monitoring Network** (`172.22.0.0/24`) - Observability stack
- **Security Network** (`172.23.0.0/24`) - Security services

## 🚀 Quick Start

### Prerequisites

- Ubuntu 22.04 LTS server
- Docker 20.10+ and Docker Compose 2.12+
- Domain name with Cloudflare DNS
- Hetzner Storage Box (optional but recommended)
- Tailscale account
- GitHub account (for CI/CD)

### Initial Setup

1. **Clone the repository:**

   ```bash
   git clone https://github.com/your-username/homelab.git /opt/homelab
   cd /opt/homelab
   ```

2. **Configure environment:**

   ```bash
   # Copy environment template
   cp .env.example .env

   # Edit with your values
   nano .env
   ```

3. **Generate secrets:**

   ```bash
   make generate-secrets
   make setup-acme
   ```

4. **Mount Storage Box (optional):**

   ```bash
   sudo bash scripts/setup-storage-box.sh
   ```

5. **Deploy infrastructure:**

   ```bash
   make up
   ```

6. **Verify deployment:**
   ```bash
   make health
   ```

## 📦 Services

### Services Exposed Through Caddy (Protected by Authelia)

These services are accessible via HTTPS through Caddy reverse proxy and protected by Authelia SSO:

| Service           | URL                           | Purpose                  | Authentication     |
| ----------------- | ----------------------------- | ------------------------ | ------------------ |
| Caddy Admin       | `https://caddy.rodneyops.com`   | Reverse proxy monitoring | 2FA (Admins only)  |
| Authelia          | `https://auth.rodneyops.com`    | SSO authentication       | Password + 2FA     |
| Grafana           | `https://grafana.rodneyops.com` | Metrics & dashboards     | 2FA                |
| Uptime Kuma       | `https://status.rodneyops.com`  | Service status page      | 2FA                |
| Gotify            | `https://rodify.rodneyops.com`  | Push notifications       | 1FA                |
| Navidrome         | `https://navidrome.rodneyops.com` | Music streaming server  | 1FA                |
| Audiobookshelf    | `https://audiobooks.rodneyops.com` | Audiobook & podcast server | 1FA            |

**Note:** All services above require Authelia authentication. Health check endpoints are bypassed for monitoring.

### Services on Tailscale Only (Not in Authelia Config)

These services are only accessible via Tailscale VPN and are not exposed through Caddy:

| Service     | Tailscale URL                          | Purpose              |
| ----------- | -------------------------------------- | -------------------- |
| Jellyfin    | `https://jellyfin.kooka-lake.ts.net`   | Media streaming      |
| Jellyseerr   | `https://jellyseerr.kooka-lake.ts.net` | Media request management |
| Sonarr      | `https://sonarr.kooka-lake.ts.net`     | TV show management   |
| Radarr      | `https://radarr.kooka-lake.ts.net`     | Movie management     |
| Prowlarr    | `https://prowlarr.kooka-lake.ts.net`   | Indexer management   |
| qBittorrent | `https://qbittorrent.kooka-lake.ts.net` | Torrent client       |
| Lidarr      | `https://lidarr.kooka-lake.ts.net`     | Music management     |
| LazyLibrarian | `https://lazylibrarian.kooka-lake.ts.net` | Book management      |
| Bazarr      | `https://bazarr.kooka-lake.ts.net`     | Subtitle management  |
| Flaresolverr| `https://flaresolverr.kooka-lake.ts.net` | Cloudflare bypass proxy |
| Homarr      | `https://homarr.kooka-lake.ts.net`     | Service dashboard    |
| Portainer   | `https://portainer.kooka-lake.ts.net`  | Container management |

### Security Services

| Service  | Purpose                       | Port |
| -------- | ----------------------------- | ---- |
| CrowdSec | IDS/IPS & threat intelligence | 6060 |
| Fail2ban | System intrusion prevention   | -    |
| Authelia | SSO & 2FA authentication      | 9091 |

### Monitoring Services

| Service       | Purpose            | Port |
| ------------- | ------------------ | ---- |
| Prometheus    | Metrics collection | 9090 |
| Grafana       | Visualization      | 3000 |
| Loki          | Log aggregation    | 3100 |
| Promtail      | Log shipping       | 9080 |
| Node Exporter | System metrics     | 9100 |
| cAdvisor      | Container metrics  | 8080 |

## ⚙️ Configuration

### Environment Variables

Key environment variables in `.env`:

```bash
# General
TZ=Europe/Helsinki
DOMAIN=rodneyops.com
PUID=1000
PGID=1000

# Hetzner Storage Box
STORAGE_BOX_PASSWORD=your_password

# Cloudflare
CF_API_TOKEN=your_token

# Grafana
GRAFANA_ADMIN_PASSWORD=secure_password

# CrowdSec
CROWDSEC_ENROLL_KEY=your_key
CROWDSEC_BOUNCER_KEY=your_api_key

# Tailscale
TAILSCALE_AUTH_KEY=tskey-auth-xxxxx
```

See [`.env.example`](.env.example) for complete list.

### Caddy Configuration

- Caddyfile: [`Caddyfile`](Caddyfile)
- See [Caddy Migration Guide](docs/CADDY_MIGRATION.md) for details

### Authelia Configuration

- Main config: [`config/authelia/configuration.yml`](config/authelia/configuration.yml)
- Users: [`config/authelia/users_database.yml`](config/authelia/users_database.yml)

Generate password hash:

```bash
docker run --rm authelia/authelia:latest authelia crypto hash generate argon2 --password 'YourPassword123!'
```

### CrowdSec Configuration

- Acquisitions: [`config/crowdsec/acquis.yaml`](config/crowdsec/acquis.yaml)
- Profiles: [`config/crowdsec/profiles.yaml`](config/crowdsec/profiles.yaml)

Generate bouncer API key:

```bash
docker exec crowdsec cscli bouncers add caddy-bouncer
```

### Hetzner Storage Box

The Storage Box is mounted at `/mnt/storagebox` via WebDAV (HTTPS) and provides network storage for media files and backups. The Storage Box has been upgraded to **5TB capacity** (upgrade may take 15-30 minutes to fully propagate).

**Directory Structure:**

```
/mnt/storagebox/
├── movies/          # Jellyfin - Movies
├── tv-shows/        # Jellyfin - TV Shows
├── photos/          # Jellyfin - Photos
├── books/           # Jellyfin - Books/eBooks
├── home-videos/     # Jellyfin - Home Videos
├── music/           # Navidrome - Music streaming
├── audiobooks/      # Audiobookshelf - Audiobooks
├── podcasts/        # Audiobookshelf - Podcasts
├── downloads/       # Downloads (optional)
├── media/           # Other media (optional)
└── backups/         # Automated backups
```

**Mount Configuration:**

- **Protocol**: WebDAV (HTTPS on port 443)
- **Mount Point**: `/mnt/storagebox`
- **Credentials**: `/root/.davfs2_secrets`
- **Auto-mount**: Systemd service (recommended) or `/etc/fstab`

**Important Note:**

> ⚠️ **Auto-mount on boot may require manual intervention** because davfs2 can prompt for credentials. If the mount fails on boot, manually mount with `sudo mount /mnt/storagebox` or use the provided systemd service for reliable automatic mounting.

**Setup:**

```bash
# Setup systemd service for automatic mounting (recommended)
./scripts/setup-storagebox-systemd.sh

# Or manually:
sudo cp systemd/storagebox-mount.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable storagebox-mount.service
sudo systemctl start storagebox-mount.service

# Manual mount (if needed)
sudo mount /mnt/storagebox
# Or
sudo systemctl start storagebox-mount.service

# Check mount status
df -h | grep storagebox

# Verify directories
ls -lah /mnt/storagebox/

# Check service status
sudo systemctl status storagebox-mount.service
```

See [Storage Box Setup Guide](docs/STORAGE_BOX.md) for detailed configuration.

## 🚢 Deployment

### Prerequisites

- **Server**: Hetzner Cloud (3 vCPU, 4GB RAM, Ubuntu 22.04+)
- **Domain**: Configured with Cloudflare DNS
- **Accounts**: Cloudflare, Tailscale, CrowdSec, GitHub
- **1Password**: CLI installed with `homelab-env` vault

### Pre-Deployment Checklist

1. **Secrets Setup:**

   ```bash
   # Verify 1Password secrets
   ./scripts/verify-secrets.sh

   # Setup Git hooks
   make setup-git-hooks
   ```

2. **Server Preparation:**

   ```bash
   # SSH into server
   ssh root@95.216.176.147

   # Install Docker
   curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh

   # Configure firewall
   ufw allow 22,80,443/tcp && ufw enable
   ```

3. **Cloudflare API Token:**
   - Create token at https://dash.cloudflare.com/profile/api-tokens
   - Permissions: Zone DNS Edit, Zone Read
   - Save to: `config/caddy/cf-token` (chmod 600)

### Deployment Methods

#### Option 0: Automated Server & Storage Box Setup (New Servers)

**Create a complete Hetzner server and Storage Box automatically:**

This playbook creates a new Hetzner Cloud server, Storage Box, and configures everything with security best practices.

```bash
# Setup required variables in ansible/vault.yml
# Get your Hetzner Cloud API token from: https://console.hetzner.cloud/
# Required variables:
#   - vault_hetzner_api_token (or HETZNER_API_TOKEN env var)
#   - vault_server_name (default: "homelab-server")
#   - vault_server_location (default: "hel1")
#   - vault_server_type (default: "cpx22")
#   - vault_storage_box_name (default: "homelab-storage")
#   - vault_storage_box_type (default: "bx11")
#   - vault_ssh_key_path (default: "~/.ssh/ansible_key.pub")
#   - vault_deploy_user (default: "rodkode")

# Or use environment variable
export HETZNER_API_TOKEN="your-token-here"

# Run the setup playbook
make ansible-setup-server
```

**What it does:**

1. ✅ **Creates Hetzner Cloud Server** via API
   - Configures with cloud-init (Docker, Docker Compose, security hardening)
   - Sets up SSH hardening, UFW firewall, Fail2ban
   - Applies SOC best practices (defense-in-depth)

2. ✅ **Creates Hetzner Storage Box** via API
   - Automatically resets password and retrieves credentials
   - Configures WebDAV mount with systemd automount
   - Creates directory structure (movies, tv-shows, music, etc.)

3. ✅ **Configures Server**
   - Sets up Storage Box mount
   - Configures systemd services
   - Prepares for homelab deployment

**After setup:**

1. Update `ansible/inventory.yml` with the new server IP
2. Run: `make ansible-deploy-core`
3. Configure services

**See [Server Setup Guide](ansible/playbooks/setup-server.yml) for details.**

#### Option 1: Ansible (Recommended) - Infrastructure as Code

**Local Deployment:**

```bash
# Install Ansible
make ansible-install

# Test connection
make ansible-ping

# Deploy (requires environment variables)
export STORAGE_BOX_PASSWORD="your-password"
export CROWDSEC_ENROLL_KEY="your-key"
export CROWDSEC_BOUNCER_KEY="your-key"
export GRAFANA_ADMIN_PASSWORD="your-password"
export GOTIFY_ADMIN_PASSWORD="your-password"
export TS_AUTHKEY="your-key"

make ansible-deploy

# Or use Ansible Vault for secrets
make ansible-vault-create
make ansible-deploy
```

**Benefits:**

- Infrastructure as Code (IaC)
- Idempotent deployments
- Config file management
- Works with existing Caddy/Tailscale setup
- No conflicts with docker-compose
- Easy rollback and verification

**See [ansible/README.md](ansible/README.md) for detailed documentation.**

#### Option 2: GitHub Actions (CI/CD) - Automated

The GitHub Actions workflow automatically uses Ansible for deployment:

1. **Setup GitHub Secrets:**
   - `HETZNER_SSH_HOST` - Hetzner server IP (95.216.176.147)
   - `HETZNER_SSH_USER` - SSH username (deploy)
   - `HETZNER_SSH_KEY` - SSH private key (corresponds to `github_key.pub` on server)
   - `SSH_PORT` - SSH port (22, optional)
   - `STORAGE_BOX_PASSWORD` - Storage box password
   - `CROWDSEC_ENROLL_KEY` - CrowdSec enrollment key
   - `CROWDSEC_BOUNCER_KEY` - CrowdSec bouncer key
   - `GRAFANA_ADMIN_USER` - Grafana admin user
   - `GRAFANA_ADMIN_PASSWORD` - Grafana admin password
   - `GOTIFY_ADMIN_USER` - Gotify admin user
   - `GOTIFY_ADMIN_PASSWORD` - Gotify admin password
   - `TS_AUTHKEY` - Tailscale auth key
   - `GOTIFY_URL` - Gotify notification URL
   - `GOTIFY_TOKEN` - Gotify notification token

2. **Deploy:**
   ```bash
   git push origin main
   ```

   The workflow will:
   - Run security scans
   - Validate configuration
   - Deploy with Ansible (syncs configs, manages secrets, deploys services)
   - Verify service health
   - Send notifications

#### Option 3: Docker Compose (Manual)

```bash
# Start all services
make up

# View logs
make logs

# Check health
make health

# Restart services
make restart
```


The CI/CD pipeline automatically:

- Runs security scans (gitleaks, yamllint, shellcheck)
- Validates configuration
- Deploys with Ansible (syncs configs, manages secrets, deploys services)
- Verifies service health
- Sends notifications

## 📊 Monitoring

### Access Dashboards

- **Grafana**: https://grafana.rodneyops.com
- **Prometheus**: http://localhost:9090 (internal)
- **Caddy**: https://caddy.rodneyops.com (if admin enabled)

### Grafana Dashboards

Pre-configured dashboards:

1. **Infrastructure Overview** - All services, resource usage
2. **Security Dashboard** - CrowdSec stats, Fail2ban, blocked IPs
3. **Caddy Metrics** - Request patterns, response times (if enabled)
4. **Media Stack** - Jellyfin, \*arr services health

### Alerts

Grafana alerts are configured for:

- Service down > 2 minutes
- CPU > 85% for 5 minutes
- Disk > 90%
- Memory > 90%
- SSL certificate expiring < 7 days
- CrowdSec > 50 bans/hour

Alerts are sent to Gotify.

## 🔒 Security

### Defense-in-Depth (6 Layers)

1. **Cloudflare** - DDoS protection, WAF, rate limiting, bot management
2. **Caddy** - TLS 1.3, security headers, automatic HTTPS, request validation
3. **CrowdSec** - IDS/IPS, threat intelligence, automatic IP blocking
4. **Authelia** - SSO, 2FA (TOTP), session management, access control
5. **Fail2ban** - SSH protection, auth failure blocking, system hardening
6. **Tailscale** - Zero-trust VPN for private services

### Access Control

- **Public services** require Authelia 2FA
- **Admin services** require 2FA + IP whitelist
- **Private services** require Tailscale VPN
- **SSH** key-based authentication only

### Security Features

✅ **Secrets Management** - 1Password integration, no hardcoded secrets
✅ **Code Quality** - Pre-commit hooks, gitleaks, automated scanning
✅ **Network Segmentation** - Isolated networks for public/private/monitoring
✅ **Resource Limits** - All containers have CPU/memory limits
✅ **Regular Scans** - Weekly vulnerability scans via GitHub Actions
✅ **Automated Backups** - Daily backups to Hetzner Storage Box
✅ **Audit Logging** - All access logged to Loki

See [Security Guide](docs/SECURITY.md) for complete security documentation and [Security Checklist](docs/SECURITY.md#pre-deployment-security-checklist) before production deployment.

## 🛠 Maintenance

### Backups

**Automated backups** run daily at 03:00 UTC via GitHub Actions.

Manual backup:

```bash
make backup
```

Restore from backup:

```bash
make restore
```

### Updates

**Automated updates** run daily at 02:00 UTC via GitHub Actions.

Manual update:

```bash
make update
```

### Common Tasks

```bash
# View CrowdSec decisions (bans)
make crowdsec-decisions

# View CrowdSec metrics
make crowdsec-metrics

# Add CrowdSec bouncer
make crowdsec-add-bouncer

# View Authelia users
make authelia-users

# View service status
make ps

# View resource usage
docker stats
```

## 📋 Logging & Log Access

### Log Architecture

All services follow Docker best practices by logging to **stdout/stderr**, which Docker captures automatically. This provides:

- ✅ **Automatic log rotation** - Docker handles rotation based on size
- ✅ **Automatic compression** - Logs are compressed when rotated
- ✅ **Centralized access** - All logs accessible via `docker logs`
- ✅ **Monitoring integration** - Promtail automatically collects logs via Docker socket

### Docker Log Configuration

Docker log rotation is configured per-service in `docker-compose.yml`:

```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"      # Rotate when log reaches 10MB
    max-file: "3"        # Keep 3 rotated files (30MB total)
    compress: "true"     # Compress rotated logs (gzip)
```

**Default Docker daemon settings** (if not specified per-service):
- Location: `/var/lib/docker/containers/<container-id>/<container-id>-json.log`
- Rotation: Managed by Docker daemon
- Compression: Enabled by default

### Accessing Logs

#### View Logs via Docker CLI

```bash
# View Caddy logs (last 100 lines)
docker logs caddy --tail 100

# Follow Caddy logs in real-time
docker logs caddy -f

# View logs with timestamps
docker logs caddy -t

# View logs from last 10 minutes
docker logs caddy --since 10m

# View logs between timestamps
docker logs caddy --since 2024-01-08T06:00:00 --until 2024-01-08T07:00:00

# View all service logs
docker compose logs

# View specific service logs
docker compose logs caddy
docker compose logs authelia
docker compose logs crowdsec
```

#### View Logs via Grafana/Loki

1. **Access Grafana**: https://grafana.rodneyops.com
2. **Navigate to Explore** (compass icon)
3. **Select Loki** as data source
4. **Query logs**:
   ```
   # All Caddy logs
   {container="caddy"}

   # Caddy error logs
   {container="caddy"} |= "error"

   # Caddy access logs (JSON format)
   {container="caddy"} | json
   
   # All service logs
   {job="containers"}
   
   # Filter by log level
   {container="caddy"} | json | level="error"
   ```

#### View Logs via Promtail (if running locally)

```bash
# Check Promtail targets
curl http://localhost:9080/targets

# View Promtail metrics
curl http://localhost:9080/metrics
```

### Log Locations

**Docker Log Files** (on host):
```bash
# Docker container logs location
/var/lib/docker/containers/<container-id>/<container-id>-json.log

# Find Caddy container log file
docker inspect caddy | grep LogPath

# View log file directly (if needed)
sudo tail -f /var/lib/docker/containers/$(docker inspect -f '{{.Id}}' caddy)/$(docker inspect -f '{{.Id}}' caddy)-json.log
```

**System Logs** (for CrowdSec/Fail2ban):
- `/var/log/auth.log` - Authentication attempts
- `/var/log/syslog` - System logs
- Mounted at: `./config/pangolin/crowdsec_logs/` (for CrowdSec)

### Log Rotation Best Practices

Docker automatically handles log rotation based on the configuration:

1. **Per-Service Configuration** (recommended):
   ```yaml
   logging:
     driver: "json-file"
     options:
       max-size: "10m"      # Rotate at 10MB
       max-file: "3"        # Keep 3 files (30MB total)
       compress: "true"     # Compress old logs
   ```

2. **Docker Daemon Configuration** (global fallback):
   Edit `/etc/docker/daemon.json`:
   ```json
   {
     "log-driver": "json-file",
     "log-opts": {
       "max-size": "10m",
       "max-file": "3",
       "compress": "true"
     }
   }
   ```
   Then restart Docker: `sudo systemctl restart docker`

### Log Monitoring

- **Promtail** automatically collects all container logs via Docker socket
- **Loki** stores logs for querying and analysis
- **Grafana** provides visualization and alerting
- **CrowdSec** monitors logs for security threats

### Troubleshooting Log Issues

```bash
# Check if logs are being written
docker logs traefik --tail 10

# Check Docker log driver
docker inspect caddy | grep -A 10 LogConfig

# Check log file size
docker inspect caddy | grep LogPath
sudo ls -lh $(docker inspect -f '{{.LogPath}}' caddy)

# Check Promtail is collecting logs
docker logs promtail --tail 50 | grep caddy

# Check Loki is receiving logs
curl http://localhost:3100/ready
```

## 🐍 Python CLI Tools

The homelab includes a modular Python-based CLI tool (`homelab_tools`) for managing various aspects of the infrastructure.

### Features

- ✅ **Storage Management** - Mount/unmount Storage Boxes, setup SSH keys, verify connectivity
- ✅ **Backup & Restore** - Borg-based backups to remote locations with deduplication
- ✅ **Health Checks** - Comprehensive service health monitoring (local and remote via SSH)
- ✅ **Performance Monitoring** - System and Docker metrics collection with Slack reporting
- ✅ **Git Hooks** - Automated security and quality checks via pre-commit/pre-push hooks

### Quick Start

```bash
# Install homelab_tools (automatically installed via Ansible)
python3 -m homelab_tools --help

# Check service health
python3 -m homelab_tools health-check --local

# Mount Storage Boxes
python3 -m homelab_tools storage mount --box all

# Create backup
python3 -m homelab_tools backup create --type full --repository primary

# Performance monitoring
python3 -m homelab_tools performance report --format slack
```

### Integration

The Python tools are automatically:
- ✅ Installed on the server via Ansible during deployment to `/opt/tools/` (separate from `/opt/homelab/`)
- ✅ Integrated with the Makefile for easy access
- ✅ Available in the performance monitoring Docker stack
- ✅ Configured to send logs to Loki for centralized logging

**Installation Location:**
- Tools are installed in `/opt/tools/` to keep `/opt/homelab/` clean for backups
- Only configuration files in `/opt/homelab/` are backed up (not Python tools code)

**See [Homelab Tools Documentation](docs/HOMELAB_TOOLS.md) for complete usage guide and all available commands.**

## 🐛 Troubleshooting

### Service Won't Start

```bash
# Check logs
docker logs traefik --tail 100
docker logs crowdsec --tail 100
docker logs authelia --tail 100

# Or use make commands (if available)
make logs-caddy
make logs-crowdsec
make logs-authelia

# Verify configuration
make validate

# Check health
make health
```

### SSL Certificate Issues

```bash
# Check acme.json permissions
chmod 600 config/traefik/acme.json

# Check Cloudflare API token
cat config/caddy/cf-token

# View Caddy logs
make logs-caddy
```

### CrowdSec Not Blocking

```bash
# Check CrowdSec status
docker exec crowdsec cscli metrics

# Check bouncer connection
docker exec crowdsec cscli bouncers list

# Verify log acquisition
docker exec crowdsec cscli metrics
```

### Storage Box Not Mounted

```bash
# Check mount
mountpoint /mnt/storagebox

# Remount
sudo mount /mnt/storagebox

# Check credentials
cat /root/.davfs2_secrets

# Manual mount (WebDAV)
sudo mount.davfs https://u526046.your-storagebox.de /mnt/storagebox
```

## 🎬 Jellyfin Performance Optimization

Jellyfin has been optimized for performance on virtualized servers without hardware GPU acceleration.

### Performance Features

- ✅ **RAM-based Transcoding Cache** - 2GB tmpfs mount for transcoding segments (10-100x faster I/O)
- ✅ **Optimized Software Transcoding** - Faster encoder presets, throttling, segment deletion
- ✅ **Hardware Acceleration Support** - `/dev/dri` device mount for potential VA-API/QSV acceleration
- ✅ **Resource Management** - CPU throttling prevents overload during transcoding

### Configuration

**Automatic Optimization:**

```bash
# Run optimization script (applies all settings)
./scripts/optimize-jellyfin-transcoding.sh
```

**Manual Configuration:**

1. Access Jellyfin: `https://jellyfin.kooka-lake.ts.net`
2. Navigate to: Dashboard → Playback → Transcoding
3. Apply settings:
   - **Hardware acceleration**: `None` (or `VA-API` if available)
   - **Transcoding temp path**: `/config/data/transcodes` (tmpfs)
   - **Encoder preset**: `Very Fast`
   - **Enable throttling**: `On`
   - **Throttle delay**: `60 seconds`
   - **Enable segment deletion**: `On`

### Performance Tips

- **Direct Play**: Use clients that support your media formats to avoid transcoding
- **Pre-transcode**: Convert media to MP4/H.264 for better compatibility
- **Limit Concurrent Transcodes**: Set to 2-3 for CPX21 servers (3 vCPU)
- **Monitor Performance**: Check Dashboard → Dashboard → Active Devices for transcoding status

**See [Jellyfin Guide](docs/JELLYFIN.md) for complete documentation on performance optimization and hardware acceleration.**

## 📚 Documentation

### Core Documentation

- [Security Guide](docs/SECURITY.md) - Complete security documentation and checklist
- [Homelab Tools](docs/HOMELAB_TOOLS.md) - Python CLI tools for storage, backups, health checks, and performance monitoring
- [Storage Box Guide](docs/STORAGE_BOX.md) - Complete Hetzner Storage Box setup, migration, and troubleshooting
- [Media Services](docs/MEDIA_SERVICES.md) - Navidrome and Audiobookshelf setup

### Service-Specific Guides

- [Jellyfin Guide](docs/JELLYFIN.md) - Performance optimization, hardware acceleration, and transcoding configuration
- [Trakt Integration](docs/TRAKT.md) - Trakt setup with Jellyfin for watch history, ratings, and collections
- [LazyLibrarian Guide](docs/LAZYLIBRARIAN.md) - API configuration, HTTPS access, and Prowlarr integration
- [qBittorrent Guide](docs/QBITTORRENT.md) - Arr stack integration, security verification, and download configuration

### Additional Documentation

- [Arr Stack Media Integration](docs/ARR_STACK_MEDIA_INTEGRATION.md) - Integration between Arr services and media servers
- [Immich Backup Setup](docs/IMMICH_BACKUP_SETUP.md) - Immich backup configuration and scheduling
- [Tailscale Troubleshooting](docs/TAILSCALE_TROUBLESHOOTING.md) - Tailscale setup and common issues

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- [Caddy](https://caddyserver.com/) - Modern reverse proxy with automatic HTTPS
- [CrowdSec](https://crowdsec.net/) - Collaborative security
- [Authelia](https://www.authelia.com/) - SSO & 2FA
- [Prometheus](https://prometheus.io/) - Monitoring system
- [Grafana](https://grafana.com/) - Observability platform

## 📞 Support

For issues, questions, or suggestions:

- Open an [Issue](https://github.com/your-username/homelab/issues)
- Email: rodney@kodeflash.dev

---

**Built with ❤️ for maximum security and reliability**
