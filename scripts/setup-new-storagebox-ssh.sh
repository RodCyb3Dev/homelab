#!/bin/bash
# Setup SSH access to new Hetzner Storage Box (u526046)
# Based on: https://docs.hetzner.com/storage/storage-box/backup-space-ssh-keys

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SERVER_IP="95.216.176.147"
NEW_STORAGE_BOX_USER="u526046"
NEW_STORAGE_BOX_HOST="u526046.your-storagebox.de"
NEW_STORAGE_BOX_PASSWORD="gNV=ezPaR+uH5§k"
SSH_KEY_PATH="/root/.ssh/storagebox"

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🔧 Setup SSH Access to New Storage Box${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo -e "${YELLOW}📋 Prerequisites Check:${NC}"
echo ""
echo "1. ✅ SSH Support must be ENABLED in Hetzner Console"
echo "   - Go to: https://robot.hetzner.com/storage"
echo "   - Select Storage Box: ${NEW_STORAGE_BOX_HOST}"
echo "   - Click 'Change settings' → Enable 'SSH Support'"
echo "   - Wait 2-3 minutes for activation"
echo ""

read -p "Is SSH Support enabled? (y/N): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}⚠️  Please enable SSH Support in Hetzner Console first${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}📋 Step 1: Verify SSH key exists on server...${NC}"

ssh root@${SERVER_IP} bash << EOF
# Check if key exists
if [ ! -f ${SSH_KEY_PATH} ]; then
    echo "❌ SSH key not found. Generating..."
    ssh-keygen -t rsa -b 4096 -f ${SSH_KEY_PATH} -N '' -C 'storagebox-mount'
    echo "✅ SSH key generated"
else
    echo "✅ SSH key exists"
fi

# Display public key
echo ""
echo "📋 Server's public key:"
cat ${SSH_KEY_PATH}.pub
EOF

echo ""
echo -e "${GREEN}📋 Step 2: Add SSH key to new Storage Box${NC}"
echo ""
echo -e "${YELLOW}Run this command from your LOCAL machine (where password auth works):${NC}"
echo ""
echo "ssh root@${SERVER_IP} 'cat ${SSH_KEY_PATH}.pub' | ssh -p 23 ${NEW_STORAGE_BOX_USER}@${NEW_STORAGE_BOX_HOST} install-ssh-key"
echo ""
echo "Enter password when prompted: ${NEW_STORAGE_BOX_PASSWORD}"
echo ""

read -p "Have you added the SSH key? (y/N): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}⚠️  Please add the SSH key first${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}📋 Step 3: Test SSH key authentication...${NC}"

# Test connection
if ssh root@${SERVER_IP} "ssh -i ${SSH_KEY_PATH} -p 23 -o StrictHostKeyChecking=no -o ConnectTimeout=10 ${NEW_STORAGE_BOX_USER}@${NEW_STORAGE_BOX_HOST} 'echo \"✅ Connection successful!\" && df -h'" 2>&1 | grep -q "Connection successful"; then
    echo -e "${GREEN}✅ SSH key authentication works!${NC}"
    echo ""
    
    # Test SSHFS mount
    echo -e "${GREEN}📋 Step 4: Testing SSHFS mount...${NC}"
    
    ssh root@${SERVER_IP} bash << EOF
        MOUNT_POINT="/mnt/storagebox-new"
        
        # Create mount point
        mkdir -p \${MOUNT_POINT}
        
        # Test mount
        umount \${MOUNT_POINT} 2>/dev/null || true
        sshfs ${NEW_STORAGE_BOX_USER}@${NEW_STORAGE_BOX_HOST}:/ \${MOUNT_POINT} -p 23 -o IdentityFile=${SSH_KEY_PATH},uid=1000,gid=1000,allow_other,StrictHostKeyChecking=no 2>&1
        
        if mountpoint -q \${MOUNT_POINT}; then
            echo "✅ SSHFS mount successful!"
            echo ""
            echo "📊 Mount status:"
            df -h | grep storagebox-new
            echo ""
            echo "📁 Contents:"
            ls -lah \${MOUNT_POINT}/ | head -10
        else
            echo "❌ SSHFS mount failed"
            exit 1
        fi
EOF
    
    echo ""
    echo -e "${GREEN}✅ Setup complete!${NC}"
    echo ""
    echo -e "${BLUE}📋 Next steps:${NC}"
    echo "  1. Update /etc/fstab if needed"
    echo "  2. Create media directories"
    echo "  3. Update docker-compose.yml with new Storage Box"
    
else
    echo -e "${RED}❌ SSH key authentication failed${NC}"
    echo ""
    echo -e "${YELLOW}Possible issues:${NC}"
    echo "  1. SSH Support not enabled in Hetzner Console"
    echo "  2. Key not properly added (use install-ssh-key command)"
    echo "  3. Server IP blocked by Hetzner (contact support)"
    echo "  4. Wait a few minutes for Hetzner to process the key"
    echo ""
    echo -e "${YELLOW}Alternative: Test password authentication${NC}"
    echo "  ssh -p 23 ${NEW_STORAGE_BOX_USER}@${NEW_STORAGE_BOX_HOST}"
fi

