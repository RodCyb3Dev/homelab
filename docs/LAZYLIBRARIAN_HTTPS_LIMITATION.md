# LazyLibrarian HTTPS Access Limitation with Tailscale Serve

## Issue

When accessing LazyLibrarian via `https://anduin.kooka-lake.ts.net:5299`, you may encounter the error:
```
Client sent an HTTP request to an HTTPS server.
```

## Root Cause

**Update (2024):** Tailscale serve now supports `X-Forwarded-Proto` headers (added in [GitHub PR #8224](https://github.com/tailscale/tailscale/pull/8224), merged June 2023). However, LazyLibrarian must be configured to use these headers through its web interface.

The issue occurs because:
1. LazyLibrarian needs to be configured to read `X-Forwarded-Proto` headers (via web UI settings)
2. LazyLibrarian automatically rewrites its `config.ini` file, removing manual edits
3. Without proper proxy configuration, LazyLibrarian generates HTTP redirects even when accessed via HTTPS

## Current Configuration

**⚠️ Important:** LazyLibrarian automatically rewrites its `config.ini` file, so manual edits to add proxy settings may be lost. The proxy settings must be configured through the web UI.

### Configure Proxy Settings via Web UI

**Important:** Tailscale serve now supports `X-Forwarded-Proto` headers (since Tailscale v1.40+), but LazyLibrarian must be configured to use them.

1. **Access LazyLibrarian via HTTP** (direct access to configure):
   - Use SSH tunnel: `ssh -L 5299:172.25.0.2:5299 rodkode@your-server-ip`
   - Then access: `http://localhost:5299`
   - Or access directly via: `http://172.25.0.2:5299` (from within Docker network)

2. **Navigate to Settings:**
   - Go to **Config** → **Interface** tab
   - Enable **"Enable http proxy"** checkbox
     - This enables CherryPy's `tools.proxy.on` which reads `X-Forwarded-Proto` header
   - **Note:** The "Proxy local" field is NOT available in the web UI
   - Click **Save changes**

3. **Add `proxy_local` to config.ini manually:**
   - The `proxy_local` setting must be added manually to the `[WEBSERVER]` section in `config.ini`
   - Add this line to `/opt/homelab/config/lazylibrarian/config.ini`:
     ```ini
     [WEBSERVER]
     http_proxy = True
     proxy_local = X-Forwarded-Proto
     ```
   - This tells LazyLibrarian to read the `X-Forwarded-Proto` header from Tailscale serve

4. **Restart LazyLibrarian:**
   ```bash
   docker restart lazylibrarian
   ```

5. **Test HTTPS Access:**
   - Try accessing: `https://anduin.kooka-lake.ts.net:5299`
   - If it still redirects, the configuration may need to be set through the web UI again

## Workarounds

### Option 1: Access via Direct IP (Recommended for Internal Use)

Access LazyLibrarian directly via the Gluetun container's IP:
- Internal Docker network: `http://172.25.0.2:5299` (from within the Docker network)
- Or access via SSH tunnel: `ssh -L 5299:172.25.0.2:5299 rodkode@your-server-ip`

### Option 2: Use HTTP (Not Recommended for Security)

Access via HTTP directly (bypassing Tailscale serve):
- Note: This requires direct network access and is not secure over the internet

### Option 3: Use a Different Reverse Proxy (If HTTPS is Required)

If you need HTTPS access, consider using Caddy or Nginx as a reverse proxy instead of Tailscale serve:
- Caddy automatically handles `X-Forwarded-Proto` headers
- Nginx can be configured to send proper proxy headers

## Configuration Note

**⚠️ Manual Config File Edits Are Not Persistent**

LazyLibrarian automatically rewrites its `config.ini` file, removing sections that aren't set through the web UI. Therefore, proxy settings must be configured through the web interface, not by editing the config file directly.

The `config/lazylibrarian/config.ini` file in the repository contains the base configuration, but proxy settings should be configured via the web UI after initial deployment.

## References

- [LazyLibrarian Interface Configuration Documentation](https://lazylibrarian.gitlab.io/config_interface/)
- [Tailscale Serve Documentation](https://tailscale.com/kb/1242/tailscale-serve)

## Status

- ✅ LazyLibrarian service is running and healthy
- ✅ Cache directory permissions are fixed (777 for Mako templates)
- ✅ Service is accessible via HTTP directly
- ✅ Tailscale serve supports `X-Forwarded-Proto` headers (v1.40+, current: v1.92.5)
- ✅ **HTTPS access via Tailscale serve is now working!**
  - "HTTP proxy" checkbox enabled via web UI (Config → Interface)
  - `proxy_local = X-Forwarded-Proto` added to `[WEBSERVER]` section in `config.ini`
  - LazyLibrarian now correctly reads the `X-Forwarded-Proto` header from Tailscale serve

## Recommended Solution

**Use SSH Tunnel for Secure Access:**

```bash
# Create SSH tunnel
ssh -L 5299:172.25.0.2:5299 rodkode@your-server-ip

# Then access LazyLibrarian via:
http://localhost:5299
```

This provides secure access through the SSH tunnel without the HTTPS redirect issues.

## Tailscale X-Forwarded-Proto Support

**Good News:** Tailscale serve now supports `X-Forwarded-Proto` headers! This was added in [GitHub PR #8224](https://github.com/tailscale/tailscale/pull/8224) and merged in June 2023. Tailscale serve automatically sends:
- `X-Forwarded-Proto: https` when proxying HTTPS requests
- `X-Forwarded-Host` header with the original host

**Current Tailscale Version:** 1.92.5 (supports X-Forwarded-Proto)

To make this work with LazyLibrarian:
1. Configure LazyLibrarian's proxy settings via the web UI (see above)
2. Ensure the "Enable http proxy" setting is enabled
3. Restart LazyLibrarian after configuration

If issues persist after configuration, it may be due to LazyLibrarian's config file being rewritten. In that case, the SSH tunnel workaround remains the most reliable solution.
