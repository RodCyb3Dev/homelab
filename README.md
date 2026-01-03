# Secure Homelab Infrastructure

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Docker](https://img.shields.io/badge/docker-required-blue)
![Security](https://img.shields.io/badge/security-hardened-brightgreen)

A production-ready, maximum-security homelab infrastructure with defense-in-depth architecture, zero-trust access controls, and full observability.

## 🎯 Features

### Security

- ✅ **6-Layer Defense-in-Depth** - Cloudflare WAF, Traefik, CrowdSec, Authelia, Fail2ban, Tailscale
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

## 📋 Table of Contents

- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Services](#services)
- [Configuration](#configuration)
- [Deployment](#deployment)
- [Monitoring](#monitoring)
- [Security](#security)
- [Maintenance](#maintenance)
- [Troubleshooting](#troubleshooting)

## 🏗 Architecture

```
Internet
    ↓
Cloudflare CDN/WAF (Layer 1)
    ↓
Traefik Reverse Proxy (Layer 2)
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
│ • Traefik Dashboard        │ • Sonarr, Radarr (TV/Movies)│
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

### Public Services (via Traefik + Authelia)

| Service           | URL                     | Purpose                  | Auth               |
| ----------------- | ----------------------- | ------------------------ | ------------------ |
| Traefik Dashboard | `traefik.rodneyops.com` | Reverse proxy monitoring | 2FA + IP whitelist |
| Grafana           | `grafana.rodneyops.com` | Metrics & dashboards     | 2FA                |
| Gotify            | `rodify.rodneyops.com`  | Push notifications       | Password           |
| Uptime Kuma       | `status.rodneyops.com`  | Service status page      | 2FA                |
| Authelia          | `auth.rodneyops.com`    | SSO authentication       | Password + 2FA     |

### Private Services (Tailscale-only)

| Service     | Internal Port | Purpose              |
| ----------- | ------------- | -------------------- |
| Jellyfin    | 8096          | Media streaming      |
| Sonarr      | 8989          | TV show management   |
| Radarr      | 7878          | Movie management     |
| Prowlarr    | 9696          | Indexer management   |
| qBittorrent | 8085          | Torrent client       |
| Lidarr      | 8686          | Music management     |
| Readarr     | 8787          | Book management      |
| Bazarr      | 6767          | Subtitle management  |
| Homarr      | 7575          | Service dashboard    |
| Portainer   | 9000          | Container management |

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
CROWDSEC_BOUNCER_API_KEY=your_api_key

# Tailscale
TAILSCALE_AUTH_KEY=tskey-auth-xxxxx
```

See [`.env.example`](.env.example) for complete list.

### Traefik Configuration

- Static config: [`config/traefik/traefik.yml`](config/traefik/traefik.yml)
- Dynamic config: [`config/traefik/dynamic/`](config/traefik/dynamic/)
- Middlewares: [`config/traefik/dynamic/middlewares.yml`](config/traefik/dynamic/middlewares.yml)

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
docker exec crowdsec cscli bouncers add traefik-bouncer
```

### Hetzner Storage Box

The Storage Box is mounted at `/mnt/storagebox` via WebDAV (HTTPS) and provides network storage for media files and backups.

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

See [Storage Box Setup Guide](docs/STORAGE_BOX_SETUP.md) for detailed configuration.

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
   - Save to: `config/traefik/cf_api_token.txt` (chmod 600)

### Deployment Methods

#### Option 1: Kamal (Zero-Downtime) - Recommended

```bash
# Setup Kamal
make kamal-setup

# Deploy
make kamal-deploy

# Rollback if needed
make kamal-rollback
```

**Benefits:**

- Zero-downtime rolling updates
- Only Docker images deployed (no file transfers)
- Automatic health checks
- Instant rollback support

#### Option 2: Docker Compose (Manual)

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

#### Option 3: GitHub Actions (CI/CD)

1. **Setup GitHub Secrets:**
   - `SSH_HOST` - Hetzner server IP
   - `SSH_USER` - SSH username
   - `SSH_PRIVATE_KEY` - SSH private key
   - `KAMAL_REGISTRY_USERNAME` - GitHub username
   - `KAMAL_REGISTRY_PASSWORD` - GitHub token (write:packages)

2. **Deploy:**
   ```bash
   git push origin main
   ```

The CI/CD pipeline automatically:

- Runs security scans (gitleaks, yamllint, shellcheck)
- Validates configuration
- Builds and pushes Docker image
- Deploys with zero-downtime (Kamal)
- Runs health checks
- Sends notifications

## 📊 Monitoring

### Access Dashboards

- **Grafana**: https://grafana.rodneyops.com
- **Prometheus**: http://localhost:9090 (internal)
- **Traefik**: https://traefik.rodneyops.com

### Grafana Dashboards

Pre-configured dashboards:

1. **Infrastructure Overview** - All services, resource usage
2. **Security Dashboard** - CrowdSec stats, Fail2ban, blocked IPs
3. **Traefik Dashboard** - Traffic patterns, response times
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
2. **Traefik** - TLS 1.3, security headers, rate limiting, request validation
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

## 🐛 Troubleshooting

### Service Won't Start

```bash
# Check logs
make logs-traefik
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
cat config/traefik/cf_api_token.txt

# View Traefik logs
make logs-traefik
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

## 📚 Documentation

- [Security Guide](docs/SECURITY.md) - Complete security documentation and checklist
- [Media Services](docs/MEDIA_SERVICES.md) - Navidrome and Audiobookshelf setup
- [Storage Box Setup](docs/STORAGE_BOX_SETUP.md) - Hetzner Storage Box configuration

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- [Traefik](https://traefik.io/) - Modern reverse proxy
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
