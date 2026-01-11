#!/bin/bash
##############################################################################
# CLEANUP OLD DIRECTORIES
# Removes old docker-compose-pangolin and docker-compose-tailscale directories
##############################################################################

set -e

# Colors
# shellcheck disable=SC2034
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  CLEANUP OLD DIRECTORIES${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Base directory
BASE_DIR="/Users/rodneyhammad/Private/Gandalf-gate-docke"

# Directories to clean up
OLD_DIRS=(
    "$BASE_DIR/docker-compose-pangolin"
    "$BASE_DIR/docker-compose-tailscale"
)

##############################################################################
# BACKUP BEFORE CLEANUP
##############################################################################

echo -e "${YELLOW}Creating backup before cleanup...${NC}"

BACKUP_DIR="$BASE_DIR/old-configs-backup-$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

for dir in "${OLD_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        dir_name=$(basename "$dir")
        echo "Backing up: $dir_name"
        cp -r "$dir" "$BACKUP_DIR/"
    fi
done

echo -e "${GREEN}✅ Backup created: $BACKUP_DIR${NC}"
echo ""

##############################################################################
# LIST WHAT WILL BE REMOVED
##############################################################################

echo -e "${YELLOW}The following directories will be removed:${NC}"
echo ""

TOTAL_SIZE=0

for dir in "${OLD_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        SIZE=$(du -sh "$dir" | cut -f1)
        TOTAL_SIZE=$((TOTAL_SIZE + $(du -s "$dir" | cut -f1)))
        echo "  📁 $dir ($SIZE)"
    fi
done

echo ""
echo -e "${YELLOW}Total space to be freed: $(numfmt --to=iec --from-unit=1024 $TOTAL_SIZE)${NC}"
echo ""

##############################################################################
# CONFIRMATION
##############################################################################

read -p "⚠️  Do you want to proceed with cleanup? (yes/no): " -r
if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo "Cleanup cancelled."
    exit 0
fi

echo ""

##############################################################################
# CLEANUP
##############################################################################

echo -e "${YELLOW}Starting cleanup...${NC}"
echo ""

for dir in "${OLD_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        dir_name=$(basename "$dir")
        echo -n "Removing $dir_name... "
        rm -rf "$dir"
        echo -e "${GREEN}✅${NC}"
    else
        echo "$dir does not exist, skipping"
    fi
done

echo ""

##############################################################################
# CLEANUP OTHER FILES
##############################################################################

echo -e "${YELLOW}Cleaning up other old files...${NC}"
echo ""

# Check for old Docker volumes
if docker volume ls | grep -q "pangolin\|arr-stack"; then
    echo "Found old Docker volumes:"
    docker volume ls | grep "pangolin\|arr-stack" || true
    echo ""
    read -p "Remove old Docker volumes? (yes/no): " -r
    if [[ $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        docker volume ls | grep "pangolin\|arr-stack" | awk '{print $2}' | xargs -r docker volume rm
        echo -e "${GREEN}✅ Old volumes removed${NC}"
    fi
fi

# Check for old Docker networks
if docker network ls | grep -q "pangolin\|starr\|ts-anduin"; then
    echo "Found old Docker networks:"
    docker network ls | grep "pangolin\|starr\|ts-anduin" || true
    echo ""
    read -p "Remove old Docker networks? (yes/no): " -r
    if [[ $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        docker network ls | grep "pangolin\|starr\|ts-anduin" | awk '{print $1}' | xargs -r docker network rm
        echo -e "${GREEN}✅ Old networks removed${NC}"
    fi
fi

echo ""

##############################################################################
# SUMMARY
##############################################################################

echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✅ CLEANUP COMPLETE${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "Summary:"
echo "  • Old directories removed"
echo "  • Backup created: $BACKUP_DIR"
echo "  • Space freed: $(numfmt --to=iec --from-unit=1024 $TOTAL_SIZE)"
echo ""
echo "Next steps:"
echo "  1. Review the new homelab infrastructure: cd homelab/"
echo "  2. Configure environment: cp .env.example .env"
echo "  3. Deploy: make up"
echo ""
echo -e "${YELLOW}Note: You can restore from backup if needed:${NC}"
echo "  cp -r $BACKUP_DIR/* $BASE_DIR/"
echo ""

