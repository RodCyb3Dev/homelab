# Arr-Stack Integration with Media Servers

This document explains how the Arr-stack (Lidarr, Radarr, Sonarr, and LazyLibrarian) integrates with media servers (Navidrome, Jellyfin, and Audiobookshelf) to create an automated media management workflow.

**See also:** [`QBITTORRENT_ARR_CONFIGURATION.md`](./QBITTORRENT_ARR_CONFIGURATION.md) for detailed qBittorrent setup and troubleshooting health check warnings.

---

## 🔄 Integration Overview

The Arr-stack acts as the **automation layer** that downloads and organizes media, while Navidrome and Audiobookshelf act as the **consumption layer** that serves the media to users. They work together through shared storage on the Hetzner Storage Box.

### Architecture Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    Hetzner Storage Box                          │
│              (u526046.your-storagebox.de)                       │
│                                                                 │
│  /mnt/storagebox/                                               │
│  ├── music/          ← Lidarr writes here                      │
│  ├── audiobooks/    ← LazyLibrarian writes here                │
│  └── podcasts/      ← (Manual uploads or future automation)    │
└─────────────────────────────────────────────────────────────────┘
         ▲                                    ▲
         │                                    │
         │ (read-only)                        │ (read-only)
         │                                    │
┌────────┴────────┐                  ┌────────┴────────┐
│   Navidrome     │                  │ Audiobookshelf │
│  (Music Server) │                  │ (Audiobook      │
│                 │                  │  Server)       │
└─────────────────┘                  └────────────────┘
         ▲                                    ▲
         │                                    │
         │ (serves to users)                  │ (serves to users)
         │                                    │
    ┌────┴────┐                          ┌────┴────┐
    │  Users  │                          │  Users  │
    └─────────┘                          └─────────┘
```

---

## 🎵 Lidarr → Navidrome Integration

### How It Works

1. **Lidarr** (Music Manager)
   - Searches for music releases using **Prowlarr** (indexer manager)
   - Downloads music via **qBittorrent** (through Gluetun VPN)
   - Organizes files into artist/album structure
   - Saves to: `/media/music` (which maps to `hetzner-media:/music`)

2. **Navidrome** (Music Server)
   - Reads from: `/music` (same `hetzner-media:/music` volume, read-only)
   - Auto-scans every hour (`ND_SCANNER_SCHEDULE=@every 1h`)
   - Detects new files via file watcher (`ND_SCANNER_WATCHERWAIT=5s`)
   - Indexes and serves music to users

### Configuration Steps

#### 1. Configure Lidarr

Access Lidarr: `https://anduin.kooka-lake.ts.net:8686`

**Set Root Folder:**

1. Navigate to **Settings → Media Management** (`/settings/mediamanagement`)
2. In the **Root Folders** section, you'll see your current root folder(s)
3. Click on the existing root folder (or click **Add Root Folder** if none exists)
4. In the **Edit Root Folder** modal:
   - **Name:** `Music` (or any descriptive name)
   - **Path:** `/media/music` ⚠️ **Critical:** Change from `/media/downloads` to `/media/music`
   - **Monitor:** `All Albums` (or your preference)
     - Options: `All Albums`, `Future Albums`, `Missing Albums`, `Existing Albums`, `First Album`, `Latest Album`, `None`
   - **Monitor New Albums:** `All Albums` (or your preference)
     - Options: `All Albums`, `New Albums Only`, `None`
   - **Quality Profile:** Select your preferred quality profile (e.g., `Any`, `MP3 320`, `FLAC`)
   - **Metadata Profile:** `Standard` (or your preference)
   - **Default Lidarr Tags:** (optional) Add tags if you want to organize music
5. Click **Save**

