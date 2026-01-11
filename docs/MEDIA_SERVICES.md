# Media Services - Audiobookshelf & Navidrome

This guide covers the setup and configuration of Audiobookshelf and Navidrome, two media services that use the Hetzner Storage Box (`u526046.your-storagebox.de`) for media storage.

---

## 📋 Overview

The media services stack includes:

- **Audiobookshelf** (`gandalf.kooka-lake.ts.net`) - Audiobook and podcast server
  - The Grey wizard as lore-master and narrator
  - Hostname: `gandalf`
  - Port: `13378`

- **Navidrome** (`bard.kooka-lake.ts.net`) - Music server
  - Bard the Bowman, famed for his melodies
  - Hostname: `bard`
  - Port: `4533`

Both services:
- Use their own Tailscale containers for secure access
- Access the Hetzner Storage Box via the `hetzner-media` Docker volume
- Are deployed via Ansible
- Auto-start on server boot via systemd

---

## 🗄️ Storage Box Integration

Both services use the **Hetzner Storage Box** (`u526046.your-storagebox.de`) mounted at `/mnt/storagebox` on the server, which is exposed to Docker containers via the `hetzner-media` volume.

### Storage Structure

The Storage Box should be organized as follows:

```
/mnt/storagebox/
├── audiobooks/          # Audiobookshelf library
├── podcasts/           # Audiobookshelf podcasts
└── music/               # Navidrome music library
```

### Volume Mounts

- **Audiobookshelf:**
  - `/audiobooks` → `hetzner-media:/audiobooks` (read-only)
  - `/podcasts` → `hetzner-media:/podcasts` (read-only)

- **Navidrome:**
  - `/music` → `hetzner-media:/music` (read-only)

---

## 🚀 Deployment

### Prerequisites

1. **Storage Box Mounted:**
   - Ensure the Storage Box is mounted at `/mnt/storagebox`
   - Verify the `hetzner-media` Docker volume exists:
     ```bash
     docker volume inspect homelab_hetzner-media
     ```

2. **Tailscale Auth Key:**
   - Ensure `TAILSCALE_AUTHKEY` is set in `.env` or `ansible/vault.yml`

3. **Storage Box Structure:**
   - Create directories on the Storage Box:
     ```bash
     ssh rodkode@your-server-ip
     mkdir -p /mnt/storagebox/{audiobooks,podcasts,music}
     ```

### Deploy via Ansible

```bash
make ansible-deploy-media
```

This will:
1. Sync configuration files to the server
2. Deploy the Docker Compose stack
3. Start Tailscale services first
4. Start media services
5. Enable systemd service for auto-start

### Manual Deployment

```bash
cd /opt/homelab
docker compose -f docker-compose.media.yml up -d
```

---

## ⚙️ Configuration

### Audiobookshelf

1. **Access the Web UI:**
   - URL: `https://gandalf.kooka-lake.ts.net`
   - First-time setup will prompt for admin credentials

2. **Configure Libraries:**
   - Go to **Settings → Libraries**
   - Add library:
     - **Name:** `Audiobooks`
     - **Path:** `/audiobooks`
     - **Type:** `Audiobooks`
   - Add library:
     - **Name:** `Podcasts`
     - **Path:** `/podcasts`
     - **Type:** `Podcasts`

3. **Configure Metadata:**
   - Go to **Settings → Metadata**
   - Enable providers:
     - ✅ **OpenLibrary**
     - ✅ **Audible**
     - ✅ **iTunes Podcasts**

### Navidrome

1. **Access the Web UI:**
   - URL: `https://bard.kooka-lake.ts.net`
   - Default credentials:
     - **Username:** `admin`
     - **Password:** `admin` (change on first login)

2. **Configure Music Library:**
   - Go to **Settings → Music Folders**
   - Add folder: `/music`
   - Click **Scan Now** to index your music

3. **Configure Transcoding:**
   - Go to **Settings → Transcoding**
   - Enable transcoding if needed
   - Set cache size: `100MB` (already configured)

---

## 🔗 Integration with Arr Stack

### LazyLibrarian (Books)

LazyLibrarian is already part of the Arr stack (`docker-compose.arr-stack.yml`) and can be configured to sync with Audiobookshelf:

