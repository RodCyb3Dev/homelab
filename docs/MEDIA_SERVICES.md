# 🎵 Media Services Guide

This guide covers the media streaming services in your homelab: Navidrome and Audiobookshelf.

---

## 🎵 Navidrome - Music Streaming Server

**URL:** `https://navidrome.rodneyops.com`

### Overview

Navidrome is a self-hosted music streaming server compatible with Subsonic/Airsonic clients. Stream your personal music collection anywhere.

### Features

- ✅ Subsonic/Airsonic API compatible
- ✅ Web player with modern UI
- ✅ Mobile apps support (iOS, Android)
- ✅ Multi-user support
- ✅ Playlists and favorites
- ✅ Smart playlists
- ✅ Transcoding support
- ✅ Last.fm scrobbling
- ✅ Artist radio

### Storage Structure

Music files should be organized on your Hetzner Storage Box:

```
/mnt/storagebox/
└── music/
    ├── Artist 1/
    │   └── Album 1/
    │       ├── 01 - Track.mp3
    │       └── cover.jpg
    ├── Artist 2/
    │   └── Album 2/
    │       └── ...
    └── ...
```

### Supported Formats

- **Audio:** MP3, FLAC, OGG, M4A, WMA, AAC, ALAC, APE
- **Playlists:** M3U, PLS
- **Metadata:** ID3v1, ID3v2, Vorbis Comments, APE tags

### Mobile Apps

#### iOS

- **play:Sub** - Premium Subsonic client
- **substreamer** - Free alternative

#### Android

- **Symfonium** - Modern and feature-rich (recommended)
- **DSub** - Classic Subsonic client
- **Ultrasonic** - Open source client

#### Desktop

- **Sublime Music** - Linux GTK client
- **Sonixd** - Cross-platform Electron app

### Configuration

Server details for mobile apps:

```
Server: https://navidrome.rodneyops.com
Username: (your username)
Password: (your password)
```

### First-Time Setup

1. **Access Navidrome:**

   ```bash
   open https://navidrome.rodneyops.com
   ```

2. **Create Admin Account:**
   - First user to sign up becomes admin
   - Username: your choice
   - Password: secure password

3. **Upload Music:**
   - Upload to Storage Box: `/mnt/storagebox/music/`
   - Or via SFTP: `sftp://u525677@u525677.your-storagebox.de/music`

4. **Scan Library:**
   - Automatically scans every hour
   - Manual scan: Settings → "Scan Library Now"

### Advanced Configuration

Edit `config/navidrome/navidrome.toml`:

```toml
# Scan schedule (cron format)
ScanSchedule = "@every 1h"

# Enable transcoding
EnableTranscodingConfig = true

# Last.fm integration
LastFM.ApiKey = "your-api-key"
LastFM.Secret = "your-secret"

# Max transcoding cache size (MB)
TranscodingCacheSize = "1GB"
```

---

## 📚 Audiobookshelf - Audiobook & Podcast Server

**URL:** `https://audiobooks.rodneyops.com`

### Overview

Audiobookshelf is a dedicated audiobook and podcast server with a beautiful web player and mobile apps.

### Features

- ✅ Audiobook library management
- ✅ Podcast management with auto-download
- ✅ Progress tracking across devices
- ✅ Sleep timer
- ✅ Playback speed control
- ✅ Chapter support
- ✅ Multi-user support with user management
- ✅ Mobile apps (iOS & Android)
- ✅ Book metadata fetching
- ✅ Series support
- ✅ Collections and playlists

### Storage Structure

Audiobooks and podcasts should be organized on your Hetzner Storage Box:

```
/mnt/storagebox/
├── audiobooks/
│   ├── Author Name/
│   │   └── Book Title/
│   │       ├── cover.jpg
│   │       ├── Chapter 01.mp3
│   │       ├── Chapter 02.mp3
│   │       └── metadata.json
│   └── ...
└── podcasts/
    ├── Podcast Name/
    │   ├── cover.jpg
    │   └── Episode 001.mp3
    └── ...
```

### Supported Formats

**Audio:**

- MP3, M4B, M4A, FLAC, OGG, AAC, WMA

**Ebooks:**

- EPUB, PDF, MOBI, AZW3, CBR, CBZ

**Metadata:**

- metadata.json, desc.txt, reader.txt

### Mobile Apps

#### iOS

- **Audiobookshelf** (Official)
- Free on App Store
- CarPlay support

#### Android

- **Audiobookshelf** (Official)
- Free on Google Play
- Android Auto support

### First-Time Setup

1. **Access Audiobookshelf:**

   ```bash
   open https://audiobooks.rodneyops.com
   ```

2. **Initial Setup Wizard:**
   - Create root user account
   - Set library paths:
     - Audiobooks: `/audiobooks`
     - Podcasts: `/podcasts`

3. **Upload Content:**
   - Via Storage Box SFTP
   - Or mount locally and copy

4. **Scan Libraries:**
   - Click "Scan" button in each library
   - Automatic scanning: Settings → "Library Settings"

### Library Organization

**Audiobook folder structure:**

```
Author Name/
└── Book Title/
    ├── cover.jpg (optional)
    ├── 01 - Chapter One.mp3
    ├── 02 - Chapter Two.mp3
    └── ...
```

**Podcast folder structure:**

```
Podcast Name/
├── cover.jpg (optional)
├── 001 - Episode Title.mp3
├── 002 - Episode Title.mp3
└── ...
```

### Features Guide

#### Progress Tracking

- Syncs across all devices
- Resume from where you left off
- Per-user progress tracking

#### Collections