⚠️ **Critical Configuration:**
- The path `/media/music` maps to `hetzner-media:/music` on the Storage Box
- This is where Lidarr will organize downloaded music files **after** they're downloaded
- **This must be different from your download client's download directory**
  - qBittorrent downloads to `/incomplete` (tmpfs in RAM) first
  - Then qBittorrent moves completed downloads to `/media/downloads` (staging area)
  - Lidarr then imports and organizes files from `/media/downloads` to `/media/music` (final location)
- Navidrome reads from the same location (`/music`), so files organized here will be automatically available

**⚠️ Health Check Fix:**
If you see warnings about download directories:
1. **qBittorrent's "Default Save Path"** must be set to `/media/downloads` (staging area, NOT a root folder)
2. **qBittorrent's "Incomplete downloads"** must be set to `/incomplete`
3. **Lidarr's Root Folder** must be `/media/music` (NOT `/media/downloads` or `/media/downloads/music`)
4. **Remote Path Mappings** in Lidarr must correctly map qBittorrent's paths

**Configure Download Client (qBittorrent):**

1. Go to **Settings → Download Clients**
2. Click **Add Download Client** → **qBittorrent**
3. Configure:
   - **Name:** `qBittorrent`
   - **Host:** `gluetun` (internal Docker network name, not `localhost` or `127.0.0.1`)
   - **Port:** `8085`
   - **Username:** Your qBittorrent username (default: `admin`)
   - **Password:** Your qBittorrent password
   - **Category:** (optional) `music` or leave empty
   - **Priority:** `Normal`
   - **Initial State:** `Start`
4. Click **Test** to verify connection
5. Click **Save**

**Configure Download Client Settings:**
- Go to **Settings → Media Management → Completed Download Handling**
- **Enable:** ✅ **Completed Download Handling**
- **Remove Completed:** ✅ (optional) Automatically remove completed downloads from qBittorrent
- **Check for Finished Downloads Interval:** `1` minute (or your preference)

**Configure Remote Path Mappings:**
1. Go to **Settings → Media Management → Remote Path Mappings**
2. Click **Add Remote Path Mapping**
3. Configure:
   - **Host:** `gluetun` (or `qbittorrent` if using category-based paths)
   - **Remote Path:** `/media/downloads` (where qBittorrent saves completed downloads)
   - **Local Path:** `/media/downloads` (same path, since all services share the same volume)
4. Click **Save**

**Why Remote Path Mappings?**
- When Lidarr and qBittorrent are in the same Docker network, they see the same paths
- Remote Path Mappings ensure Lidarr can find files that qBittorrent downloaded
- Since both use `hetzner-media:/media`, the paths are the same, but this mapping ensures compatibility

**Configure Indexers (Prowlarr):**
- Go to **Settings → Indexers**
- Add Prowlarr:
  - **Host:** `gluetun`
  - **Port:** `9696`
  - **API Key:** From Prowlarr settings

**Configure Quality Profiles:**

1. Go to **Settings → Quality Profiles**
2. You can use the default **Any** profile, or create custom profiles:
   - Click **Add Quality Profile**
   - **Name:** e.g., `MP3 320`, `FLAC`, `High Quality`
   - **Upgrade Allowed:** ✅ (allows upgrading to better quality)
   - **Quality Groups:** Select preferred formats and bitrates:
     - **MP3:** 320 kbps, 256 kbps, 192 kbps, etc.
     - **FLAC:** Lossless
     - **M4A:** AAC formats
   - **Preferred:** Drag quality groups to set priority order
3. Click **Save**

**Recommended:** Start with the **Any** profile, then create custom profiles as needed based on your preferences.

#### 2. Configure Navidrome

Access Navidrome: `https://bard.kooka-lake.ts.net`

**Music Folder:**
- Already configured: `/music` (via `ND_MUSICFOLDER=/music`)
- Navidrome automatically scans this folder

**Scanner Settings:**
- **Auto-scan:** Every hour (`@every 1h`)
- **Scan on startup:** Enabled
- **File watcher:** 5-second delay (avoids scanning incomplete files)

