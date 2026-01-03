# 🗄️ Hetzner Storage Box Setup Guide

Complete guide for setting up your Hetzner Storage Box for media services.

---

## 📋 Overview

Your homelab uses a Hetzner Storage Box for media storage, providing:

- **1TB+ Storage** for music, audiobooks, podcasts
- **Off-site backup** storage
- **CIFS/SMB mount** for Docker containers
- **Read-only access** for media services (security)

**Storage Box Details:**

- Host: `u525677.your-storagebox.de`
- Username: `u525677`
- SSH Port: 23
- Protocol: CIFS/SMB

---

## ✅ Prerequisites

1. **Server Requirements:**
   - ✅ Ubuntu 24.04 (Noble)
   - ✅ CIFS utilities installed
   - ✅ SSH access as root

2. **Storage Box:**
   - ✅ Hetzner Storage Box activated
   - ✅ Password (from 1Password or Hetzner console)

3. **Local Requirements:**
   - SSH key configured for server access
   - 1Password CLI (optional, for automated setup)

---

## 🔍 Step 1: Check Current Status

Before setup, check what's already configured:

```bash
cd /Users/rodneyhammad/Private/Gandalf-gate-docke/homelab
./scripts/check-storage-box.sh
```

**Expected Output:**

```
📊 Summary:
  - Server: 95.216.176.147 ✅
  - CIFS Utils: ✅
  - Mount Point: ❌  (will be created)
  - Mounted: ❌  (will be mounted)
  - Fstab Entry: ❌  (will be added)
  - Credentials: ❌  (will be created)
```

---

## 🚀 Step 2: Run Setup Script

### Option A: With 1Password (Recommended)

```bash
# Sign in to 1Password CLI
eval $(op signin)

# Ensure Storage Box password is in 1Password
op item list --vault homelab-env | grep STORAGE_BOX_PASSWORD

# If not found, add it:
op item create --vault homelab-env --category=password \
  --title="STORAGE_BOX_PASSWORD" \
  password="YOUR_STORAGE_BOX_PASSWORD"

# Run setup (will get password from 1Password automatically)
./scripts/setup-storage-box-server.sh
```

### Option B: Manual Password Entry

```bash
# Run setup and enter password when prompted
./scripts/setup-storage-box-server.sh
```

### Option C: With Environment Variable

```bash
# Set password in environment
export STORAGE_BOX_PASSWORD="your_password_here"

# Run setup
./scripts/setup-storage-box-server.sh
```

---

## 📁 What Gets Created

The setup script creates this directory structure:

```
/mnt/storagebox/
├── music/         # For Navidrome (music streaming)
├── audiobooks/    # For Audiobookshelf (audiobooks)
├── podcasts/      # For Audiobookshelf (podcasts)
├── downloads/     # For download clients (optional)
├── media/         # For other media (movies, TV shows)
└── backups/       # For system backups
```

**Permissions:** `770` (rwxrwx---)
**Owner:** `1000:1000` (Docker user)

---

## 🔐 Security Configuration

### Credentials File

Created at: `/root/.smbcredentials`

```ini
username=u525677
password=YOUR_PASSWORD
```

**Permissions:** `600` (only root can read)

### Fstab Entry

Added to: `/etc/fstab`

```bash
//u525677.your-storagebox.de/backup /mnt/storagebox cifs credentials=/root/.smbcredentials,uid=1000,gid=1000,file_mode=0770,dir_mode=0770,_netdev 0 0
```

**Options:**

- `credentials` - Use credentials file
- `uid=1000,gid=1000` - Set owner to Docker user
- `file_mode=0770` - File permissions
- `dir_mode=0770` - Directory permissions
- `_netdev` - Wait for network before mounting

---

## 📤 Step 3: Upload Media Files

### Option A: Via SFTP

```bash
# Connect to Storage Box directly
sftp -P 23 u525677@u525677.your-storagebox.de

# Navigate and upload
cd music
put -r /path/to/your/music/*

cd ../audiobooks
put -r /path/to/your/audiobooks/*
```

### Option B: Via Server (Faster)

```bash
# Upload to server, then move to Storage Box
scp -r /path/to/music/* root@95.216.176.147:/tmp/

# SSH to server and move
ssh root@95.216.176.147
mv /tmp/music/* /mnt/storagebox/music/
```

### Option C: rsync (Best for Large Collections)

```bash
# Initial sync
rsync -avz --progress -e "ssh -p 23" \
  /path/to/music/ \
  u525677@u525677.your-storagebox.de:/home/music/

# Or via server mount
rsync -avz --progress \
  /path/to/music/ \
  root@95.216.176.147:/mnt/storagebox/music/
```

---

## 🧪 Step 4: Verify Setup

### Check Mount Status

```bash
# Run check script again
./scripts/check-storage-box.sh
```

**Should now show:**

```
📊 Summary:
  - Server: 95.216.176.147 ✅
  - CIFS Utils: ✅
  - Mount Point: ✅
  - Mounted: ✅
  - Fstab Entry: ✅
  - Credentials: ✅
```

### Verify Files on Server

