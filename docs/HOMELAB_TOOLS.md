# Homelab Tools - Python CLI Documentation

## Overview

Homelab Tools is a modular Python CLI application for managing homelab infrastructure. It replaces multiple bash scripts with a unified, scalable, and maintainable Python-based solution.

## Installation

### Local Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Install package in development mode
pip install -e .
```

### Server Installation (via Ansible)

The package is automatically installed during Ansible deployment to `/opt/tools/` (separate from `/opt/homelab/`).

**Installation Location:**
- **Package Directory:** `/opt/tools/homelab_tools/`
- **Requirements:** `/opt/tools/requirements.txt`
- **Setup Script:** `/opt/tools/setup.py`

**Why `/opt/tools` instead of `/opt/homelab`?**
- Keeps `/opt/homelab` clean for backups (only config, compose files, `.env`)
- Python tools code is already version controlled in git
- Tools can be reinstalled easily if needed
- Avoids backing up `.venv`, build artifacts, and Python cache

### Project Structure

```
homelab_tools/
├── __init__.py
├── __main__.py
├── cli.py                  # Main CLI entry point
├── config.py              # Configuration management
├── logging.py              # Loki logging integration
├── modules/
│   ├── __init__.py
│   ├── backup.py          # Borg backup operations
│   ├── restore.py         # Backup restore operations
│   ├── health_check.py    # Service health monitoring
│   ├── storage.py         # Storage Box management
│   ├── performance.py     # Performance monitoring
│   └── git_hooks.py       # Git hooks management
└── utils/
    ├── __init__.py
    ├── ssh.py             # SSH client utilities
    ├── docker.py          # Docker API utilities
    └── borg.py            # BorgBackup wrapper
```

## Usage

### CLI Commands

```bash
# Health checks
python3 -m homelab_tools health-check --local
python3 -m homelab_tools health-check --remote <host>

# Backup operations
python3 -m homelab_tools backup create --type full
python3 -m homelab_tools backup list
python3 -m homelab_tools backup prune

# Restore operations
python3 -m homelab_tools restore list
python3 -m homelab_tools restore extract <archive-name>

# Storage Box management
python3 -m homelab_tools storage mount --box main
python3 -m homelab_tools storage status
python3 -m homelab_tools storage setup --box main --method webdav

# Performance monitoring
python3 -m homelab_tools performance check
python3 -m homelab_tools performance report --format slack
python3 -m homelab_tools performance slack

# Git hooks
python3 -m homelab_tools git-hooks install
python3 -m homelab_tools git-hooks test
```

### Makefile Integration

The Makefile has been updated to use the Python CLI:

```bash
make health          # Health check
make backup          # Create backup
make restore         # List available backups
make setup-storage-box  # Mount Storage Boxes
make setup-git-hooks    # Install Git hooks
```

## Configuration

Configuration is loaded from:
1. Environment variables
2. `~/.homelab/config.yaml` (if exists)

### Configuration File Example

```yaml
deploy_path: /opt/homelab
ssh_user: rodkode
ssh_host: 95.216.176.147
ssh_key: ~/.ssh/ansible_key
loki_url: http://loki:3100
prometheus_url: http://prometheus:9090

storage_boxes:
  main:
    host: u529830.your-storagebox.de
    user: u529830
    mount_point: /mnt/storagebox
  immich:
    host: u527847.your-storagebox.de
    user: u527847
    mount_point: /mnt/storagebox-immich

backup:
  primary:
    type: storagebox
    host: <backup-storagebox-host>
    user: <backup-user>
    repository: ssh://user@host:23/./backups/homelab
  secondary:
    type: server
    host: <backup-server-host>
    user: <backup-user>
    repository: ssh://user@host:22/~/backups/homelab

slack:
  webhook_url: https://hooks.slack.com/services/...
