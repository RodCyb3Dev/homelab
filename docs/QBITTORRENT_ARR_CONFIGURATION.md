# qBittorrent Configuration for Arr-Stack

This guide explains how to properly configure qBittorrent to work with all Arr services (Lidarr, Radarr, Sonarr, LazyLibrarian) and avoid common health check warnings.

---

## ⚠️ Common Health Check Warnings

If you see these warnings in Lidarr/Radarr/Sonarr:

1. **"Download client qBittorrent places downloads in /media/downloads/music but this directory does not appear to exist inside the container"**
2. **"Download client qBittorrent places downloads in the root folder /media/downloads/. You should not download to a root folder."**

These indicate incorrect configuration. Follow this guide to fix them.

---

## 🔧 qBittorrent Configuration

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

## 🐛 Troubleshooting

### Warning: "Directory does not appear to exist"

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
