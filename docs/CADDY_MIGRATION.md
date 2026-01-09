# Caddy Migration Guide

## Overview

This document describes the migration from Traefik + Pangolin + Gerbil to Caddy reverse proxy.

## What Changed

### Removed Services
- **Pangolin**: Domain/certificate management API (no longer needed)
- **Gerbil**: WireGuard gateway (simplified network architecture)
- **Traefik**: Replaced with Caddy

### New Services
- **Caddy**: Modern reverse proxy with automatic HTTPS

### Updated Services
- **Fail2ban**: Changed from `network_mode: service:gerbil` to `network_mode: host`
- **CrowdSec**: Updated collections from `crowdsecurity/traefik` to `crowdsecurity/caddy`
- **All monitoring services**: Removed Traefik Docker labels (Caddy uses Caddyfile)

## Architecture Changes

### Before (Traefik + Pangolin + Gerbil)
```
Internet → Gerbil (WireGuard) → Traefik → Services
                ↓
            Pangolin (API)
```

### After (Caddy)
```
Internet → Caddy → Services
```

## Configuration Files

### Caddyfile
- Location: `/opt/homelab/Caddyfile`
- Format: Caddyfile syntax (simpler than Traefik YAML)
- Routing: All routes defined in single file
- Authentication: Uses `forward_auth` directive for Authelia

### Network
- Old: `pangolin-proxy`
- New: `caddy-proxy`

## Security Features

### Maintained
- ✅ Authelia authentication/authorization
- ✅ CrowdSec IDS/IPS (updated for Caddy)
- ✅ Fail2ban system protection
- ✅ Security headers (HSTS, CSP, etc.)
- ✅ Automatic HTTPS with Let's Encrypt

### Improved
- ✅ Simpler configuration (single Caddyfile)
- ✅ Better privacy defaults (no telemetry)
- ✅ Lower resource usage
- ✅ Easier to audit and maintain

## Migration Steps

1. **Backup current configuration**
   ```bash
   cp -r config/traefik config/traefik.backup
   ```

2. **Stop services**
   ```bash
   docker compose down
   docker compose -f docker-compose.monitoring.yml down
   ```

3. **Deploy new configuration**
   ```bash
   make ansible-deploy
   make ansible-deploy-monitoring
   ```

4. **Verify services**
   - Check Caddy logs: `docker logs caddy`
   - Check Authelia: `https://auth.rodneyops.com`
   - Test protected services: `https://grafana.rodneyops.com`

## Caddyfile Structure

```caddyfile
# Global options
{
    admin off
    email your-email@example.com
}

# Authelia (authentication)
auth.rodneyops.com {
    reverse_proxy authelia:9091
}

# Protected services
grafana.rodneyops.com {
    forward_auth authelia:9091 {
        uri /api/verify?auth=basic
    }
    reverse_proxy grafana:3000
}
```

## Troubleshooting

### Certificates not generating
- Ensure port 80 is accessible for HTTP-01 challenge
- Check Caddy logs: `docker logs caddy`
- Verify DNS records point to server

### Services not accessible
- Check Caddyfile syntax: `docker exec caddy caddy validate --config /etc/caddy/Caddyfile`
- Verify services are on `caddy-proxy` network
- Check Authelia is healthy: `docker logs authelia`

### Fail2ban not working
- Verify `network_mode: host` is set
- Check logs: `docker logs fail2ban`
- Ensure `/var/log` is mounted

## Benefits

1. **Simplicity**: Single Caddyfile vs multiple Traefik config files
2. **Security**: Privacy-first defaults, no telemetry
3. **Performance**: Lower memory footprint
4. **Maintainability**: Easier to understand and modify
5. **Resource Efficiency**: Better for 4GB server

## Rollback

If needed, rollback to Traefik:
1. Restore `config/traefik` from backup
2. Revert `docker-compose.yml` and `docker-compose.monitoring.yml`
3. Redeploy with Ansible

