# qBittorrent Complete Guide

Complete guide for qBittorrent configuration, security, and integration with Arr services.

---

## 📋 Overview

qBittorrent is your download client for the Arr stack, configured to route all traffic through a VPN (Gluetun) for privacy and security. This guide covers:
- Configuration for Arr stack integration
- Security and privacy verification
- Download path setup
- Troubleshooting

**Access URL:** `https://anduin.kooka-lake.ts.net:8085`

---

## 🔧 Configuration for Arr-Stack

### Common Health Check Warnings

If you see these warnings in Lidarr/Radarr/Sonarr:

1. **"Download client qBittorrent places downloads in /media/downloads/music but this directory does not appear to exist inside the container"**
2. **"Download client qBittorrent places downloads in the root folder /media/downloads/. You should not download to a root folder."**

These indicate incorrect configuration. Follow this guide to fix them.

### Step 1: Configure Download Paths

Access qBittorrent: `https://anduin.kooka-lake.ts.net:8085`

1. Go to **Tools → Options → Downloads**
2. Configure:
   - **Default Save Path:** `/media/downloads`
     - ⚠️ **This is a staging area, NOT a root folder**
     - All completed downloads go here temporarily
     - Arr services will import from here and organize to their root folders
   - **Incomplete downloads:** `/incomplete`
     - This uses tmpfs (RAM) for faster I/O during downloads
     - Files are moved to `/media/downloads` when complete

3. Click **Save**

### Step 2: Disable Category-Based Subdirectories (Recommended)

1. Go to **Tools → Options → Downloads**
2. **Uncheck:** ✅ **Create subfolder for torrents with multiple files**
3. **Uncheck:** ✅ **Append .!qB extension to incomplete files** (optional, but recommended)
4. Click **Save**

**Why?** Categories can create subdirectories like `/media/downloads/music`, but Arr services expect all downloads in `/media/downloads` and will organize them themselves.

### Step 3: Alternative - Use Categories (If You Prefer)

If you want to use categories for organization:

1. Go to **Tools → Options → Downloads**
2. **Check:** ✅ **Create subfolder for torrents with multiple files**
3. Go to **Tools → Options → Categories**
4. Create categories:
   - **music** → Save path: `/media/downloads/music`
   - **movies** → Save path: `/media/downloads/movies`
   - **tv** → Save path: `/media/downloads/tv`
   - **books** → Save path: `/media/downloads/books`

**Then configure Remote Path Mappings in each Arr service** (see below).

---

## 📁 Arr Service Root Folders

Each Arr service must have its own root folder, separate from the download directory:

### Lidarr Configuration

1. Access Lidarr: `https://anduin.kooka-lake.ts.net:8686`
2. Go to **Settings → Media Management → Root Folders**
3. Edit root folder:
   - **Path:** `/media/music` ⚠️ **NOT `/media/downloads`**
   - This is where Lidarr organizes music after import

### Radarr Configuration

1. Access Radarr: `https://anduin.kooka-lake.ts.net:7878`
2. Go to **Settings → Media Management → Root Folders**
3. Edit root folder:
   - **Path:** `/media/movies` ⚠️ **NOT `/media/downloads`**
   - This is where Radarr organizes movies after import

### Sonarr Configuration

1. Access Sonarr: `https://anduin.kooka-lake.ts.net:8989`
2. Go to **Settings → Media Management → Root Folders**
3. Edit root folder:
   - **Path:** `/media/tv` ⚠️ **NOT `/media/downloads`**
   - This is where Sonarr organizes TV shows after import

### LazyLibrarian Configuration

1. Access LazyLibrarian: `https://anduin.kooka-lake.ts.net:5299`
2. Go to **Settings → Folders**
3. Set **Audiobook Folder:**
   - **Path:** `/media/audiobooks` ⚠️ **NOT `/media/downloads`**
   - This is where LazyLibrarian organizes audiobooks after import

---

## 🔗 Remote Path Mappings

Since all services share the same Docker volume (`hetzner-media`), Remote Path Mappings are usually not needed, but it's good practice to configure them for compatibility.

### Lidarr Remote Path Mapping

1. Go to **Settings → Media Management → Remote Path Mappings**
2. Click **Add Remote Path Mapping**
3. Configure:
   - **Host:** `gluetun` (or `qbittorrent` if using categories)
   - **Remote Path:** `/media/downloads` (or `/media/downloads/music` if using categories)
   - **Local Path:** `/media/downloads` (same path, since same volume)
4. Click **Save**

### Radarr Remote Path Mapping

1. Go to **Settings → Media Management → Remote Path Mappings**
2. Click **Add Remote Path Mapping**
3. Configure:
   - **Host:** `gluetun`
   - **Remote Path:** `/media/downloads` (or `/media/downloads/movies` if using categories)
   - **Local Path:** `/media/downloads`
4. Click **Save**

