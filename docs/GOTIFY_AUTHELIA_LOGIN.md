# Gotify + Authelia Login Issue

## Problem

After successfully logging into Authelia, Gotify shows "Login failed" when trying to log in.

## Root Cause

Gotify has its own authentication system and **does not support proxy authentication** from Authelia. This means:

1. **Authelia authenticates you first** (via forward_auth)
2. **Gotify still requires its own login** with Gotify credentials
3. You need to use **Gotify credentials**, not Authelia credentials

## Solution

### Use Gotify Credentials

After passing Authelia authentication, you must log in to Gotify using:

- **Username**: Value from `GOTIFY_ADMIN_USER` in `.env` (default: `admin`)
- **Password**: Value from `GOTIFY_ADMIN_PASSWORD` in `.env`

### Check Your Credentials

```bash
# SSH into server
ssh rodkode@your-server

# Check Gotify credentials from .env
grep GOTIFY_ADMIN /opt/homelab/.env
```

### Verify Gotify is Running

```bash
# Check Gotify container status
docker ps | grep gotify

# Check Gotify logs
docker logs gotify --tail 50

# Check if Gotify is accessible
curl -I http://localhost:80/health
```

### Reset Gotify Admin Password (if needed)

If you've forgotten the Gotify password:

1. **Stop Gotify**:
   ```bash
   docker compose -f docker-compose.monitoring.yml stop gotify
   ```

2. **Delete Gotify database** (this will reset all users and apps):
   ```bash
   rm -rf /opt/homelab/config/gotify/gotify.db
   ```

3. **Update .env** with new password:
   ```bash
   # Edit .env and set new GOTIFY_ADMIN_PASSWORD
   nano /opt/homelab/.env
   ```

4. **Start Gotify**:
   ```bash
   docker compose -f docker-compose.monitoring.yml up -d gotify
   ```

5. **Log in** with the new credentials from `.env`

## Alternative: Use API Tokens

Instead of using the web UI, you can use Gotify's API tokens:

1. Access Gotify directly (bypass Authelia temporarily) or use API
2. Create an application token
3. Use the token for sending messages via API

## Configuration Notes

- **Authelia**: Protects access to Gotify (requires 1FA)
- **Gotify**: Has its own authentication system (separate from Authelia)
- **Double Login**: This is expected behavior - Authelia first, then Gotify

## Troubleshooting

### Check Authelia Logs

```bash
docker logs authelia --tail 50 | grep rodify
```

### Check Caddy Logs

```bash
docker logs caddy --tail 50 | grep rodify
```

### Check Gotify Logs

```bash
docker logs gotify --tail 50
```

### Test Direct Access (Bypass Authelia)

Temporarily comment out `forward_auth` in Caddyfile to test if Gotify login works directly:

```caddyfile
rodify.rodneyops.com {
    # forward_auth authelia:9091 {
    #     uri /api/authz/forward-auth
    #     copy_headers Remote-User Remote-Groups Remote-Name Remote-Email
    # }

    reverse_proxy gotify:80
}
```

Then reload Caddy and test Gotify login directly.

## Expected Behavior

1. User accesses `https://rodify.rodneyops.com`
2. Authelia forward_auth checks authentication
3. If not authenticated, redirects to Authelia login
4. After Authelia login, user is redirected back to Gotify
5. **Gotify shows its own login page** (this is normal)
6. User enters Gotify credentials (`GOTIFY_ADMIN_USER` / `GOTIFY_ADMIN_PASSWORD`)
7. User is logged into Gotify

This double authentication is expected because Gotify doesn't support proxy authentication headers from Authelia.