**Manual Scan:**
- If you want to trigger an immediate scan:
  - Go to **Settings → Music Folders**
  - Click **Scan Now**

### Workflow Example

1. **Add Artist in Lidarr:**
   - Search for an artist (e.g., "The Beatles")
   - Click **Add Artist**
   - Select albums to monitor

2. **Lidarr Downloads:**
   - Lidarr searches via Prowlarr
   - Sends download to qBittorrent (through VPN)
   - qBittorrent downloads to `/media/music/The Beatles/Album Name/`

3. **Lidarr Organizes:**
   - Renames files according to your naming scheme
   - Moves to final location: `/media/music/The Beatles/Album Name/`

4. **Navidrome Detects:**
   - File watcher detects new files (waits 5 seconds)
   - Scanner indexes the new music
   - Music appears in Navidrome UI

5. **Users Access:**
   - Music is available in Navidrome at `https://bard.kooka-lake.ts.net`
   - Can stream, download, or add to playlists

---

## 🎬 Radarr & Sonarr → Jellyfin Integration

### How It Works

**Radarr** (Movie Manager) and **Sonarr** (TV Manager) work similarly to Lidarr:

1. **Radarr/Sonarr** search for releases using **Prowlarr**
2. Download via **qBittorrent** (through Gluetun VPN)
3. Organize files and save to:
   - **Radarr:** `/media/movies` (which maps to `hetzner-media:/movies`)
   - **Sonarr:** `/media/tv` (which maps to `hetzner-media:/tv`)

4. **Jellyfin** (Media Server)
   - Reads from: `/media/movies` and `/media/tv` (same `hetzner-media` volume, read-only)
   - Auto-detects new files via library scanning
   - Serves movies and TV shows to users

### Configuration Steps

#### Configure Radarr

Access Radarr: `https://anduin.kooka-lake.ts.net:7878`

**Set Root Folder:**
1. Go to **Settings → Media Management → Root Folders**
2. Edit root folder:
   - **Path:** `/media/movies` ⚠️ **NOT `/media/downloads`**
   - This is where Radarr organizes movies after import

**Configure Download Client (qBittorrent):**
- Same as Lidarr configuration (see above)
- **Host:** `gluetun`
- **Port:** `8085`

**Configure Remote Path Mappings:**
- **Host:** `gluetun`
- **Remote Path:** `/media/downloads`
- **Local Path:** `/media/downloads`

#### Configure Sonarr

Access Sonarr: `https://anduin.kooka-lake.ts.net:8989`

**Set Root Folder:**
1. Go to **Settings → Media Management → Root Folders**
2. Edit root folder:
   - **Path:** `/media/tv` ⚠️ **NOT `/media/downloads`**
   - This is where Sonarr organizes TV shows after import

**Configure Download Client (qBittorrent):**
- Same as Lidarr configuration
- **Host:** `gluetun`
- **Port:** `8085`

**Configure Remote Path Mappings:**
- **Host:** `gluetun`
- **Remote Path:** `/media/downloads`
- **Local Path:** `/media/downloads`

---

## 📚 LazyLibrarian → Audiobookshelf Integration

### How It Works

1. **LazyLibrarian** (Book/Audiobook Manager)
   - Searches for audiobooks using **Prowlarr** (indexer manager)
   - Downloads audiobooks via **qBittorrent** (through Gluetun VPN)
   - Organizes files into author/book structure
   - Saves to: `/media/audiobooks` (which maps to `hetzner-media:/audiobooks`)

2. **Audiobookshelf** (Audiobook Server)
   - Reads from: `/audiobooks` (same `hetzner-media:/audiobooks` volume, read-only)
   - Requires manual library scan (or can be configured for auto-scan)
   - Indexes and serves audiobooks to users

### Configuration Steps

#### 1. Configure LazyLibrarian

Access LazyLibrarian: `https://anduin.kooka-lake.ts.net:5299`