```bash
# SSH to server
ssh root@95.216.176.147

# Check mount
df -h | grep storagebox

# List contents
ls -lah /mnt/storagebox/
ls -lah /mnt/storagebox/music/
ls -lah /mnt/storagebox/audiobooks/
```

### Test Docker Access

```bash
# On server, test Docker can access
docker run --rm -v /mnt/storagebox/music:/music:ro alpine ls -lah /music
```

---

## 🐳 Step 5: Update Docker Compose

The `docker-compose.yml` already includes the Storage Box volume:

```yaml
volumes:
  hetzner-media:
    driver: local
    driver_opts:
      type: cifs
      o: "username=u525677,password=${STORAGE_BOX_PASSWORD},uid=1000,gid=1000,file_mode=0770,dir_mode=0770"
      device: "//u525677.your-storagebox.de/backup"
```

**Services using Storage Box:**

- `navidrome` → `/music` (read-only)
- `audiobookshelf` → `/audiobooks`, `/podcasts` (read-only)

---

## 🎵 Step 6: Deploy Media Services

```bash
# Deploy Navidrome and Audiobookshelf
docker compose up -d navidrome audiobookshelf

# Check logs
docker logs navidrome
docker logs audiobookshelf

# Access services
open https://navidrome.rodneyops.com
open https://audiobooks.rodneyops.com
```

---

## 🔧 Troubleshooting

### Mount Failed

**Problem:** `mount error(13): Permission denied`

```bash
# Check credentials
cat /root/.smbcredentials

# Test mount manually
mount -t cifs //u525677.your-storagebox.de/backup /mnt/storagebox \
  -o credentials=/root/.smbcredentials,uid=1000,gid=1000
```

### Cannot Access Files

**Problem:** Permission denied in Docker containers

```bash
# Check permissions
ls -ld /mnt/storagebox
ls -lah /mnt/storagebox/music

# Fix permissions
chmod -R 770 /mnt/storagebox/*
chown -R 1000:1000 /mnt/storagebox/*
```

### Mount at Boot Fails

**Problem:** Storage Box not mounted after reboot

```bash
# Check fstab entry
grep storagebox /etc/fstab

# Ensure _netdev option is set
# Edit /etc/fstab if needed

# Test mount
mount -a
```

### Connection Timeout

**Problem:** `mount error(110): Connection timed out`

```bash
# Check network connectivity
ping u525677.your-storagebox.de

# Check if port 445 is accessible
nc -zv u525677.your-storagebox.de 445

# Try with different options
mount -t cifs //u525677.your-storagebox.de/backup /mnt/storagebox \
  -o credentials=/root/.smbcredentials,vers=3.0
```

---

## 🔄 Maintenance

### Remount Storage Box

```bash
# Unmount
umount /mnt/storagebox

# Remount
mount -a

# Or
mount /mnt/storagebox
```

### Check Disk Usage

```bash
# On Storage Box
du -sh /mnt/storagebox/*

# Via SFTP
sftp -P 23 u525677@u525677.your-storagebox.de
df -h
```

### Update Password

```bash
# Update in 1Password
op item edit STORAGE_BOX_PASSWORD --vault homelab-env

# Update credentials file on server
ssh root@95.216.176.147
nano /root/.smbcredentials
# Update password
# Save and exit

# Remount
umount /mnt/storagebox
mount /mnt/storagebox
```

---

## 📊 Storage Organization Best Practices

### Music (Navidrome)

```
/mnt/storagebox/music/
├── Artist Name/
│   ├── Album Name (Year)/
│   │   ├── 01 - Track Name.mp3
│   │   ├── 02 - Track Name.mp3
│   │   └── cover.jpg
│   └── Album Name 2/
│       └── ...
└── Various Artists/
    └── ...
```

### Audiobooks (Audiobookshelf)

```
/mnt/storagebox/audiobooks/
├── Author Name/
│   ├── Book Title/
│   │   ├── cover.jpg
│   │   ├── Chapter 01.mp3
│   │   ├── Chapter 02.mp3
│   │   └── metadata.json (optional)
│   └── Book Title 2/
│       └── ...
└── ...
```

### Podcasts (Audiobookshelf)

```
/mnt/storagebox/podcasts/
├── Podcast Name/
│   ├── cover.jpg
│   ├── 001 - Episode Title.mp3
│   ├── 002 - Episode Title.mp3
│   └── ...
└── ...
```

---

## 📚 Additional Resources

- **Hetzner Docs**: https://docs.hetzner.com/robot/storage-box/
- **CIFS Mount**: https://wiki.ubuntu.com/MountWindowsSharesPermanently
- **Navidrome**: https://www.navidrome.org/docs/installation/docker/
- **Audiobookshelf**: https://www.audiobookshelf.org/docs

---

## ✅ Checklist

Before deploying media services:

- [ ] Storage Box password in 1Password
- [ ] Setup script executed successfully
- [ ] Mount verified with `check-storage-box.sh`
- [ ] Media files uploaded
- [ ] Permissions verified (`770`, `1000:1000`)
- [ ] Docker can access mount
- [ ] Services deployed
- [ ] Web interfaces accessible

---

**Questions? Run `./scripts/check-storage-box.sh` to diagnose issues!** 🚀
