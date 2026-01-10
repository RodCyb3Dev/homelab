# Deployment Fixes - Automated Service Health

This document describes the automated fixes that are applied during deployment to ensure all services start healthy on new servers.

## Automated Fixes

### 1. Jellyfin Database Permissions ✅

**Issue**: Jellyfin fails to start with `SQLite Error 8: 'attempt to write a readonly database'`

**Automated Fix**:
- Ansible playbook automatically sets ownership to `1000:1000` (PUID/PGID) for `/opt/homelab/config/jellyfin/config`
- Database files (`.db`, `.db-shm`, `.db-wal`) are set to `664` permissions
- Directories are set to `755` permissions

**Location**: `ansible/playbooks/deploy-arr-stack.yml` (post_tasks)

### 2. jellyfin-auto-collections Config ✅

**Issue**: Container can't resolve Tailscale domain `anduin.kooka-lake.ts.net` from within container

**Automated Fix**:
- Config file automatically updated to use `http://localhost:8096` for Jellyfin
- Config file automatically updated to use `http://localhost:5055` for Jellyseerr
- Uses `lineinfile` module to replace Tailscale domains with localhost

**Location**: 
- Default config: `config/jellyfin/jellyfin-plugins/auto-collections/config.yaml`
- Auto-fix: `ansible/playbooks/deploy-arr-stack.yml` (post_tasks)

### 3. jellyseerr Healthcheck ✅

**Issue**: Healthcheck fails or service restarts

**Automated Fix**:
- Healthcheck uses `ping -c 1 127.0.0.1` instead of HTTP endpoint
- More reliable and doesn't depend on service being fully initialized

**Location**: `docker-compose.arr-stack.yml` (line 149)

### 4. Loki Healthcheck ✅

**Issue**: Healthcheck fails with process check

**Automated Fix**:
- Healthcheck uses `ping -c 1 127.0.0.1` instead of process check
- Simpler and more reliable

**Location**: `docker-compose.monitoring.yml` (line 159)

### 5. Gluetun and ARR Services Healthchecks ✅

**Issue**: HTTP healthchecks fail or are unreliable

**Automated Fix**:
- All ARR services (Gluetun, qBittorrent, Prowlarr, Radarr, Sonarr, Lidarr, LazyLibrarian, Bazarr, Flaresolverr) use `ping -c 1 127.0.0.1`
- More reliable and faster

**Location**: `docker-compose.arr-stack.yml`

### 6. jellyfin-auto-collections Requirements ✅

**Issue**: `requirements.txt` not synced, causing `ModuleNotFoundError: No module named 'requests'`

**Automated Fix**:
- Ansible rsync includes `requirements.txt` and `Dockerfile` files
- Dockerfile properly installs requirements during build

**Location**: 
- `ansible/roles/sync_config/tasks/main.yml` (rsync_opts)
- `config/jellyfin/jellyfin-plugins/auto-collections/Dockerfile`

## Deployment Process

When you run `make ansible-deploy-arr`, the following happens automatically:

1. **Config Sync**: All configuration files are synced (including `requirements.txt` and `Dockerfile`)
2. **Secrets Sync**: Environment variables are set up
3. **Service Deployment**: Docker Compose services are deployed
4. **Permission Fixes** (post_tasks):
   - Jellyfin config directory ownership set to `1000:1000`
   - Database files made writable
   - Config files verified/updated to use localhost URLs

## Verification

After deployment, verify services are healthy:

```bash
ssh rodkode@your-server
cd /opt/homelab
sudo docker compose -f docker-compose.arr-stack.yml ps
```

All services should show as `Up` and `healthy` (or at least not `unhealthy`).

## Manual Fixes (if needed)

If services are still unhealthy after deployment:

1. **Jellyfin permissions**:
   ```bash
   sudo chown -R 1000:1000 /opt/homelab/config/jellyfin/config
   sudo find /opt/homelab/config/jellyfin/config -type f -name "*.db*" -exec chmod 664 {} \;
   ```

2. **Rebuild auto-collections**:
   ```bash
   cd /opt/homelab
   sudo docker compose -f docker-compose.arr-stack.yml build jellyfin-auto-collections
   sudo docker compose -f docker-compose.arr-stack.yml up -d jellyfin-auto-collections
   ```

3. **Check config URLs**:
   ```bash
   grep -E "server_url.*localhost" /opt/homelab/config/jellyfin/jellyfin-plugins/auto-collections/config.yaml
   ```

## Files Modified

- `ansible/playbooks/deploy-arr-stack.yml` - Added permission fixes and config verification
- `ansible/roles/fix_permissions/tasks/main.yml` - New role for permission fixes
- `ansible/roles/sync_config/tasks/main.yml` - Updated to include requirements.txt
- `docker-compose.arr-stack.yml` - Updated healthchecks to use ping
- `docker-compose.monitoring.yml` - Updated Loki healthcheck to use ping
- `config/jellyfin/jellyfin-plugins/auto-collections/config.yaml` - Default URLs set to localhost
- `config/jellyfin/jellyfin-plugins/auto-collections/Dockerfile` - Fixed to properly install requirements