**Set Download Path:**
- Go to **Settings → Folders**
- Set **Audiobook Folder:** `/media/audiobooks`
- This is where LazyLibrarian will save downloaded audiobooks

**Configure Download Client (qBittorrent):**
- Go to **Settings → Download Clients**
- Add qBittorrent:
  - **Host:** `gluetun`
  - **Port:** `8085`
  - **Username/Password:** Your qBittorrent credentials

**Configure Indexers (Prowlarr):**
- Go to **Settings → Providers**
- Add Prowlarr:
  - **Host:** `gluetun`
  - **Port:** `9696`
  - **API Key:** From Prowlarr settings (Settings → General → API Key)

**Enable API in LazyLibrarian (for Prowlarr integration):**
- Go to **Config → Interface → Startup**
- Enable **"Enable API"** checkbox
- Copy the displayed API key
- Use this API key in Prowlarr: **Settings → Apps → Add LazyLibrarian**
  - See [LazyLibrarian API Key Guide](./LAZYLIBRARIAN_API_KEY.md) for detailed steps

**Configure Naming:**
- Go to **Settings → Naming**
- Set naming scheme for audiobooks (e.g., `{Author}/{Book Title}/{Book Title}.{ext}`)

#### 2. Configure Audiobookshelf

Access Audiobookshelf: `https://gandalf.kooka-lake.ts.net`

**Add Library:**
- Go to **Settings → Libraries**
- Click **Add Library**
- **Name:** `Audiobooks`
- **Path:** `/audiobooks`
- **Type:** `Audiobooks`
- Click **Save**

**Configure Metadata:**
- Go to **Settings → Metadata**
- Enable providers:
  - ✅ **OpenLibrary** (for book metadata)
  - ✅ **Audible** (for audiobook metadata)
  - ✅ **iTunes Podcasts** (if you also use podcasts)

**Manual Scan:**
- Go to **Settings → Libraries**
- Select your library
- Click **Scan Now** to index existing files
- Or use **Settings → Libraries → Scan All Libraries**

**Auto-Scan (Optional):**
- Audiobookshelf doesn't have built-in file watching like Navidrome
- You can set up a scheduled scan in Audiobookshelf settings
- Or use external tools (cron, systemd timer) to trigger scans

### Workflow Example

1. **Add Book in LazyLibrarian:**
   - Search for a book (e.g., "The Hobbit")
   - Click **Add to Wanted**
   - LazyLibrarian searches for audiobook releases

2. **LazyLibrarian Downloads:**
   - Finds release via Prowlarr
   - Sends download to qBittorrent (through VPN)
   - qBittorrent downloads to `/media/audiobooks/J.R.R. Tolkien/The Hobbit/`

3. **LazyLibrarian Organizes:**
   - Renames files according to your naming scheme
   - Moves to final location: `/media/audiobooks/J.R.R. Tolkien/The Hobbit/`

4. **Audiobookshelf Detects:**
   - **Option 1:** Manual scan (Settings → Libraries → Scan Now)
   - **Option 2:** Scheduled scan (if configured)
   - Audiobookshelf indexes the new audiobook

5. **Users Access:**
   - Audiobook is available in Audiobookshelf at `https://gandalf.kooka-lake.ts.net`
   - Can stream, download, or track progress

---

## 🔗 Shared Storage Architecture

All services share the same `hetzner-media` Docker volume, which maps to `/mnt/storagebox` on the host:

### Volume Mappings

**Arr-Stack Services (Write Access):**
- **Lidarr:** `/media` → `hetzner-media` (read-write)
  - Root Folder: `/media/music` (final organized location)
- **Radarr:** `/media` → `hetzner-media` (read-write)
  - Root Folder: `/media/movies` (final organized location)
- **Sonarr:** `/media` → `hetzner-media` (read-write)
  - Root Folder: `/media/tv` (final organized location)
- **LazyLibrarian:** `/media` → `hetzner-media` (read-write)
  - Download Path: `/media/audiobooks` (final organized location)
