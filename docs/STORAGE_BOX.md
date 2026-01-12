# Hetzner Storage Box Complete Guide

Complete guide for setting up, managing, and troubleshooting Hetzner Storage Boxes for your homelab.

---

## 📋 Overview

Your homelab uses Hetzner Storage Boxes for media storage, providing:
- **5TB Storage** for media (movies, TV shows, music, audiobooks, podcasts)
- **1TB Storage** for Immich photos (separate Storage Box)
- **Off-site backup** storage
- **CIFS/SMB, WebDAV, or SSHFS** mount options
- **Read-only access** for media services (security)

**Current Storage Boxes:**
- **Main Media Storage Box:** `u529830.your-storagebox.de` (5TB)
- **Immich Storage Box:** `u527847.your-storagebox.de` (1TB)

---

## 🚀 Initial Setup

### Prerequisites

1. **Server Requirements:**
   - ✅ Ubuntu 24.04 (Noble)
   - ✅ CIFS utilities installed (`cifs-utils`, `davfs2`, `sshfs`, `fuse3`)
   - ✅ SSH access as root

2. **Storage Box:**
   - ✅ Hetzner Storage Box activated
   - ✅ Password (from 1Password or Hetzner console)

### Step 1: Choose Mount Method

#### Option 1: WebDAV (Recommended)

WebDAV is the recommended method for mounting the Storage Box.

**Setup:**
```bash
# Install davfs2
sudo apt-get update
sudo apt-get install -y davfs2

# Create mount point
sudo mkdir -p /mnt/storagebox
sudo chown root:root /mnt/storagebox
sudo chmod 755 /mnt/storagebox

# Configure credentials
sudo nano /etc/davfs2/secrets
```

Add the following line:
```
https://u529830.your-storagebox.de u529830 your_password
```

Set proper permissions:
```bash
sudo chmod 600 /etc/davfs2/secrets
```

**Add to /etc/fstab:**
```
https://u529830.your-storagebox.de /mnt/storagebox davfs uid=1000,gid=1000,file_mode=0770,dir_mode=0770,noexec,nosuid,nodev,_netdev 0 0
```

**Mount:**
```bash
sudo mount /mnt/storagebox
```

#### Option 2: SSHFS

SSHFS is an alternative method using SSH.

**Setup:**
```bash
# Install sshfs
sudo apt-get update
sudo apt-get install -y sshfs

# Create mount point
sudo mkdir -p /mnt/storagebox
sudo chown 1000:1000 /mnt/storagebox

# Setup SSH key (recommended)
sudo ssh-keygen -t ed25519 -f /root/.ssh/storagebox -N ""
sudo ssh-copy-id -i /root/.ssh/storagebox -p 23 u529830@u529830.your-storagebox.de
```

**Add to /etc/fstab:**
```
u529830@u529830.your-storagebox.de:/ /mnt/storagebox fuse.sshfs _netdev,user,idmap=user,transform_symlinks,IdentityFile=/root/.ssh/storagebox,allow_other,default_permissions,uid=1000,gid=1000,port=23,StrictHostKeyChecking=no 0 0
```

#### Option 3: CIFS/SMB

CIFS/SMB can be used but is generally slower than WebDAV or SSHFS.

**Setup:**
```bash
# Install cifs-utils
sudo apt-get update
sudo apt-get install -y cifs-utils

# Create credentials file
sudo nano /root/.smbcredentials
```

Add:
```
username=u529830
password=your_password
domain=u529830
```

Set permissions:
```bash
sudo chmod 600 /root/.smbcredentials
```

**Add to /etc/fstab:**
```
//u529830.your-storagebox.de/backup /mnt/storagebox cifs credentials=/root/.smbcredentials,uid=1000,gid=1000,file_mode=0777,dir_mode=0777,vers=3.0,sec=ntlmv2,_netdev 0 0
```

### Step 2: Create Directory Structure

```bash
# Create all directories
sudo mkdir -p /mnt/storagebox/{audiobooks,backups,books,downloads,home-videos,media,movies,music,photos,podcasts,tv-shows}

# Set permissions
sudo chown -R 1000:1000 /mnt/storagebox/*
sudo chmod -R 755 /mnt/storagebox/*
```

### Step 3: Configure Auto-Mount on Boot

Create a systemd service:

```bash
sudo nano /etc/systemd/system/mnt-storagebox.mount
```

Add:
```ini
[Unit]
Description=Mount Hetzner Storage Box
After=network-online.target
Wants=network-online.target

[Mount]
What=https://u529830.your-storagebox.de
Where=/mnt/storagebox
Type=davfs
Options=uid=1000,gid=1000,file_mode=0770,dir_mode=0770,noexec,nosuid,nodev,_netdev

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable mnt-storagebox.mount
sudo systemctl start mnt-storagebox.mount
```

---

## 📁 Folder Structure

### Complete Directory Layout

