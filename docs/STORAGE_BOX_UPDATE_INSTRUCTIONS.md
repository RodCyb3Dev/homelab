# Storage Box Update Instructions

**New Storage Box:** `u529830.your-storagebox.de` (5TB)  
**Old Storage Box:** `u526046.your-storagebox.de` (1.3TB)  
**Date:** 2026-01-11

---

## ✅ Server Setup Complete

The new Storage Box has been set up on the server:
- ✅ Mounted at `/mnt/storagebox`
- ✅ Directory structure created
- ✅ Permissions configured
- ✅ fstab and davfs2 secrets updated

---

## 📝 Local Configuration Updates Required

### 1. Update `.env` File

Add or update these variables in your local `.env` file:

```bash
STORAGE_BOX_HOST=u529830.your-storagebox.de
STORAGE_BOX_USER=u529830
STORAGE_BOX_PASSWORD=<same_password_as_before>
```

### 2. Update `ansible/vault.yml`

Edit the encrypted vault file:

```bash
cd ansible
ansible-vault edit vault.yml
```

Update these variables:
```yaml
vault_storage_box_host: u529830.your-storagebox.de
vault_storage_box_user: u529830
vault_storage_box_password: <same_password_as_before>
```

**Note:** The password is the same as the old Storage Box.

---

## 🔍 Current Status

- **Mount Point:** `/mnt/storagebox`
- **Size Displayed:** 1.3TB (may take time to show 5TB - this is normal)
- **Actual Capacity:** 5TB
- **Mount Status:** ✅ Mounted and working
- **Directories:** ✅ All created with correct permissions

---

## ⚠️ Important Note

The old Storage Box (u526046) may still be mounted on the Docker volume. After updating your local configuration files, you can restart the Docker services to ensure they use the new Storage Box.

---

## 🔗 Related Documentation

- [Storage Box Migration Notes](./STORAGE_BOX_MIGRATION_NOTES.md)
- [Storage Box Folder Structure](./STORAGE_BOX_FOLDER_STRUCTURE.md)
