# Storage Box Migration Notes

**Date:** 2026-01-11  
**Old Storage Box:** `u526046.your-storagebox.de` (1.3TB)  
**New Storage Box:** `u529830.your-storagebox.de` (5TB)  
**Password:** Same as before

---

## ✅ Configuration Files Updated

### 1. Systemd Mount Unit
- **File:** `systemd/mnt-storagebox.mount`
- **Updated:** `u526046` → `u529830`

### 2. Server Configuration (Updated on Server)
- **fstab:** `/etc/fstab` - Updated Storage Box hostname
- **davfs2 secrets:** `/etc/davfs2/secrets` - Updated username and hostname
- **systemd:** Reloaded and restarted automount service

---

## ⚠️ Files That Need Manual Update

### 1. `.env` File (Local)
Add or update these variables:
```bash
STORAGE_BOX_HOST=u529830.your-storagebox.de
STORAGE_BOX_USER=u529830
STORAGE_BOX_PASSWORD=<same_password>
```

### 2. `ansible/vault.yml` (Encrypted)
Update the vault with new Storage Box details:
```bash
# Edit vault.yml
ansible-vault edit ansible/vault.yml

# Update these variables:
vault_storage_box_host: u529830.your-storagebox.de
vault_storage_box_user: u529830
vault_storage_box_password: <same_password>
```

---

## ✅ Server Setup Completed

1. ✅ Unmounted old Storage Box
2. ✅ Updated `/etc/fstab` with new hostname (`u529830`)
3. ✅ Updated `/etc/davfs2/secrets` with new username/hostname (`u529830`)
4. ✅ Mounted new Storage Box successfully
5. ✅ Created directory structure:
   - `audiobooks/`
   - `backups/`
   - `books/`
   - `downloads/`
   - `home-videos/`
   - `media/`
   - `movies/`
   - `music/`
   - `photos/`
   - `podcasts/`
   - `tv-shows/`
6. ✅ Set permissions (deploy:deploy, 755)
7. ✅ Verified write access
8. ✅ Docker volume (`homelab_hetzner-media`) correctly mapped to `/mnt/storagebox`

**✅ Verified:** The Storage Box `u529830` shows **5TB** in Hetzner Console (confirmed).

**Note:** The `df -h` command may show 1.3TB instead of 5TB - this is a known davfs2 limitation when mounting WebDAV shares. The actual capacity is 5TB as confirmed in Hetzner Console, and the Storage Box will accept files up to 5TB regardless of what `df -h` displays.

**Note:** The Immich Storage Box (`u527847`) showing 1.3TB is correct (1TB + filesystem overhead).

---

## 📋 Verification Steps

### Check Mount Status
```bash
df -h /mnt/storagebox
mount | grep storagebox
```

### Check Directory Structure
```bash
ls -la /mnt/storagebox/
```

### Test Write Access
```bash
touch /mnt/storagebox/test.txt && rm /mnt/storagebox/test.txt
```

### Check Docker Volume
```bash
docker volume inspect homelab_hetzner-media
```

---

## 🔄 Next Steps

1. **Update Local Configuration:**
   - Update `.env` file with new Storage Box details
   - Update `ansible/vault.yml` with new Storage Box details

2. **Verify Services:**
   - Check that Docker containers can access the Storage Box
   - Verify Jellyfin, Arr-stack services can read/write

3. **Data Transfer Status:**
   - ⚠️ **The old Storage Box (`u526046`) was deleted** - all data on it is gone
   - ✅ **The new Storage Box (`u529830`) is empty** - ready for new data
   - 📥 **Movies need to be re-rsync'd** if you want them on the new Storage Box
   - The movies that were previously rsync'd ("Hidden Figures (2016)") are not on the new Storage Box

---

## 📝 SSH Key Setup

The SSH key for the new Storage Box was already generated:
- **Private Key:** `/root/.ssh/storagebox`
- **Public Key:** `/root/.ssh/storagebox.pub`
- **Status:** ✅ Added to new Storage Box during creation

---

## 🔗 Related Documentation

- [Storage Box Setup Guide](./STORAGE_BOX_SETUP.md)
- [Storage Box Folder Structure](./STORAGE_BOX_FOLDER_STRUCTURE.md)
- [Storage Box SSH Key Setup](./STORAGE_BOX_SSH_KEY_SETUP.md)