```
/mnt/storagebox/
├── audiobooks/          # LazyLibrarian → Audiobookshelf
├── backups/             # System backups
├── books/               # LazyLibrarian ebooks
├── downloads/           # qBittorrent staging area (Arr services import from here)
├── home-videos/         # Personal videos
├── media/               # General media storage
├── movies/              # Radarr → Jellyfin
├── music/               # Lidarr → Navidrome
├── photos/              # Photo storage
├── podcasts/            # LazyLibrarian → Audiobookshelf
└── tv-shows/            # Sonarr → Jellyfin
```

### Directory Usage

| Directory | Source Service | Destination Service | Purpose |
|-----------|---------------|---------------------|---------|
| `/movies/` | Radarr | Jellyfin | Final organized movie library |
| `/tv-shows/` | Sonarr | Jellyfin | Final organized TV show library |
| `/music/` | Lidarr | Navidrome | Final organized music library |
| `/audiobooks/` | LazyLibrarian | Audiobookshelf | Final organized audiobook library |
| `/podcasts/` | LazyLibrarian | Audiobookshelf | Final organized podcast library |
| `/books/` | LazyLibrarian | (Future) | Ebook library |
| `/downloads/` | qBittorrent | Arr services | Staging area for completed downloads |

---

## 🔐 SSH Key Setup

### Generate SSH Key

```bash
# Generate RSA key pair
sudo ssh-keygen -t rsa -b 4096 -f /root/.ssh/storagebox -N ""

# View public key
sudo cat /root/.ssh/storagebox.pub
```

### Add Public Key to Storage Box

1. **Copy the public key** (starts with `ssh-rsa ...`)
2. **Go to Hetzner Console:**
   - Navigate to: https://console.hetzner.cloud/
   - Go to **Storage** → **Storage Boxes**
   - Select your Storage Box
   - Go to **SSH Keys** → **Add Key**
   - Paste the entire public key (one line)

### Test SSH Connection

```bash
# Test SSH connection
ssh -i /root/.ssh/storagebox -p 23 u529830@u529830.your-storagebox.de "echo 'SSH connection successful'"
```

---

## 🔄 Migration to New Storage Box

### When to Migrate

- Storage Box capacity needs to be increased
- Storage Box needs to be recreated
- Moving to a different Storage Box

### Migration Steps

1. **Create New Storage Box:**
   - Go to Hetzner Console
   - Create new Storage Box with desired capacity
   - Note the new hostname (e.g., `u529830.your-storagebox.de`)

2. **Generate SSH Key** (if not already done):
   ```bash
   sudo ssh-keygen -t rsa -b 4096 -f /root/.ssh/storagebox -N ""
   ```

3. **Add SSH Key to New Storage Box:**
   - Copy public key: `sudo cat /root/.ssh/storagebox.pub`
   - Add to new Storage Box in Hetzner Console

4. **Update Server Configuration:**
   ```bash
   # Update fstab
   sudo sed -i 's/u526046/u529830/g' /etc/fstab
   
   # Update davfs2 secrets
   sudo sed -i 's/u526046/u529830/g' /etc/davfs2/secrets
   
   # Update systemd mount unit
   sudo sed -i 's/u526046/u529830/g' /etc/systemd/system/mnt-storagebox.mount
   ```

5. **Unmount Old Storage Box:**
   ```bash
   sudo umount /mnt/storagebox
   ```

6. **Mount New Storage Box:**
   ```bash
   sudo mount /mnt/storagebox
   ```

7. **Recreate Directory Structure:**
   ```bash
   sudo mkdir -p /mnt/storagebox/{audiobooks,backups,books,downloads,home-videos,media,movies,music,photos,podcasts,tv-shows}
   sudo chown -R 1000:1000 /mnt/storagebox/*
   sudo chmod -R 755 /mnt/storagebox/*
   ```

8. **Update Local Configuration:**
   - Update `.env` file with new Storage Box details
   - Update `ansible/vault.yml` with new Storage Box details

---

## 📊 Capacity Verification

### Check Storage Box Capacity

**Hetzner Console:**
1. Go to: https://console.hetzner.com/
2. Navigate to **Storage** → **Storage Boxes**
3. Check the capacity of your Storage Box

**On Server:**
```bash
# Check mount status
df -h /mnt/storagebox

# Note: davfs2 may show cached/incorrect capacity
# The actual capacity is what's shown in Hetzner Console
```

**Important:** The `df -h` command may show incorrect capacity due to davfs2 caching. The actual capacity is what's shown in Hetzner Console. The Storage Box will accept files up to the actual capacity regardless of what `df -h` displays.

### Current Storage Boxes

| Storage Box | Capacity | Purpose | Status |
|-------------|----------|---------|--------|
| `u529830` | 5TB | Main media storage | ✅ Active |
| `u527847` | 1TB | Immich photos | ✅ Active |

---

## 🔧 Troubleshooting

### Mount Failed