- Create custom collections
- Group related books
- Share collections with users

#### Series Management

- Automatically detects series
- Shows reading order
- Tracks series progress

#### Podcast Features

- Auto-download new episodes
- Episode queue management
- Playback history

### Mobile App Setup

1. **Download app** from App Store or Google Play
2. **Server URL:** `https://audiobooks.rodneyops.com`
3. **Login** with your credentials
4. **Settings:**
   - Enable offline mode
   - Set download quality
   - Configure sleep timer

### Advanced Configuration

Settings → Server Settings:

```yaml
# Scanner settings
Scanner Settings:
  - Scan Interval: 24 hours
  - Prefer audio metadata: true
  - Prefer OPF metadata: false

# Backup settings
Backup Settings:
  - Automatic backups: Daily at 2 AM
  - Backup retention: 7 days
  - Include metadata images: true

# Authentication
Authentication:
  - Allow guest access: false
  - Password requirements: Strong
  - Session timeout: 7 days
```

---

## 📊 Storage Requirements

### Recommended Storage Structure

```bash
/mnt/storagebox/
├── music/              # 100-500 GB (your music collection)
├── audiobooks/         # 50-200 GB (typical collection)
├── podcasts/           # 10-50 GB (grows over time)
└── backups/           # As needed
```

### Backup Strategy

**Metadata Backups (Daily):**

```bash
# Navidrome
/config/navidrome/navidrome.db → Backed up daily

# Audiobookshelf
/config/audiobookshelf/config/metadata.db → Backed up daily
```

**Media Files:**

- Original files on Hetzner Storage Box
- Consider separate backup of Storage Box

---

## 🔒 Security & Access

### Authentication

Both services are protected by:

1. **Authelia** - Single Sign-On with 2FA
2. **Traefik** - HTTPS with Let's Encrypt certificates
3. **Individual service authentication** - Username/password per service

### Network Access

- **Public:** Available via HTTPS from anywhere
- **Private Network:** Accessible via Tailscale
- **Storage:** Read-only mount for security

### User Management

#### Navidrome

- Admin user created on first signup
- Add users: Settings → Users → "Add User"
- User roles: Admin or Regular

#### Audiobookshelf

- Root user created during setup
- Add users: Settings → Users → "Add User"
- User permissions: Admin, User, or Guest

---

## 🧪 Testing

### Test Navidrome

```bash
# Check service health
docker logs navidrome

# Test web interface
curl -k https://navidrome.rodneyops.com

# Check music folder mount
docker exec navidrome ls -lah /music

# Force library scan
# UI: Settings → Scan Library Now
```

### Test Audiobookshelf

```bash
# Check service health
docker logs audiobookshelf

# Test web interface
curl -k https://audiobooks.rodneyops.com

# Check audiobooks folder mount
docker exec audiobookshelf ls -lah /audiobooks

# Check podcasts folder mount
docker exec audiobookshelf ls -lah /podcasts

# Force library scan
# UI: Library → Three dots → Scan
```

---

## 🐛 Troubleshooting

### Navidrome Issues

**Problem:** Music not showing up

```bash
# Check mount
docker exec navidrome ls /music

# Check permissions
docker exec navidrome ls -la /music

# Force rescan
# UI: Settings → "Scan Library Now"
```

**Problem:** Transcoding not working

```bash
# Check ffmpeg
docker exec navidrome ffmpeg -version

# Check transcoding config
docker exec navidrome cat /data/navidrome.toml
```

### Audiobookshelf Issues

**Problem:** Audiobooks not detected

```bash
# Check folder structure
docker exec audiobookshelf ls -R /audiobooks | head -20

# Check scanner logs
docker logs audiobookshelf | grep -i scan

# Verify metadata
# UI: Library → Book → Three dots → "Match"
```

**Problem:** Podcast downloads failing

```bash
# Check network connectivity
docker exec audiobookshelf curl -I https://example.com/podcast.rss

# Check podcast logs
docker logs audiobookshelf | grep -i podcast

# Retry download
# UI: Podcast → Episode → Download
```

### Common Issues

**Mount point empty:**

```bash
# On Hetzner server, check Storage Box mount
df -h | grep storagebox

# Remount if needed
mount -a
```

**Permission denied:**

```bash
# Fix permissions on local config
sudo chown -R 1000:1000 config/navidrome
sudo chown -R 1000:1000 config/audiobookshelf
```

---

## 📚 Resources

### Navidrome

- **Documentation:** https://www.navidrome.org/docs/
- **GitHub:** https://github.com/navidrome/navidrome
- **Subsonic API:** http://www.subsonic.org/pages/api.jsp
- **Community:** https://github.com/navidrome/navidrome/discussions

### Audiobookshelf

- **Documentation:** https://www.audiobookshelf.org/docs
- **GitHub:** https://github.com/advplyr/audiobookshelf
- **Community:** https://github.com/advplyr/audiobookshelf/discussions
- **Discord:** https://discord.gg/audiobookshelf

### Mobile Apps

- **Navidrome Apps:** https://www.navidrome.org/docs/usage/apps/
- **Audiobookshelf Apps:** https://www.audiobookshelf.org/install

---

## ✅ Quick Reference

```bash
# Start services
docker compose up -d navidrome audiobookshelf

# View logs
docker logs -f navidrome
docker logs -f audiobookshelf

# Restart services
docker restart navidrome audiobookshelf

# Access services
https://navidrome.rodneyops.com
https://audiobooks.rodneyops.com

# Check resource usage
docker stats navidrome audiobookshelf
```

---

**Enjoy your personal media streaming server!** 🎵📚