- **qBittorrent:** `/media` → `hetzner-media` (read-write)
  - Default Save Path: `/media/downloads` (staging area for all downloads)
  - Incomplete Path: `/incomplete` (tmpfs in RAM)

**Media Server Services (Read-Only Access):**
- **Jellyfin:** `/media` → `hetzner-media` (read-only)
  - Reads from: `/media/movies`, `/media/tv`
- **Navidrome:** `/music` → `hetzner-media:/music` (read-only)
- **Audiobookshelf:** `/audiobooks` → `hetzner-media:/audiobooks` (read-only)
- **Audiobookshelf:** `/podcasts` → `hetzner-media:/podcasts` (read-only)

### Storage Box Structure

```
/mnt/storagebox/
├── downloads/          # qBittorrent staging area (temporary)
│   ├── music/          # Music downloads (before Lidarr organizes)
│   ├── movies/         # Movie downloads (before Radarr organizes)
│   └── tv/             # TV downloads (before Sonarr organizes)
├── music/              # Lidarr final location → Navidrome reads
│   ├── Artist 1/
│   │   ├── Album 1/
│   │   └── Album 2/
│   └── Artist 2/
│       └── Album 1/
├── movies/             # Radarr final location → Jellyfin reads
│   └── Movie Name (Year)/
│       └── Movie Name (Year).mkv
├── tv/                 # Sonarr final location → Jellyfin reads
│   └── Show Name/
│       └── Season 01/
│           └── Show Name - S01E01.mkv
├── audiobooks/         # LazyLibrarian final location → Audiobookshelf reads
│   ├── Author 1/
│   │   ├── Book 1/
│   │   └── Book 2/
│   └── Author 2/
│       └── Book 1/
└── podcasts/           # Manual uploads or future automation
    └── Podcast Name/
        └── Episode 1.mp3
```

### Download Workflow

**For All Arr Services (Lidarr, Radarr, Sonarr, LazyLibrarian):**

1. **qBittorrent Downloads:**
   - Incomplete files: `/incomplete` (tmpfs in RAM - 10GB)
   - Completed files: `/media/downloads` (staging area on Storage Box)

2. **Arr Service Imports:**
   - Lidarr: Imports from `/media/downloads` → Organizes to `/media/music`
   - Radarr: Imports from `/media/downloads` → Organizes to `/media/movies`
   - Sonarr: Imports from `/media/downloads` → Organizes to `/media/tv`
   - LazyLibrarian: Imports from `/media/downloads` → Organizes to `/media/audiobooks`

3. **Media Server Indexes:**
   - Jellyfin: Reads from `/media/movies` and `/media/tv`
   - Navidrome: Reads from `/music` (auto-scans every hour)
   - Audiobookshelf: Reads from `/audiobooks` (manual/scheduled scan)

---

## 🚀 Automation Benefits

### Automated Workflow

1. **Add Content:**
   - Add artist/book in Lidarr/LazyLibrarian
   - Set quality preferences and monitoring options

2. **Automatic Download:**
   - Arr-stack searches for releases
   - Downloads via qBittorrent (through VPN)
   - Organizes files automatically

3. **Automatic Indexing:**
   - **Navidrome:** Auto-scans every hour
   - **Audiobookshelf:** Manual or scheduled scan

4. **Automatic Availability:**
   - Content appears in media servers
   - Users can immediately stream/download

### Quality Management

- **Lidarr:** Manages music quality (MP3, FLAC, etc.)
- **LazyLibrarian:** Manages audiobook formats and quality
- **Prowlarr:** Manages indexers and search quality
- **qBittorrent:** Handles actual downloads (through VPN for privacy)

---

## ⚙️ Advanced Configuration

### Navidrome Auto-Scan Optimization

Navidrome is already configured for optimal auto-scanning:

```yaml
- ND_SCANNER_SCHEDULE=@every 1h      # Scan every hour
- ND_SCANNER_SCANONSTARTUP=true      # Scan on container start
- ND_SCANNER_WATCHERWAIT=5s          # Wait 5s after file change
```

This means:
- New music from Lidarr is detected within 5 seconds (via file watcher)
- Full library scan runs every hour (catches any missed files)
- Scan runs on startup (ensures library is up-to-date after restarts)

### Audiobookshelf Scan Automation

Audiobookshelf doesn't have built-in file watching, but you can:

**Option 1: Scheduled Scan in Audiobookshelf UI**
- Go to **Settings → Libraries**
- Configure scan schedule (if available in your version)

**Option 2: External Cron Job**
```bash
# Add to crontab on server
0 * * * * docker exec audiobookshelf curl -X POST http://localhost/api/libraries/scan
```

**Option 3: Webhook Integration (Future)**
- Some Arr-stack services support webhooks
- Could trigger Audiobookshelf scan after download completes

---

## 🔍 Monitoring & Troubleshooting

### Check Download Status

**Lidarr:**
- Go to **Activity** tab
- See download queue and completed downloads
- Check for any errors

**LazyLibrarian:**
- Go to **Wanted** tab
- See books being searched/downloaded
- Check **Status** for any issues

### Check Media Server Status

**Navidrome:**
- Check **Activity** panel for scan progress
- View logs: `docker logs navidrome`
- Verify music appears in library

**Audiobookshelf:**
- Check **Settings → Libraries** for scan status
- View logs: `docker logs audiobookshelf`
- Verify audiobooks appear in library

### Common Issues

**Music/Audiobooks Not Appearing:**
1. Check file permissions on Storage Box
2. Verify files are in correct directory structure
3. Trigger manual scan in media server
4. Check Arr-stack logs for download errors

**Slow Indexing:**
- Large libraries take time to scan
- Navidrome scans incrementally (only new/changed files)
- Audiobookshelf may need full scan for new directories

**Permission Errors:**
- Ensure Storage Box is mounted with correct permissions
- Verify `PUID`/`PGID` match Storage Box ownership
- Check Docker volume permissions

---

## 📊 Summary

### All Arr Services Configuration

**Root Folders (Final Organized Location):**
- **Lidarr:** `/media/music` → Navidrome reads from `/music`
- **Radarr:** `/media/movies` → Jellyfin reads from `/media/movies`
- **Sonarr:** `/media/tv` → Jellyfin reads from `/media/tv`
- **LazyLibrarian:** `/media/audiobooks` → Audiobookshelf reads from `/audiobooks`

**Download Staging Area (qBittorrent):**
- **All Arr services:** qBittorrent downloads to `/media/downloads`
- Arr services import from here and organize to their root folders

**⚠️ Critical Rule:**
- **Never set root folders to `/media/downloads`** - this is a download staging area, not a root folder
- Each Arr service must have its own root folder separate from the download directory

### Integration Points

| Service | Role | Writes To | Reads From |
|---------|------|-----------|------------|
| **Lidarr** | Music Manager | `/media/music` | - |
| **Navidrome** | Music Server | - | `/music` (read-only) |
| **LazyLibrarian** | Book Manager | `/media/audiobooks` | - |
| **Audiobookshelf** | Audiobook Server | - | `/audiobooks` (read-only) |
| **qBittorrent** | Download Client | `/media/*` | - |
| **Prowlarr** | Indexer Manager | - | - |

### Workflow Summary

1. **User adds content** → Lidarr/LazyLibrarian
2. **Arr-stack searches** → Prowlarr
3. **Arr-stack downloads** → qBittorrent (VPN)
4. **Arr-stack organizes** → Storage Box
5. **Media server detects** → Navidrome (auto) / Audiobookshelf (manual/scheduled)
6. **Users consume** → Stream/download from media servers

This creates a fully automated media management system where you add content once, and it's automatically downloaded, organized, and made available for streaming! 🎉