**Problem:** `mount error(13): Permission denied`

**Solution:**
```bash
# Check credentials
cat /etc/davfs2/secrets  # or /root/.smbcredentials

# Test mount manually
sudo mount -t davfs https://u529830.your-storagebox.de /mnt/storagebox
```

### Cannot Access Files

**Problem:** Permission denied in Docker containers

**Solution:**
```bash
# Check permissions
ls -ld /mnt/storagebox
ls -lah /mnt/storagebox/music

# Fix permissions
sudo chmod -R 770 /mnt/storagebox/*
sudo chown -R 1000:1000 /mnt/storagebox/*
```

### Mount at Boot Fails

**Problem:** Storage Box not mounted after reboot

**Solution:**
```bash
# Check fstab entry
grep storagebox /etc/fstab

# Ensure _netdev option is set
# Edit /etc/fstab if needed

# Test mount
sudo mount -a
```

### Connection Timeout

**Problem:** `mount error(110): Connection timed out`

**Solution:**
```bash
# Check network connectivity
ping u529830.your-storagebox.de

# Check if port 445 is accessible (for CIFS)
nc -zv u529830.your-storagebox.de 445

# Try with different options
sudo mount -t cifs //u529830.your-storagebox.de/backup /mnt/storagebox \
  -o credentials=/root/.smbcredentials,vers=3.0
```

### APT Package Manager TLS Handshake Errors

**Problem:** `apt-get update` fails with TLS handshake errors

**Solution:**
```bash
# Backup sources file
sudo cp /etc/apt/sources.list.d/ubuntu.sources /etc/apt/sources.list.d/ubuntu.sources.backup

# Update to use HTTP mirrors
sudo sed -i 's|https://mirror.hetzner.com/ubuntu/packages|http://archive.ubuntu.com/ubuntu|g' /etc/apt/sources.list.d/ubuntu.sources
sudo sed -i 's|https://mirror.hetzner.com/ubuntu/security|http://security.ubuntu.com/ubuntu|g' /etc/apt/sources.list.d/ubuntu.sources

# Update package lists
sudo apt-get update
```

### Capacity Shows Incorrectly

**Problem:** `df -h` shows 1.3TB instead of 5TB

**Solution:**
- This is a known davfs2 limitation
- The actual capacity is what's shown in Hetzner Console
- The Storage Box will accept files up to the actual capacity
- No action needed - this is a display issue, not a real problem

---

## 🔄 Maintenance

### Remount Storage Box

```bash
# Unmount
sudo umount /mnt/storagebox

# Remount
sudo mount -a

# Or
sudo mount /mnt/storagebox
```

### Check Disk Usage

```bash
# On Storage Box
du -sh /mnt/storagebox/*

# Via SFTP
sftp -P 23 u529830@u529830.your-storagebox.de
df -h
```

### Update Password

```bash
# Update in 1Password (if using)
op item edit STORAGE_BOX_PASSWORD --vault homelab-env

# Update credentials file on server
sudo nano /etc/davfs2/secrets  # or /root/.smbcredentials
# Update password
# Save and exit

# Remount
sudo umount /mnt/storagebox
sudo mount /mnt/storagebox
```

---

## 🐳 Docker Integration

### Docker Volume Configuration

The `hetzner-media` Docker volume maps to `/mnt/storagebox`:

```yaml
volumes:
  hetzner-media:
    driver: local
    driver_opts:
      type: bind
      o: bind
      device: /mnt/storagebox
```

**Services using Storage Box:**
- `navidrome` → `/music` (read-only)
- `audiobookshelf` → `/audiobooks`, `/podcasts` (read-only)
- `jellyfin` → `/movies`, `/tv-shows` (read-only)
- `qbittorrent` → `/downloads` (read-write)
- `radarr`, `sonarr`, `lidarr`, `lazylibrarian` → Various directories (read-write)

### Verify Docker Access

```bash
# Check volume
docker volume inspect homelab_hetzner-media

# Test Docker can access
docker run --rm -v /mnt/storagebox/music:/music:ro alpine ls -lah /music
```

---

## 📚 Additional Resources

- **Hetzner Docs**: https://docs.hetzner.com/robot/storage-box/
- **CIFS Mount**: https://wiki.ubuntu.com/MountWindowsSharesPermanently
- **WebDAV Mount**: https://wiki.ubuntu.com/MountWebDav

---

## ✅ Checklist

Before deploying services:
- [ ] Storage Box password in 1Password or `.env`
- [ ] Mount method chosen (WebDAV recommended)
- [ ] Mount point created and configured
- [ ] Directory structure created
- [ ] Permissions verified (`755` for dirs, `1000:1000` owner)
- [ ] Auto-mount on boot configured
- [ ] Docker volume working correctly
- [ ] Services can access Storage Box

---

**Questions? Check the troubleshooting section or verify mount status with `df -h /mnt/storagebox`!** 🚀
