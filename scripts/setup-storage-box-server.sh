#!/bin/bash
# Setup Hetzner Storage Box on the server with proper media directory structure

set -e

# Colors
# shellcheck disable=SC2034
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SERVER_IP="95.216.176.147"
STORAGE_BOX_HOST="u526046.your-storagebox.de"
STORAGE_BOX_USER="u526046"
MOUNT_POINT="/mnt/storagebox"

# Check for dry-run mode
DRY_RUN=false
if [[ "$1" == "--dry-run" ]] || [[ "$1" == "-n" ]]; then
    DRY_RUN=true
    echo -e "${YELLOW}🧪 DRY-RUN MODE - No changes will be made${NC}"
    echo ""
fi

# Export DRY_RUN for use in conditional commands (even if not used in this script)
export DRY_RUN

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🗄️  Hetzner Storage Box Setup${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo -e "${GREEN}Server: ${SERVER_IP}${NC}"
echo -e "${GREEN}Storage Box: ${STORAGE_BOX_HOST}${NC}"
echo -e "${GREEN}Mount Point: ${MOUNT_POINT}${NC}"
echo ""

# Check for SSH key
echo -e "${GREEN}📋 Step 1: Checking SSH key setup...${NC}"

ssh root@${SERVER_IP} bash << 'EOF'
# Check if SSH key exists
if [ ! -f /root/.ssh/storagebox ]; then
    echo "❌ SSH key not found. Generating..."
    ssh-keygen -t rsa -b 4096 -f /root/.ssh/storagebox -N '' -C 'storagebox-mount'
    echo "✅ SSH key generated"
    echo ""
    echo "📋 Public key (add this to Storage Box):"
    cat /root/.ssh/storagebox.pub
    echo ""
    echo "⚠️  Please add this key to Storage Box using:"
    echo "   cat /root/.ssh/storagebox.pub | ssh -p 23 u526046@u526046.your-storagebox.de install-ssh-key"
    exit 1
else
    echo "✅ SSH key exists"
fi
EOF

# Test SSH key authentication
echo ""
echo -e "${GREEN}📋 Step 2: Testing SSH key authentication...${NC}"

if ssh root@${SERVER_IP} "ssh -i /root/.ssh/storagebox -p 23 -o StrictHostKeyChecking=no -o ConnectTimeout=5 u526046@u526046.your-storagebox.de 'echo test' 2>&1 | grep -q 'test'"; then
    echo -e "${GREEN}✅ SSH key authentication works!${NC}"
else
    echo -e "${YELLOW}⚠️  SSH key authentication failed. Make sure the key is added to Storage Box.${NC}"
    echo -e "${YELLOW}   Continuing with setup anyway...${NC}"
fi

echo ""
echo -e "${GREEN}📋 Step 3: Installing sshfs...${NC}"

ssh root@${SERVER_IP} bash << 'EOF'
# Install sshfs if not already installed
if ! command -v sshfs &> /dev/null; then
    apt-get update -qq && apt-get install -y sshfs
    echo "✅ sshfs installed"
else
    echo "✅ sshfs already installed"
fi
EOF

echo ""
echo -e "${GREEN}📋 Step 4: Creating mount point...${NC}"

ssh root@${SERVER_IP} bash << 'EOF'
# Create mount point
mkdir -p /mnt/storagebox
chmod 755 /mnt/storagebox

echo "✅ Mount point created"
EOF

echo ""
echo -e "${GREEN}📋 Step 5: Adding to /etc/fstab...${NC}"

ssh root@${SERVER_IP} bash << 'EOF'
# Check if already in fstab
if grep -q "storagebox" /etc/fstab; then
    echo "⚠️  Entry already exists in fstab, removing old entry..."
    sed -i '/storagebox/d' /etc/fstab
fi

# Add SSHFS entry to fstab
echo "${STORAGE_BOX_USER}@${STORAGE_BOX_HOST}:/ ${MOUNT_POINT} fuse.sshfs _netdev,user,idmap=user,transform_symlinks,IdentityFile=/root/.ssh/storagebox,allow_other,default_permissions,uid=1000,gid=1000,port=23,StrictHostKeyChecking=no 0 0" >> /etc/fstab

echo "✅ Added to fstab"
EOF

echo ""
echo -e "${GREEN}📋 Step 6: Mounting Storage Box...${NC}"

ssh root@${SERVER_IP} bash << 'EOF'
# Unmount if already mounted
umount /mnt/storagebox 2>/dev/null || true

# Mount using SSHFS
sshfs ${STORAGE_BOX_USER}@${STORAGE_BOX_HOST}:/ ${MOUNT_POINT} -p 23 -o IdentityFile=/root/.ssh/storagebox,uid=1000,gid=1000,allow_other,StrictHostKeyChecking=no 2>&1

# Verify mount
if mountpoint -q /mnt/storagebox; then
    echo "✅ Storage Box mounted successfully"
    df -h | grep storagebox
else
    echo "❌ Mount failed - check SSH key authentication"
    exit 1
fi
EOF

echo ""
echo -e "${GREEN}📋 Step 5: Checking current contents...${NC}"

CURRENT_CONTENTS=$(ssh root@${SERVER_IP} "ls -lah ${MOUNT_POINT}/ 2>/dev/null")

echo "$CURRENT_CONTENTS"

echo ""
echo -e "${GREEN}📋 Step 6: Creating media directory structure...${NC}"

ssh root@${SERVER_IP} bash << 'EOF'
# Create directories for media services
mkdir -p ${MOUNT_POINT}/music
mkdir -p ${MOUNT_POINT}/audiobooks
mkdir -p ${MOUNT_POINT}/podcasts
mkdir -p ${MOUNT_POINT}/downloads
mkdir -p ${MOUNT_POINT}/media
mkdir -p ${MOUNT_POINT}/backups

# Set permissions
chmod -R 770 ${MOUNT_POINT}/music
chmod -R 770 ${MOUNT_POINT}/audiobooks
chmod -R 770 ${MOUNT_POINT}/podcasts
chmod -R 770 ${MOUNT_POINT}/downloads
chmod -R 770 ${MOUNT_POINT}/media
chmod -R 770 ${MOUNT_POINT}/backups

echo "✅ Directory structure created"
EOF

echo ""
echo -e "${GREEN}📋 Step 7: Verifying directory structure...${NC}"

ssh root@${SERVER_IP} bash << 'EOF'
echo ""
echo "=== Directory Tree ==="
ls -lah /mnt/storagebox/

echo ""
echo "=== Disk Usage ==="
du -sh /mnt/storagebox/* 2>/dev/null || echo "Empty directories"

echo ""
echo "=== Permissions Check ==="
ls -ld /mnt/storagebox/{music,audiobooks,podcasts,downloads,media,backups} 2>/dev/null
EOF

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ Storage Box Setup Complete!${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "📁 Directory Structure Created:"
echo "   /mnt/storagebox/"
echo "   ├── music/         # For Navidrome"
echo "   ├── audiobooks/    # For Audiobookshelf"
echo "   ├── podcasts/      # For Audiobookshelf"
echo "   ├── downloads/     # For downloads (optional)"
echo "   ├── media/         # For other media (optional)"
echo "   └── backups/       # For backups"
echo ""
echo "📋 Next Steps:"
echo ""
echo "1. Upload media files to Storage Box:"
echo "   ${YELLOW}sftp ${STORAGE_BOX_USER}@${STORAGE_BOX_HOST}${NC}"
echo ""
echo "2. Or mount locally and copy:"
echo "   ${YELLOW}# From your Mac:${NC}"
echo "   ${YELLOW}scp -r /path/to/music/* root@${SERVER_IP}:${MOUNT_POINT}/music/${NC}"
echo ""
echo "3. Verify files on server:"
echo "   ${YELLOW}ssh root@${SERVER_IP} 'ls -lah ${MOUNT_POINT}/music/'${NC}"
echo ""
echo "4. Deploy media services:"
echo "   ${YELLOW}docker compose up -d navidrome audiobookshelf${NC}"
echo ""
echo "5. Access services:"
echo "   ${GREEN}https://navidrome.rodneyops.com${NC}"
echo "   ${GREEN}https://audiobooks.rodneyops.com${NC}"
echo ""