### Sonarr Remote Path Mapping

1. Go to **Settings → Media Management → Remote Path Mappings**
2. Click **Add Remote Path Mapping**
3. Configure:
   - **Host:** `gluetun`
   - **Remote Path:** `/media/downloads` (or `/media/downloads/tv` if using categories)
   - **Local Path:** `/media/downloads`
4. Click **Save**

---

## ✅ Correct Workflow

### Download Process

1. **Arr Service (Lidarr/Radarr/Sonarr) sends download to qBittorrent:**
   - qBittorrent receives torrent
   - Downloads to `/incomplete` (tmpfs in RAM)

2. **qBittorrent completes download:**
   - Moves completed files to `/media/downloads` (staging area)
   - If using categories: moves to `/media/downloads/{category}`

3. **Arr Service imports and organizes:**
   - Detects completed download in `/media/downloads`
   - Imports files
   - Organizes to root folder:
     - Lidarr: `/media/downloads` → `/media/music`
     - Radarr: `/media/downloads` → `/media/movies`
     - Sonarr: `/media/downloads` → `/media/tv`
   - Optionally removes original from `/media/downloads` (if "Remove Completed" is enabled)

4. **Media Server indexes:**
   - Jellyfin: Reads from `/media/movies`, `/media/tv`
   - Navidrome: Auto-scans `/music` (maps to `/media/music`)
   - Audiobookshelf: Scans `/audiobooks` (maps to `/media/audiobooks`)

---

## 🔒 Security & Privacy

### Security Status: ✅ SECURE - No Data Leaks Detected

Comprehensive security checks confirm that qBittorrent is properly configured to route all traffic through the VPN (Gluetun) with no IP leaks detected. The setup includes an active firewall/kill switch that blocks all traffic if the VPN connection fails.

### Security Checks Performed

#### ✅ 1. Network Configuration
- **qBittorrent Network Mode:** `network_mode: service:gluetun` ✓
- **Status:** qBittorrent shares Gluetun's network stack, ensuring all traffic routes through VPN

#### ✅ 2. IP Address Verification
- **Gluetun Public IP:** `212.92.104.246` (Netherlands, North Brabant, Breda)
- **qBittorrent Public IP:** `212.92.104.246` (Netherlands, North Brabant, Breda)
- **Status:** Both containers show identical VPN IP address - **NO IP LEAK**

**Test Results:**
- `api.ipify.org`: `212.92.104.246` ✓
- `ipv4.icanhazip.com`: `212.92.104.246` ✓
- `ifconfig.me`: `212.92.104.246` ✓
- `check.torproject.org`: `212.92.104.246` ✓

#### ✅ 3. VPN Interface Verification
- **Gluetun VPN Interface:** `tun0` with IP `10.2.0.2/32` ✓
- **qBittorrent VPN Interface:** `tun0` with IP `10.2.0.2/32` ✓
- **Status:** Both containers have access to the VPN tunnel interface

#### ✅ 4. Firewall / Kill Switch
- **Firewall Status:** `enabled successfully` ✓
- **iptables OUTPUT Policy:** `DROP` (default deny) ✓
- **Allowed Traffic:** Only traffic through `tun0` interface ✓
- **Status:** Kill switch is active - if VPN fails, all traffic is blocked

**iptables Rules:**
```
Chain OUTPUT (policy DROP)
- ACCEPT all traffic on loopback (lo)
- ACCEPT established/related connections
- ACCEPT traffic to Docker network (172.25.0.0/24)
- ACCEPT UDP to VPN server (62.169.136.199:51820)
- ACCEPT all traffic through tun0 (VPN interface)
```

#### ✅ 5. IPv6 Leak Test
- **qBittorrent IPv6:** Only loopback (`::1`) - no global IPv6 addresses ✓
- **Status:** **NO IPv6 LEAK** - IPv6 is disabled/not exposed

#### ✅ 6. DNS Leak Test
- **qBittorrent DNS:** `127.0.0.1` (local resolver) ✓
- **Status:** DNS queries route through VPN via Gluetun's local resolver

#### ✅ 7. Routing Verification
- **Default Route:** All traffic routes through VPN interface (`tun0`) ✓
- **Status:** No direct internet access - all traffic must go through VPN

### Configuration Details

#### Gluetun Configuration
```yaml
VPN_SERVICE_PROVIDER: protonvpn
VPN_TYPE: wireguard
SERVER_COUNTRIES: Netherlands
FIREWALL_VPN_INPUT_PORTS: 6881
VPN_INPUT_PORTS: 6881
```

#### qBittorrent Configuration
- **Network Mode:** `service:gluetun` (shares VPN network stack)
- **Download Location:** `/media/downloads` (Hetzner Storage Box)
- **Incomplete Downloads:** `/incomplete` (tmpfs - 10GB RAM)

### Recommendations

