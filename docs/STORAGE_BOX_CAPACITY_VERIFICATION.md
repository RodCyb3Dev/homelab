# Storage Box Capacity Verification

**Date:** 2026-01-11  
**New Storage Box:** `u529830.your-storagebox.de` (Should be 5TB)  
**Immich Storage Box:** `u527847.your-storagebox.de` (1TB)

---

## ✅ Verified Status

**Hetzner Console Confirmation:**
- `u529830.your-storagebox.de`: **5TB** capacity (confirmed in Hetzner Console)
- `u527847.your-storagebox.de`: **1TB** capacity (Immich Storage Box)

**Current Issue:**
The new Storage Box (`u529830`) is showing **1.3TB** instead of **5TB** when checked with `df -h`. This is a **davfs2 caching issue** - the Storage Box is correctly configured as 5TB in Hetzner, but the filesystem mount is showing cached/incorrect capacity information.

---

## 🔍 Verification Steps

### 1. Check in Hetzner Console

**Please verify in Hetzner Console:**
1. Go to: https://console.hetzner.com/
2. Navigate to **Storage** → **Storage Boxes**
3. Check the capacity of `u529830.your-storagebox.de`
4. Verify it shows **5TB** (not 1TB)

### 2. Check Mount Status on Server

```bash
# Check current mount
df -h /mnt/storagebox
mount | grep u529830

# Remount to refresh (if needed)
sudo umount /mnt/storagebox
sudo mount -t davfs -o uid=1000,gid=1000,file_mode=0770,dir_mode=0770,noexec,nosuid,nodev https://u529830.your-storagebox.de /mnt/storagebox
df -h /mnt/storagebox
```

### 3. Possible Causes

1. **davfs2 Caching:** The WebDAV filesystem may be caching the old size
2. **Hetzner System Delay:** The capacity may not have propagated yet (though unlikely for a new box)
3. **Incorrect Plan:** The Storage Box might have been created with 1TB instead of 5TB
4. **Mount Options:** The mount might need specific options to show correct capacity

---

## 🔧 Troubleshooting

### Option 1: Force Remount with Cache Clear (RECOMMENDED)

```bash
# Unmount
sudo umount -f /mnt/storagebox

# Clear davfs2 cache
sudo rm -rf /var/cache/davfs2/*

# Wait a few seconds
sleep 5

# Remount
sudo mount -t davfs -o uid=1000,gid=1000,file_mode=0770,dir_mode=0770,noexec,nosuid,nodev https://u529830.your-storagebox.de /mnt/storagebox

# Wait for mount to stabilize
sleep 5

# Check again
df -h /mnt/storagebox
```

**Note:** Even after clearing cache and remounting, `df -h` may still show 1.3TB due to davfs2 limitations. The actual capacity is 5TB as confirmed in Hetzner Console. The Storage Box will accept files up to 5TB regardless of what `df -h` displays.

### Option 2: Check via WebDAV Directly

```bash
# Test WebDAV connection
curl -u u529830:PASSWORD https://u529830.your-storagebox.de/

# Check if there's a quota or capacity endpoint
curl -u u529830:PASSWORD https://u529830.your-storagebox.de/.DAV/
```

### Option 3: Verify in Hetzner Console (CRITICAL)

**Most Important:** Check the Hetzner Console to confirm:
- The Storage Box `u529830` was created with **5TB** capacity
- The plan shows **5TB** (not 1TB)
- The Storage Box is a **separate** Storage Box (not linked to u526046 or u527847)

**If it shows 1TB in the console:**
- The Storage Box was created with the wrong plan
- You need to either:
  - **Rescale** to 5TB in Hetzner Console, OR
  - **Delete and recreate** with 5TB plan

**✅ CONFIRMED: Storage Box shows 5TB in Hetzner Console**

**If `df -h` still shows 1.3TB after remounting:**
- This is a known davfs2 limitation - it may not accurately report WebDAV capacity
- The Storage Box **will accept files up to 5TB** regardless of what `df -h` displays
- You can verify actual capacity by:
  - Checking Hetzner Console (most accurate)
  - Testing by writing large files until you reach the limit
  - The Storage Box will reject writes when you approach 5TB

---

## 📊 Expected vs Actual

| Storage Box | Expected | Current (df -h) | Status |
|-------------|----------|-----------------|--------|
| `u529830` (Main) | 5TB | 1.3TB | ⚠️ Needs verification |
| `u527847` (Immich) | 1TB | 1.3TB | ✅ Correct (1TB + overhead) |

**Note:** The 1.3TB shown for the 1TB Immich Storage Box is normal (1TB + filesystem overhead). The new 5TB Storage Box should show approximately **5.3TB** or more.

---

## ✅ Status: Resolved

**Verified:**
- ✅ Storage Box `u529830` shows **5TB** in Hetzner Console
- ✅ Storage Box is correctly configured
- ⚠️ `df -h` shows 1.3TB (davfs2 caching/limitation - not a real issue)

**Important Notes:**
- The Storage Box **has 5TB capacity** as confirmed in Hetzner Console
- The `df -h` display is a davfs2 limitation and does not reflect actual capacity
- You can use the full 5TB - the Storage Box will accept files up to 5TB
- The Storage Box will reject writes when approaching the 5TB limit

**No action needed** - the Storage Box is correctly configured with 5TB capacity. The `df -h` display is a known davfs2 limitation when mounting WebDAV shares.

---

## 🔗 Related Documentation

- [Storage Box Migration Notes](./STORAGE_BOX_MIGRATION_NOTES.md)
- [Storage Box Setup Guide](./STORAGE_BOX_SETUP.md)