```

## Modules

### Backup Module

- **Borg-based backups** to separate Storage Box and backup server
- **Automatic pruning** (keep daily/weekly/monthly)
- **Repository verification**
- **Encrypted backups** with repokey encryption

### Restore Module

- **List available archives**
- **Extract archives** to temporary or specified location
- **Verify archive integrity**

### Health Check Module

- **Docker container status**
- **Service endpoint checks**
- **Resource usage** (CPU, memory, disk)
- **SSL certificate expiry**
- **Storage Box mount status**
- **Remote SSH health checks**

### Storage Module

- **Mount/unmount Storage Boxes** (WebDAV or SSH)
- **Generate systemd units** for automatic mounting
- **Status monitoring**

### Performance Module

- **System metrics** (CPU, memory, disk)
- **Container statistics**
- **Jellyfin-specific metrics**
- **Generate reports** (JSON, HTML, Slack)
- **Daily automated reports** via cron

### Git Hooks Module

- **Pre-commit checks**: Secret scanning, YAML validation, shell script checks
- **Pre-push checks**: Full repository scan, TODO checks
- **Automatic installation** of hooks

## Logging Integration

All tools log to Loki via HTTP API:
- **Structured JSON logging** with labels
- **Automatic retry** on failure
- **Fallback to file logging** if Loki unavailable

Logs are automatically collected by Promtail and visible in Grafana.

## Performance Monitoring Stack

The `docker-compose.performance.yml` file provides:
- **Continuous monitoring** service
- **Daily cron reports** to Slack
- **Integration with Prometheus** for metrics storage

## Migration from Bash Scripts

The following scripts have been replaced by the Python CLI:

| Old Script | New Command |
|------------|-------------|
| `scripts/backup.sh` | `python3 -m homelab_tools backup create` |
| `scripts/restore.sh` | `python3 -m homelab_tools restore extract` |
| `scripts/health-check.sh` | `python3 -m homelab_tools health-check` |
| `scripts/mount-storage-boxes.sh` | `python3 -m homelab_tools storage mount` |
| `scripts/mount-storagebox.sh` | `python3 -m homelab_tools storage mount` |
| `scripts/setup-new-storagebox-ssh.sh` | `python3 -m homelab_tools storage setup` |
| `scripts/setup-storage-box-server.sh` | `python3 -m homelab_tools storage setup` |
| `scripts/setup-storagebox-systemd.sh` | `python3 -m homelab_tools storage setup` |
| `scripts/setup-git-hooks.sh` | `python3 -m homelab_tools git-hooks install` |
| `scripts/jellyfin-performance-check.sh` | `python3 -m homelab_tools performance check` |

**Removed Scripts:**
- `scripts/optimize-jellyfin-transcoding.sh` - Can be done via Jellyfin UI
- `scripts/cleanup-git-secrets-simple.sh` - One-time cleanup (no longer needed)
- `scripts/cleanup-old-dirs.sh` - One-time cleanup (no longer needed)
- `systemd/storagebox-mount.service` - Replaced by automount units

**Kept Scripts:**
- `scripts/vault_pwd.sh` - Required by Ansible for vault password management

## Dependencies

See `requirements.txt` for full list. Key dependencies:
- `click` - CLI framework
- `pyyaml` - Configuration
- `requests` - HTTP client
- `paramiko` - SSH client
- `docker` - Docker SDK
- `psutil` - System monitoring

## Development

### Local Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Install package in development mode
pip install -e .

# Test CLI
python3 -m homelab_tools --help
python3 -m homelab_tools health-check --local
```

### Code Quality

```bash
# Lint code
pylint homelab_tools/

# Run tests (when implemented)
pytest
```

## Implementation History

This Python CLI tool was created to replace multiple bash scripts with a unified, scalable solution:

- **Consolidated 5 storage scripts** into one `storage` module
- **Replaced backup/restore scripts** with Borg-based `backup` and `restore` modules
- **Enhanced health checks** with Docker integration and remote SSH support
- **Added performance monitoring** with Jellyfin-specific metrics
- **Integrated logging** to Loki for centralized log management
- **Created Git hooks** for automated security and quality checks

All modules use structured logging to Loki and integrate with the existing monitoring stack (Prometheus/Grafana).

## Troubleshooting

### Import Errors

If you get import errors, ensure the package is installed:
```bash
pip install -e .
```

### Loki Connection Errors

If Loki is unavailable, logs will fall back to stderr. Check:
1. Loki service is running
2. `LOKI_URL` environment variable is set correctly
3. Network connectivity to Loki

### Docker Connection Errors

If Docker operations fail:
1. Ensure Docker daemon is running
2. User has permission to access Docker socket
3. Docker SDK is installed: `pip install docker`