#### ✅ Already Implemented
1. ✓ qBittorrent uses `network_mode: service:gluetun`
2. ✓ Gluetun firewall/kill switch is enabled
3. ✓ All traffic routes through VPN tunnel (`tun0`)
4. ✓ IPv6 is disabled (no IPv6 leaks)
5. ✓ DNS routes through VPN

#### 🔧 Optional Enhancements

1. **Bind qBittorrent to VPN Interface (Recommended)**
   - In qBittorrent Web UI: **Tools → Options → Advanced**
   - Set **Network Interface** to `tun0` (or the VPN interface name)
   - This provides an additional layer of protection by explicitly binding to the VPN interface

2. **Regular Security Audits**
   - Periodically run IP leak tests
   - Monitor Gluetun logs for VPN disconnections
   - Verify firewall remains active after container restarts

3. **Monitor VPN Connection**
   - Set up alerts for VPN disconnections
   - Monitor Gluetun health status
   - Check public IP periodically to ensure it matches VPN IP

### Security Score: 9.5/10

**Strengths:**
- ✓ Network isolation via `network_mode: service:gluetun`
- ✓ Active firewall/kill switch
- ✓ No IP leaks detected
- ✓ No IPv6 leaks
- ✓ DNS routing through VPN
- ✓ All traffic routes through VPN tunnel

**Minor Improvement:**
- Consider explicitly binding qBittorrent to `tun0` interface in settings (adds defense-in-depth)

### Conclusion

Your qBittorrent setup is **SECURE and PRIVATE**. All traffic is properly routed through the ProtonVPN connection via Gluetun, with an active kill switch that prevents data leaks if the VPN connection fails. No IP leaks, DNS leaks, or IPv6 leaks were detected during comprehensive testing.

**Status:** ✅ **APPROVED FOR PRODUCTION USE**

---

## 🐛 Troubleshooting

### Warning: "Directory does not exist"

**Cause:** qBittorrent is configured to download to a subdirectory that doesn't exist (e.g., `/media/downloads/music`).

**Fix:**
1. In qBittorrent, set **Default Save Path** to `/media/downloads` (no subdirectories)
2. Or create the subdirectories manually:
   ```bash
   ssh rodkode@your-server-ip
   mkdir -p /mnt/storagebox/downloads/{music,movies,tv,books}
   ```

### Warning: "You should not download to a root folder"

**Cause:** An Arr service's root folder is set to `/media/downloads` (the download staging area).

**Fix:**
1. Change the Arr service's root folder to its proper location:
   - Lidarr: `/media/music`
   - Radarr: `/media/movies`
   - Sonarr: `/media/tv`
   - LazyLibrarian: `/media/audiobooks`
2. Root folders should be separate from the download directory

### Downloads Not Importing

**Check:**
1. Verify qBittorrent's **Default Save Path** is `/media/downloads`
2. Verify Arr service's **Root Folder** is NOT `/media/downloads`
3. Check **Remote Path Mappings** in Arr service
4. Check Arr service logs for import errors
5. Verify file permissions on Storage Box

### VPN Connection Issues

**Check Gluetun Status:**
```bash
docker logs gluetun | tail -50
docker exec gluetun curl -s https://api.ipify.org
```

**Verify VPN IP:**
- qBittorrent should show the same IP as Gluetun
- If IPs don't match, restart both containers

---

## 📊 Summary

### Correct Paths

| Service | Download Path | Root Folder | Purpose |
|---------|--------------|-------------|---------|
| **qBittorrent** | `/media/downloads` | - | Staging area for all downloads |
| **Lidarr** | - | `/media/music` | Final organized music location |
| **Radarr** | - | `/media/movies` | Final organized movie location |
| **Sonarr** | - | `/media/tv` | Final organized TV location |
| **LazyLibrarian** | - | `/media/audiobooks` | Final organized audiobook location |

### Key Rules

1. ✅ **qBittorrent downloads to:** `/media/downloads` (staging area)
2. ✅ **Arr services root folders:** Separate from download directory
3. ✅ **Never set root folder to:** `/media/downloads` (this is a download directory, not a root folder)
4. ✅ **Remote Path Mappings:** Configure for compatibility (even if paths are the same)

Following these rules will eliminate health check warnings and ensure proper file organization! 🎉

---

## ✅ Quick Setup Checklist

- [ ] qBittorrent accessible at `https://anduin.kooka-lake.ts.net:8085`
- [ ] Default Save Path set to `/media/downloads`
- [ ] Incomplete downloads set to `/incomplete` (tmpfs)
- [ ] Category-based subdirectories disabled (or configured with Remote Path Mappings)
- [ ] Arr services root folders configured (NOT `/media/downloads`)
- [ ] Remote Path Mappings configured in Arr services
- [ ] VPN connection verified (no IP leaks)
- [ ] Security checks passed

---

**Your qBittorrent is now configured and secure!** 🔒
