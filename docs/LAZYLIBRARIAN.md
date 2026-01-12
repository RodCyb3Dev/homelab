# LazyLibrarian Complete Guide

Complete guide for LazyLibrarian setup, API configuration, and HTTPS access.

---

## 📋 Overview

LazyLibrarian is your self-hosted audiobook and ebook manager, integrated with the Arr stack. This guide covers:
- API key configuration for Prowlarr integration
- HTTPS access via Tailscale serve
- Troubleshooting common issues

**Access URL:** `https://anduin.kooka-lake.ts.net:5299`

---

## 🔑 API Key Configuration

### Getting the API Key from LazyLibrarian

#### Step 1: Access LazyLibrarian Web Interface

1. **Access LazyLibrarian:**
   - URL: `https://anduin.kooka-lake.ts.net:5299`
   - Login with your credentials (username: `readarrod`)

#### Step 2: Enable API and Get API Key

1. **Navigate to Settings:**
   - Click on **Config** in the top navigation
   - Select the **Interface** tab

2. **Enable API:**
   - Scroll down to the **Startup** section
   - Check the **"Enable API"** checkbox
   - Click **"Save changes"** at the top right

3. **Get the API Key:**
   - The API key will be displayed in the **Interface** settings page
   - It's usually shown as a long alphanumeric string
   - **Copy this API key** - you'll need it for Prowlarr configuration

**Alternative Method (if API key is not visible in Interface tab):**
- The API key may also be found in the **Settings → Web Interface** section
- Or check the LazyLibrarian logs for the API key on startup

---

## 🔧 Configuring Prowlarr to Use LazyLibrarian API Key

### Step 1: Access Prowlarr

1. **Access Prowlarr:**
   - URL: `https://anduin.kooka-lake.ts.net:9696`
   - Login with your credentials

### Step 2: Add LazyLibrarian as an Application

1. **Navigate to Apps:**
   - Go to **Settings** → **Apps**

2. **Add Application:**
   - Click the **"+"** (plus) button to add a new application
   - Select **"LazyLibrarian"** from the application type dropdown

3. **Configure LazyLibrarian Connection:**
   - **Name:** `LazyLibrarian` (or your preferred name)
   - **Enable:** ✅ (checked)
   - **Sync Level:** `Add and Remove Only` (recommended) or `Full Sync`
   - **Prowlarr Server:**
     - **Host:** `gluetun` (internal Docker network name)
     - **Port:** `9696`
   - **LazyLibrarian Server:**
     - **Host:** `gluetun` (internal Docker network name)
     - **Port:** `5299`
     - **Use SSL:** ❌ (unchecked - internal Docker network)
   - **API Key:** Paste the API key you copied from LazyLibrarian
   - **Base URL:** Leave empty (unless LazyLibrarian uses a base path)

4. **Test Connection:**
   - Click the **"Test"** button
   - You should see a success message if the connection works

5. **Save Configuration:**
   - Click **"Save"** to finalize the configuration

### Verification

After configuration, Prowlarr will:
- Sync indexers with LazyLibrarian
- Allow LazyLibrarian to search for audiobooks through Prowlarr's indexers
- Automatically add/remove indexers based on your sync level

**Test the Integration:**
1. **In LazyLibrarian:**
   - Go to **Settings → Providers**
   - You should see Prowlarr listed as a provider
   - Try searching for an audiobook to verify the connection

2. **In Prowlarr:**
   - Go to **Settings → Apps**
   - Check that LazyLibrarian shows as "Healthy" or "Connected"

---

## 🔒 HTTPS Access via Tailscale Serve

### Issue

When accessing LazyLibrarian via `https://anduin.kooka-lake.ts.net:5299`, you may encounter the error:
```
Client sent an HTTP request to an HTTPS server.
```

### Root Cause

