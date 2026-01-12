# Architecture Overview

## 🏗️ System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Internet / Cloudflare                    │
└───────────────────────┬─────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────┐
│                    Caddy (Reverse Proxy)                    │
│              TLS 1.3, Automatic SSL Certs                   │
└───────────────────────┬─────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
┌───────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐
│  Authelia    │ │  CrowdSec   │ │   Services  │
│  (2FA/SSO)   │ │  (IDS/IPS)  │ │  (Apps)     │
└──────────────┘ └─────────────┘ └─────────────┘
```

## 🔐 Security Layers

1. **Cloudflare WAF** - DDoS protection and WAF rules
2. **Caddy Reverse Proxy** - TLS termination, routing
3. **CrowdSec** - Intrusion Detection/Prevention System
4. **Authelia** - Authentication & Authorization (2FA)
5. **Fail2ban** - Additional intrusion prevention
6. **Tailscale** - Zero-trust VPN for private services

## 🌐 Network Architecture

### Network Segmentation

- **caddy-proxy**: Public-facing services
- **grafana-monitoring**: Monitoring stack (isolated)
- **gluetun**: VPN network for torrent services
- **Tailscale**: Private VPN network

## 📦 Service Architecture

### Media Stack
- All services communicate via Docker networks
- Storage mounted from Hetzner Storage Box
- qBittorrent uses Gluetun for VPN routing

### Monitoring Stack
- Prometheus scrapes metrics from all services
- Loki aggregates logs via Promtail
- Grafana visualizes metrics and logs

## 🔄 Data Flow

### Media Request Flow
1. User requests media via Jellyseerr
2. Jellyseerr creates request in Radarr/Sonarr
3. Radarr/Sonarr searches via Prowlarr
4. Prowlarr finds torrent via Jackett
5. qBittorrent downloads (via Gluetun VPN)
6. Radarr/Sonarr imports to Storage Box
7. Jellyfin scans and makes available

### Authentication Flow
1. User accesses service
2. Caddy redirects to Authelia
3. Authelia authenticates (2FA)
4. User redirected to service with session

## 💾 Storage Architecture

- **Local**: `/opt/homelab` - Configuration files
- **Storage Box**: `/mnt/storagebox` - Media files (mounted via WebDAV)
- **Backups**: BorgBackup to separate Storage Box/server

## 🔧 Automation Architecture

- **Ansible**: Infrastructure as Code
- **Python CLI Tools**: Operational automation
- **GitHub Actions**: CI/CD pipeline
- **Systemd**: Service auto-start

---

[← Back to Home](./Home)
