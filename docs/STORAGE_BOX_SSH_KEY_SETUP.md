# Storage Box SSH Key Setup

This guide explains how to set up SSH key authentication for your new Hetzner Storage Box.

---

## 🔑 SSH Key Generated

An SSH key pair has been generated on your server for the new Storage Box.

**Key Location:**
- **Private Key:** `/root/.ssh/storagebox`
- **Public Key:** `/root/.ssh/storagebox.pub`

**Key Type:** RSA 4096-bit

---

## 📋 Step 1: Copy the Public Key

The public key has been generated on your server. You need to copy it to add it to your new Storage Box.

### Option A: View Public Key via SSH

```bash
ssh rodkode@95.216.176.147 "sudo cat /root/.ssh/storagebox.pub"
```

### Option B: Copy Public Key to Local Machine

```bash
# Copy public key to your local machine
scp rodkode@95.216.176.147:/root/.ssh/storagebox.pub ~/storagebox.pub

# View the public key
cat ~/storagebox.pub
```

---

## 📋 Step 2: Add Public Key to New Storage Box

When creating your new Storage Box in the Hetzner Console:

1. **Go to Hetzner Console:**
   - Navigate to: https://console.hetzner.cloud/
   - Go to **Storage** → **Storage Boxes**

2. **Create New Storage Box:**
   - Click **"Create Storage Box"**
   - Set capacity to **5TB**
   - Choose location (same as before if possible)

3. **Add SSH Key:**
   - During creation, look for **"SSH Keys"** or **"Public Keys"** section
   - Paste the public key content (starts with `ssh-rsa ...`)
   - Or after creation, go to Storage Box settings → **SSH Keys** → **Add Key**
   - Paste the entire public key (one line)

4. **Note the New Storage Box Details:**
   - **Hostname:** `uXXXXXX.your-storagebox.de` (will be different from u526046)
   - **Username:** `uXXXXXX` (same as hostname prefix)
   - **SSH Port:** `23`

---

## 📋 Step 3: Test SSH Connection

After adding the key to the new Storage Box, test the connection:

```bash
# Test SSH connection (replace uXXXXXX with your new Storage Box username)
ssh -i /root/.ssh/storagebox -p 23 uXXXXXX@uXXXXXX.your-storagebox.de "echo 'SSH connection successful'"
```

Or from your local machine:

```bash
ssh rodkode@95.216.176.147 "sudo ssh -i /root/.ssh/storagebox -p 23 uXXXXXX@uXXXXXX.your-storagebox.de 'echo SSH connection successful'"
```

---

## 📋 Step 4: Update Server Configuration

After confirming the new Storage Box hostname, update the server configuration:

### Update fstab (if using CIFS/SMB)

```bash
# Edit fstab
sudo nano /etc/fstab

# Update the line (replace u526046 with new Storage Box username)
# OLD:
//u526046.your-storagebox.de/backup /mnt/storagebox cifs ...

# NEW:
//uXXXXXX.your-storagebox.de/backup /mnt/storagebox cifs credentials=/root/.smbcredentials,uid=1000,gid=1000,file_mode=0770,dir_mode=0770,_netdev 0 0
```

### Update WebDAV mount (if using WebDAV/davfs2)

```bash
# Edit /etc/davfs2/secrets
sudo nano /etc/davfs2/secrets

# Update the line (replace u526046 with new Storage Box username)
# OLD:
https://u526046.your-storagebox.de u526046 password

# NEW:
https://uXXXXXX.your-storagebox.de uXXXXXX new_password
```

### Update systemd mount unit (if using systemd)

```bash
# Edit systemd mount unit
sudo nano /etc/systemd/system/mnt-storagebox.mount

# Update What= line
# OLD:
What=https://u526046.your-storagebox.de

# NEW:
What=https://uXXXXXX.your-storagebox.de
```

---

## 📋 Step 5: Update Credentials File

Update the SMB credentials file:

```bash
# Edit credentials file
sudo nano /root/.smbcredentials

# Update username (replace u526046 with new Storage Box username)
username=uXXXXXX
password=NEW_STORAGE_BOX_PASSWORD
```

**Set correct permissions:**
```bash
sudo chmod 600 /root/.smbcredentials
```

---

## 📋 Step 6: Remount Storage Box

After updating configuration:

```bash
# Unmount old Storage Box
sudo umount /mnt/storagebox

# Remount with new Storage Box
sudo mount /mnt/storagebox

# Verify mount
df -h /mnt/storagebox
mount | grep storagebox
```

---

## 🔐 Security Notes

1. **Private Key Security:**
   - The private key (`/root/.ssh/storagebox`) should **never** be shared
   - Keep it secure on the server
   - Permissions should be `600` (read/write for root only)

2. **Public Key:**
   - The public key (`.pub` file) is safe to share
   - It's designed to be added to the Storage Box
   - Can be viewed/copied without security concerns

3. **Key Rotation:**
   - If you need to regenerate keys, delete the old public key from Storage Box first
   - Generate new key pair
   - Add new public key to Storage Box

---

## ✅ Verification Checklist

After setup, verify:

- [ ] SSH key generated on server (`/root/.ssh/storagebox`)
- [ ] Public key copied and ready to add
- [ ] New Storage Box created with 5TB capacity
- [ ] Public key added to new Storage Box
- [ ] SSH connection tested successfully
- [ ] Server configuration updated (fstab, credentials, systemd)
- [ ] Storage Box remounted successfully
- [ ] Folder structure recreated (see [Storage Box Folder Structure](./STORAGE_BOX_FOLDER_STRUCTURE.md))
- [ ] Docker volumes working correctly
- [ ] Services can access Storage Box

---

## 🔗 Related Documentation

- [Storage Box Setup Guide](./STORAGE_BOX_SETUP.md)
- [Storage Box Folder Structure](./STORAGE_BOX_FOLDER_STRUCTURE.md)
- [Arr Stack Media Integration](./ARR_STACK_MEDIA_INTEGRATION.md)

---

## 🆘 Troubleshooting

### SSH Connection Fails

1. **Check key format:**
   ```bash
   sudo cat /root/.ssh/storagebox.pub
   ```
   Should start with `ssh-rsa` and be a single line

2. **Verify key added to Storage Box:**
   - Check Hetzner Console → Storage Box → SSH Keys
   - Ensure key is added correctly (no extra spaces/line breaks)

3. **Test with verbose output:**
   ```bash
   ssh -v -i /root/.ssh/storagebox -p 23 uXXXXXX@uXXXXXX.your-storagebox.de
   ```

### Permission Denied

- Ensure private key has correct permissions: `chmod 600 /root/.ssh/storagebox`
- Verify public key is correctly added to Storage Box
- Check Storage Box username matches the key

### Mount Fails After Key Setup

- Verify credentials file has correct username/password
- Check fstab entry uses correct hostname
- Ensure Storage Box is accessible: `ping uXXXXXX.your-storagebox.de`