**Update (2024):** Tailscale serve now supports `X-Forwarded-Proto` headers (added in [GitHub PR #8224](https://github.com/tailscale/tailscale/pull/8224), merged June 2023). However, LazyLibrarian must be configured to use these headers through its web interface.

The issue occurs because:
1. LazyLibrarian needs to be configured to read `X-Forwarded-Proto` headers (via web UI settings)
2. LazyLibrarian automatically rewrites its `config.ini` file, removing manual edits
3. Without proper proxy configuration, LazyLibrarian generates HTTP redirects even when accessed via HTTPS

### Solution

**⚠️ Important:** LazyLibrarian automatically rewrites its `config.ini` file, so manual edits to add proxy settings may be lost. The proxy settings must be configured through the web UI.

#### Configure Proxy Settings via Web UI

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

### Workarounds

#### Option 1: Access via Direct IP (Recommended for Internal Use)

Access LazyLibrarian directly via the Gluetun container's IP:
- Internal Docker network: `http://172.25.0.2:5299` (from within the Docker network)
- Or access via SSH tunnel: `ssh -L 5299:172.25.0.2:5299 rodkode@your-server-ip`

#### Option 2: Use HTTP (Not Recommended for Security)

Access via HTTP directly (bypassing Tailscale serve):
- Note: This requires direct network access and is not secure over the internet

#### Option 3: Use a Different Reverse Proxy (If HTTPS is Required)

If you need HTTPS access, consider using Caddy or Nginx as a reverse proxy instead of Tailscale serve:
- Caddy automatically handles `X-Forwarded-Proto` headers
- Nginx can be configured to send proper proxy headers

### Configuration Note

**⚠️ Manual Config File Edits Are Not Persistent**

LazyLibrarian automatically rewrites its `config.ini` file, removing sections that aren't set through the web UI. Therefore, proxy settings must be configured through the web interface, not by editing the config file directly.

The `config/lazylibrarian/config.ini` file in the repository contains the base configuration, but proxy settings should be configured via the web UI after initial deployment.

### Tailscale X-Forwarded-Proto Support

**Good News:** Tailscale serve now supports `X-Forwarded-Proto` headers! This was added in [GitHub PR #8224](https://github.com/tailscale/tailscale/pull/8224) and merged in June 2023. Tailscale serve automatically sends:
- `X-Forwarded-Proto: https` when proxying HTTPS requests
- `X-Forwarded-Host` header with the original host

**Current Tailscale Version:** 1.92.5 (supports X-Forwarded-Proto)

To make this work with LazyLibrarian:
1. Configure LazyLibrarian's proxy settings via the web UI (see above)
2. Ensure the "Enable http proxy" setting is enabled
3. Restart LazyLibrarian after configuration

If issues persist after configuration, it may be due to LazyLibrarian's config file being rewritten. In that case, the SSH tunnel workaround remains the most reliable solution.

---

## 🐛 Troubleshooting

### API Key Not Working

**Verify API is enabled in LazyLibrarian:**
- Go to **Config → Interface → Startup**
- Ensure **"Enable API"** is checked
- Restart LazyLibrarian if you just enabled it

**Check API Key:**
- Make sure you copied the entire API key (no extra spaces)
- The API key is case-sensitive

### Connection Issues

**Host Configuration:**
- Use `gluetun` (not `localhost` or `127.0.0.1`) since both services are on the Gluetun network
- Port should be `5299` for LazyLibrarian

**Network Verification:**
- Both Prowlarr and LazyLibrarian should be on the same Docker network (`service:gluetun`)
- Check that both containers are running: `docker ps | grep -E 'prowlarr|lazylibrarian'`

### API Key Location in Config File

If you need to find the API key in the config file:
- Location: `/opt/homelab/config/lazylibrarian/config.ini`
- Section: `[API]` or `[WEBSERVER]`
- Key name: `api_key` or `apikey`

**Note:** The API key may be auto-generated on first API enable, so it might not exist in the config file until you enable the API through the web UI.

### Permission Errors

**Problem:** `PermissionError: [Errno 13] Permission denied: '/config/cache/mako/formlogin.html.py'`

**Solution:**
```bash
# Fix cache directory permissions
docker exec lazylibrarian chmod -R 777 /config/cache
```

### HTTPS Redirect Issues

**Problem:** Still getting "Client sent an HTTP request to an HTTPS server" error

**Solution:**
1. Verify "Enable http proxy" is checked in web UI
2. Verify `proxy_local = X-Forwarded-Proto` is in `config.ini`
3. Restart LazyLibrarian
4. If still not working, use SSH tunnel workaround (see above)

---

## 📚 References

- [LazyLibrarian Interface Configuration](https://lazylibrarian.gitlab.io/config_interface/)
- [Prowlarr Apps Documentation](https://wiki.servarr.com/prowlarr/settings#applications)
- [Tailscale Serve Documentation](https://tailscale.com/kb/1242/tailscale-serve)

---

## ✅ Quick Setup Checklist

- [ ] LazyLibrarian accessible at `https://anduin.kooka-lake.ts.net:5299`
- [ ] API enabled in LazyLibrarian settings
- [ ] API key copied from LazyLibrarian
- [ ] Prowlarr configured with LazyLibrarian API key
- [ ] Connection tested in Prowlarr
- [ ] HTTPS access working (or SSH tunnel configured)
- [ ] Cache directory permissions fixed (if needed)

---

**Your LazyLibrarian is now configured and integrated with Prowlarr!** 📚
