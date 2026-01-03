#!/bin/bash
# Setup systemd service for automatic Storage Box mounting

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SERVER_IP="95.216.176.147"
SERVICE_UNIT="storagebox-mount.service"

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}⚙️  Storage Box Systemd Service Setup${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Check if running on server or locally
if [ "$(hostname)" = "gandalf-gate" ] || [ -f "/.dockerenv" ]; then
    SERVER_MODE=true
    echo -e "${GREEN}Running on server${NC}"
else
    SERVER_MODE=false
    echo -e "${GREEN}Running locally, will deploy to server${NC}"
fi

if [ "$SERVER_MODE" = true ]; then
    # Running on server directly
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
else
    # Running locally, need to copy files to server
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
fi

echo -e "${GREEN}📋 Step 1: Copying systemd service files to server...${NC}"

SERVICE_UNIT="storagebox-mount.service"

if [ "$SERVER_MODE" = true ]; then
    # On server, copy from local project
    cp "$PROJECT_ROOT/systemd/$SERVICE_UNIT" /etc/systemd/system/
    cp "$PROJECT_ROOT/scripts/mount-storagebox.sh" /usr/local/bin/
    chmod +x /usr/local/bin/mount-storagebox.sh
else
    # From local machine, copy to server
    scp "$PROJECT_ROOT/systemd/$SERVICE_UNIT" root@${SERVER_IP}:/etc/systemd/system/
    scp "$PROJECT_ROOT/scripts/mount-storagebox.sh" root@${SERVER_IP}:/usr/local/bin/
    ssh root@${SERVER_IP} "chmod +x /usr/local/bin/mount-storagebox.sh"
fi

echo -e "${GREEN}✅ Service files copied${NC}"

echo ""
echo -e "${GREEN}📋 Step 2: Configuring systemd service...${NC}"

if [ "$SERVER_MODE" = true ]; then
    # On server
    systemctl daemon-reload
    echo -e "${GREEN}✅ Systemd daemon reloaded${NC}"

    # Disable old services if they exist
    systemctl disable mnt-storagebox.mount 2>/dev/null || true
    systemctl disable mnt-storagebox.automount 2>/dev/null || true
    systemctl stop mnt-storagebox.mount 2>/dev/null || true
    systemctl stop mnt-storagebox.automount 2>/dev/null || true

    # Enable and start new service
    systemctl enable ${SERVICE_UNIT}
    systemctl start ${SERVICE_UNIT}

    echo -e "${GREEN}✅ Storage Box mount service enabled and started${NC}"
else
    # From local machine
    ssh root@${SERVER_IP} bash << EOF
        systemctl daemon-reload
        echo "✅ Systemd daemon reloaded"

        # Disable old services if they exist
        systemctl disable mnt-storagebox.mount 2>/dev/null || true
        systemctl disable mnt-storagebox.automount 2>/dev/null || true
        systemctl stop mnt-storagebox.mount 2>/dev/null || true
        systemctl stop mnt-storagebox.automount 2>/dev/null || true

        # Enable and start new service
        systemctl enable ${SERVICE_UNIT}
        systemctl start ${SERVICE_UNIT}

        echo "✅ Storage Box mount service enabled and started"
EOF
fi

echo ""
echo -e "${GREEN}📋 Step 3: Verifying service status...${NC}"

if [ "$SERVER_MODE" = true ]; then
    systemctl status ${SERVICE_UNIT} --no-pager | head -10
    echo ""
    if mountpoint -q /mnt/storagebox; then
        echo -e "${GREEN}✅ Storage Box is mounted${NC}"
        df -h | grep storagebox
    else
        echo -e "${YELLOW}⚠️  Storage Box not mounted${NC}"
        echo "   Check logs: journalctl -u ${SERVICE_UNIT}"
    fi
else
    ssh root@${SERVER_IP} "systemctl status ${SERVICE_UNIT} --no-pager | head -10"
    echo ""
    ssh root@${SERVER_IP} "if mountpoint -q /mnt/storagebox; then echo '✅ Storage Box is mounted'; df -h | grep storagebox; else echo '⚠️  Storage Box not mounted'; echo '   Check logs: journalctl -u ${SERVICE_UNIT}'; fi"
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ Systemd Service Setup Complete!${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${BLUE}📋 Service Management:${NC}"
echo ""
echo "  Check status:"
echo "    ${YELLOW}sudo systemctl status storagebox-mount.service${NC}"
echo ""
echo "  Manually mount:"
echo "    ${YELLOW}sudo systemctl start storagebox-mount.service${NC}"
echo ""
echo "  Unmount:"
echo "    ${YELLOW}sudo systemctl stop storagebox-mount.service${NC}"
echo ""
echo "  View logs:"
echo "    ${YELLOW}sudo journalctl -u storagebox-mount.service${NC}"
echo ""