1. **Access LazyLibrarian:**
   - URL: `https://anduin.kooka-lake.ts.net:5299`
   - Configure download paths to match Storage Box structure

2. **Configure Audiobookshelf Integration:**
   - In LazyLibrarian, set download path to `/media/audiobooks`
   - Audiobookshelf will automatically detect new files

### Lidarr (Music)

Lidarr is already part of the Arr stack and can be configured to sync with Navidrome:

1. **Access Lidarr:**
   - URL: `https://anduin.kooka-lake.ts.net:8686`
   - Configure root folder to `/media/music`

2. **Configure Navidrome Integration:**
   - In Lidarr, set root folder to `/media/music`
   - Navidrome will automatically scan for new music (every hour)

---

## 🔧 Systemd Auto-Start

The media stack is configured to auto-start on server boot via systemd:

```bash
# Enable service
sudo systemctl enable media-stack.service

# Start service
sudo systemctl start media-stack.service

# Check status
sudo systemctl status media-stack.service
```

The service file is automatically deployed by Ansible to `/etc/systemd/system/media-stack.service`.

---

## 📊 Health Checks

Both services include health checks:

- **Audiobookshelf:**
  - Healthcheck: `http://localhost:13378/api/status`
  - Interval: 30s
  - Timeout: 10s
  - Retries: 3

- **Navidrome:**
  - Healthcheck: `http://localhost:4533/ping`
  - Interval: 30s
  - Timeout: 10s
  - Retries: 3

Check service health:

```bash
docker ps --filter "name=audiobookshelf\|navidrome"
```

---

## 🔐 Security

### Tailscale Access

Both services are only accessible via Tailscale:
- **Audiobookshelf:** `gandalf.kooka-lake.ts.net`
- **Navidrome:** `bard.kooka-lake.ts.net`

### Read-Only Media Access

Media volumes are mounted as read-only to prevent accidental modifications:
- `hetzner-media:/audiobooks:ro`
- `hetzner-media:/podcasts:ro`
- `hetzner-media:/music:ro`

### Network Isolation

Each service uses `network_mode: service:<tailscale-container>` for:
- Secure access via Tailscale
- Automatic HTTPS via Tailscale certificates
- Network isolation from other services

---

## 🐛 Troubleshooting

### Services Not Starting

1. **Check Tailscale Status:**
   ```bash
   docker logs audiobookshelf-ts
   docker logs navidrome-ts
   ```

2. **Verify Storage Box Mount:**
   ```bash
   mount | grep storagebox
   docker volume inspect homelab_hetzner-media
   ```

3. **Check Service Logs:**
   ```bash
   docker logs audiobookshelf
   docker logs navidrome
   ```

### Media Not Appearing

1. **Verify Storage Box Structure:**
   ```bash
   ls -la /mnt/storagebox/{audiobooks,podcasts,music}
   ```

2. **Check Permissions:**
   ```bash
   ls -la /mnt/storagebox
   # Should be owned by deploy:deploy (1000:1000)
   ```

3. **Trigger Manual Scan:**
   - **Audiobookshelf:** Settings → Libraries → Scan Now
   - **Navidrome:** Settings → Music Folders → Scan Now

### Tailscale Connection Issues

1. **Check Tailscale Status:**
   ```bash
   docker exec audiobookshelf-ts tailscale status
   docker exec navidrome-ts tailscale status
   ```

2. **Verify Auth Key:**
   - Ensure `TAILSCALE_AUTHKEY` is set in `.env` or `ansible/vault.yml`

3. **Check Tailscale Console:**
   - Visit https://login.tailscale.com/admin/machines
   - Verify `gandalf` and `bard` machines are registered

---

## 📝 Summary

- **Audiobookshelf:** `https://gandalf.kooka-lake.ts.net` (port 13378)
- **Navidrome:** `https://bard.kooka-lake.ts.net` (port 4533)
- **Storage:** Hetzner Storage Box (`u526046.your-storagebox.de`)
- **Deployment:** `make ansible-deploy-media`
- **Auto-Start:** systemd service enabled
- **Integration:** LazyLibrarian (books) and Lidarr (music) sync with Arr stack

Both services are ready to use! 🎉
