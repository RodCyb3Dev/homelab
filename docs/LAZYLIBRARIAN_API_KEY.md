# LazyLibrarian API Key Configuration

This guide explains how to get the API key from LazyLibrarian and configure it in Prowlarr.

---

## 🔑 Getting the API Key from LazyLibrarian

### Step 1: Access LazyLibrarian Web Interface

1. **Access LazyLibrarian:**
   - URL: `https://anduin.kooka-lake.ts.net:5299`
   - Login with your credentials (username: `readarrod`)

### Step 2: Enable API and Get API Key

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

---

## ✅ Verification

After configuration, Prowlarr will:
- Sync indexers with LazyLibrarian
- Allow LazyLibrarian to search for audiobooks through Prowlarr's indexers
- Automatically add/remove indexers based on your sync level

### Test the Integration

1. **In LazyLibrarian:**
   - Go to **Settings → Providers**
   - You should see Prowlarr listed as a provider
   - Try searching for an audiobook to verify the connection

2. **In Prowlarr:**
   - Go to **Settings → Apps**
   - Check that LazyLibrarian shows as "Healthy" or "Connected"

---

## 🔍 Troubleshooting

### API Key Not Working

- **Verify API is enabled in LazyLibrarian:**
  - Go to **Config → Interface → Startup**
  - Ensure **"Enable API"** is checked
  - Restart LazyLibrarian if you just enabled it

- **Check API Key:**
  - Make sure you copied the entire API key (no extra spaces)
  - The API key is case-sensitive

### Connection Issues

- **Host Configuration:**
  - Use `gluetun` (not `localhost` or `127.0.0.1`) since both services are on the Gluetun network
  - Port should be `5299` for LazyLibrarian

- **Network Verification:**
  - Both Prowlarr and LazyLibrarian should be on the same Docker network (`service:gluetun`)
  - Check that both containers are running: `docker ps | grep -E 'prowlarr|lazylibrarian'`

### API Key Location in Config File

If you need to find the API key in the config file:
- Location: `/opt/homelab/config/lazylibrarian/config.ini`
- Section: `[API]` or `[WEBSERVER]`
- Key name: `api_key` or `apikey`

**Note:** The API key may be auto-generated on first API enable, so it might not exist in the config file until you enable the API through the web UI.

---

## 📚 References

- [LazyLibrarian Interface Configuration](https://lazylibrarian.gitlab.io/config_interface/)
- [Prowlarr Apps Documentation](https://wiki.servarr.com/prowlarr/settings#applications)
