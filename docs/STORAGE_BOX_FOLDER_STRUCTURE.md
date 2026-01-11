# Storage Box Folder Structure Documentation

**Storage Box:** `u529830.your-storagebox.de`  
**Size:** 5TB  
**Mount Point:** `/mnt/storagebox`  
**Date Documented:** 2026-01-11  
**Date Updated:** 2026-01-11 (New Storage Box created)

---

## 📁 Complete Folder Structure

### Root Level Directories

```
/mnt/storagebox/
├── audiobooks/          # LazyLibrarian → Audiobookshelf
├── backups/             # System backups
├── books/               # LazyLibrarian ebooks
├── downloads/           # qBittorrent staging area (Arr services import from here)
├── home-videos/         # Personal videos
├── lost+found/          # System directory (can be ignored)
├── media/               # General media storage
├── movies/              # Radarr → Jellyfin
│   └── Hidden Figures (2016)/  # Example movie folder
├── music/               # Lidarr → Navidrome
├── photos/              # Photo storage
├── podcasts/            # LazyLibrarian → Audiobookshelf
├── .ssh/                # SSH keys/config (hidden directory)
└── tv-shows/            # Sonarr → Jellyfin
```

---

## 📊 Directory Usage and Purpose

### Media Directories (Arr Stack → Media Servers)

| Directory | Source Service | Destination Service | Purpose |
|-----------|---------------|---------------------|---------|
| `/movies/` | Radarr | Jellyfin | Final organized movie library |
| `/tv-shows/` | Sonarr | Jellyfin | Final organized TV show library |
| `/music/` | Lidarr | Navidrome | Final organized music library |
| `/audiobooks/` | LazyLibrarian | Audiobookshelf | Final organized audiobook library |
| `/podcasts/` | LazyLibrarian | Audiobookshelf | Final organized podcast library |
| `/books/` | LazyLibrarian | (Future) | Ebook library |

### Staging and Processing

| Directory | Service | Purpose |
|-----------|---------|---------|
| `/downloads/` | qBittorrent | Staging area for completed downloads (Arr services import from here) |

### Other Directories

| Directory | Purpose |
|-----------|---------|
| `/backups/` | System and application backups |
| `/home-videos/` | Personal video storage |
| `/photos/` | Photo storage |
| `/media/` | General media storage |
| `/.ssh/` | SSH configuration (hidden) |

---

## 🔄 Workflow

### Download and Organization Flow

1. **qBittorrent Downloads:**
   - Incomplete: `/incomplete` (tmpfs in RAM - 10GB)
   - Completed: `/downloads/` (staging area)

2. **Arr Services Import:**
   - **Radarr:** `/downloads/` → `/movies/`
   - **Sonarr:** `/downloads/` → `/tv-shows/`
   - **Lidarr:** `/downloads/` → `/music/`
   - **LazyLibrarian:** `/downloads/` → `/audiobooks/` or `/books/`

3. **Media Servers Read:**
   - **Jellyfin:** Reads from `/movies/` and `/tv-shows/`
   - **Navidrome:** Reads from `/music/`
   - **Audiobookshelf:** Reads from `/audiobooks/` and `/podcasts/`

---

## 📝 Recreation Steps (After Creating New Storage Box)

### 1. Create Directory Structure

```bash
# SSH to server
ssh rodkode@95.216.176.147

# Create all directories
sudo mkdir -p /mnt/storagebox/{audiobooks,backups,books,downloads,home-videos,media,movies,music,photos,podcasts,tv-shows}

# Set permissions (if needed)
sudo chown -R deploy:deploy /mnt/storagebox/*
sudo chmod -R 755 /mnt/storagebox/*
```

### 2. Verify Structure

```bash
# List all directories
ls -la /mnt/storagebox/

# Verify structure matches
find /mnt/storagebox -maxdepth 1 -type d | sort
```

### 3. Update Docker Compose Volumes

The `hetzner-media` volume should automatically map to `/mnt/storagebox`. Verify:

```bash
docker volume inspect homelab_hetzner-media
```

Should show:
```json
"Mountpoint": "/var/lib/docker/volumes/homelab_hetzner-media/_data"
```

Which is a bind mount to `/mnt/storagebox`.

---

## ⚠️ Important Notes

1. **Hidden Directory:** `/.ssh/` is a hidden directory - ensure it's recreated if needed
2. **Lost+Found:** This is a system directory created automatically - no need to recreate
3. **Permissions:** All directories should be owned by `deploy:deploy` (uid:1000, gid:1000) or the user running Docker containers
4. **Subdirectories:** Some services create subdirectories automatically (e.g., `/movies/Movie Name (Year)/`)

---

## 🔍 Current Status

- **Storage Box:** `u526046.your-storagebox.de`
- **Current Size:** 1.3TB (should be 5TB)
- **Used:** 763GB
- **Available:** 509GB
- **Usage:** 61%

**Action Required:** Create new Storage Box with 5TB capacity and recreate this folder structure.

---

## 📋 Checklist for New Storage Box Setup

- [ ] Create new Storage Box with 5TB capacity
- [ ] Mount Storage Box at `/mnt/storagebox`
- [ ] Create all root-level directories
- [ ] Set correct permissions (deploy:deploy, 755 for dirs)
- [ ] Verify Docker volume mapping (`hetzner-media`)
- [ ] Test write access from containers
- [ ] Verify services can access their respective directories
- [ ] Restore/transfer any existing data if needed

---

## 🔗 Related Documentation

- [Storage Box Setup Guide](./STORAGE_BOX_SETUP.md)
- [Arr Stack Media Integration](./ARR_STACK_MEDIA_INTEGRATION.md)
- [qBittorrent Arr Configuration](./QBITTORRENT_ARR_CONFIGURATION.md)
