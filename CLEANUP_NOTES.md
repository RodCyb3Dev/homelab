# Cleanup Notes - Caddy Migration

## Files Removed

### Ansible Templates
- ✅ `ansible/roles/sync_config/templates/pangolin-config.yml.j2` - No longer needed
- ✅ `ansible/roles/sync_config/templates/middlewares.yml.j2` - No longer needed (Caddy uses Caddyfile)

### Fail2ban Filters
- ✅ `config/fail2ban/filter.d/traefik-auth.conf` - Replaced with `caddy-auth.conf`
- ✅ `config/fail2ban/filter.d/traefik-botsearch.conf` - Replaced with `caddy-botsearch.conf`

## Files to Archive (Optional)

These files are no longer used but can be kept as backup:

### Traefik Configuration (Legacy)
- `config/traefik/` - Entire directory can be archived
  - `traefik.yml` - Static configuration
  - `dynamic/middlewares.yml` - Dynamic middlewares
  - `dynamic/routers.yml` - Dynamic routers
  - `basic-auth.htpasswd` - Basic auth credentials (if still needed)
  - `cloudflare/acme.json` - Old certificates
  - `letsencrypt/acme.json` - Old certificates

### Pangolin Configuration (Legacy)
- `config/pangolin/` - Entire directory can be archived
  - `config.yml` - Pangolin configuration
  - `config.yml.example` - Example configuration
  - `crowdsec/` - Old CrowdSec config (moved to `config/crowdsec/`)
  - `logs/` - Old logs
  - `key` - Gerbil key (if still needed)

## Files Updated

### Fail2ban
- ✅ `config/fail2ban/jail.local` - Updated to use Caddy logs
- ✅ Created `config/fail2ban/filter.d/caddy-auth.conf`
- ✅ Created `config/fail2ban/filter.d/caddy-botsearch.conf`

### Ansible
- ✅ `ansible/roles/sync_config/tasks/main.yml` - Removed Pangolin/Traefik templating
- ✅ `ansible/roles/sync_secrets/tasks/main.yml` - Updated for Caddy CF token
- ✅ `ansible/roles/health_check/tasks/main.yml` - Updated to check Caddy

## Recommended Cleanup Commands

```bash
# Archive old configs (optional - for rollback)
mkdir -p archive/traefik archive/pangolin
mv config/traefik/* archive/traefik/ 2>/dev/null || true
mv config/pangolin/* archive/pangolin/ 2>/dev/null || true

# Or remove completely (if confident)
# rm -rf config/traefik config/pangolin
```

## What to Keep

- ✅ `config/caddy/` - New Caddy configuration
- ✅ `config/crowdsec/` - Updated CrowdSec config
- ✅ `config/fail2ban/` - Updated Fail2ban config
- ✅ `Caddyfile` - Main Caddy configuration

## Network Cleanup

After deployment, old networks can be removed:
```bash
docker network rm pangolin-proxy 2>/dev/null || true
```

## Volume Cleanup (After Testing)

Old volumes can be removed after confirming Caddy works:
```bash
# List volumes
docker volume ls | grep traefik

# Remove if no longer needed (BE CAREFUL!)
# docker volume rm <volume-name>
```

