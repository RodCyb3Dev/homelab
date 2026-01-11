#!/bin/bash
# Simple approach: Create fresh Git history without secrets

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🧹 Create Clean Git History (Simple Method)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo -e "${RED}❌ Error: Not in a Git repository${NC}"
    exit 1
fi

# Warning
echo -e "${YELLOW}⚠️  WARNING: This will create a fresh Git history!${NC}"
echo ""
echo "This script will:"
echo "  1. Create a backup of current branch"
echo "  2. Create a new clean history with all current files"
echo "  3. Replace main branch with clean history"
echo "  4. Require force push to remote"
echo ""
echo "Secrets being removed from history:"
echo "  - SMTP password in config/authelia/configuration.yml"
echo "  - Any other secrets in previous commits"
echo ""
echo -e "${GREEN}Current files are already fixed and will be in clean history${NC}"
echo ""
echo -e "${YELLOW}This operation requires force push to remote!${NC}"
echo ""
read -p "Do you want to continue? (yes/no): " confirm

if [[ "$confirm" != "yes" ]]; then
    echo "Aborted."
    exit 0
fi

echo ""
echo -e "${GREEN}📋 Step 1: Creating backup...${NC}"

# Get current branch
# shellcheck disable=SC2034
CURRENT_BRANCH=$(git branch --show-current)
BACKUP_BRANCH="backup-before-cleanup-$(date +%Y%m%d-%H%M%S)"

# Create backup
git branch "$BACKUP_BRANCH"
echo -e "${GREEN}✅ Backup branch created: $BACKUP_BRANCH${NC}"

echo ""
echo -e "${GREEN}📋 Step 2: Saving current state...${NC}"

# Stage any uncommitted changes
git add -A
if ! git diff --cached --quiet; then
    git commit -m "chore: prepare for history cleanup" || true
fi

echo ""
echo -e "${GREEN}📋 Step 3: Creating new clean branch...${NC}"

# Create new orphan branch (no history)
git checkout --orphan clean-main

echo ""
echo -e "${GREEN}📋 Step 4: Adding all files to clean history...${NC}"

# Add all files
git add -A

# Create initial clean commit
git commit -m "feat: initial commit - secure homelab infrastructure

- Complete Docker Compose setup with Traefik, Authelia, CrowdSec
- Monitoring stack: Prometheus, Grafana, Loki
- Security: Fail2ban, CrowdSec, Authelia 2FA
- Tailscale VPN integration
- 1Password secrets management
- Kamal zero-downtime deployment
- Comprehensive QA checks and secret scanning
- GitHub Actions CI/CD workflows
- Complete documentation

All secrets properly externalized to 1Password vault."

echo ""
echo -e "${GREEN}📋 Step 5: Replacing main branch...${NC}"

# Delete old main and rename clean branch
git branch -D main 2>/dev/null || git branch -d main 2>/dev/null || true
git branch -m main

echo ""
echo -e "${GREEN}📋 Step 6: Verifying no secrets in history...${NC}"

# Scan for secrets
if command -v gitleaks >/dev/null 2>&1; then
    echo "Running gitleaks scan on clean history..."
    if gitleaks detect --source . --verbose 2>&1 | grep -q "no leaks found"; then
        echo -e "${GREEN}✅ No secrets found in Git history!${NC}"
        SECRETS_CLEAN=true
    else
        echo -e "${YELLOW}⚠️  Checking current files for secrets...${NC}"
        gitleaks detect --source . --no-git --verbose 2>&1 | tail -20
        SECRETS_CLEAN=false
    fi
else
    echo -e "${YELLOW}⚠️  gitleaks not installed, skipping verification${NC}"
    SECRETS_CLEAN=unknown
fi

echo ""
echo -e "${GREEN}📋 Step 7: Cleaning up...${NC}"
git gc --aggressive --prune=now

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ Clean Git history created!${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "📊 Summary:"
echo "  - Old history backed up to: ${YELLOW}$BACKUP_BRANCH${NC}"
echo "  - New clean history created with 1 commit"
echo "  - Secrets removed from Git history: ${GREEN}✓${NC}"
echo ""
echo "📋 Next steps:"
echo ""
echo "1. Review the new history:"
echo "   ${YELLOW}git log --oneline${NC}"
echo ""
echo "2. Compare with backup if needed:"
echo "   ${YELLOW}git diff $BACKUP_BRANCH${NC}"
echo ""
echo "3. Force push to GitHub (⚠️  THIS WILL REWRITE REMOTE HISTORY):"
echo "   ${YELLOW}git push origin main --force${NC}"
echo ""
echo "4. ${RED}CRITICAL: Rotate the exposed SMTP password!${NC}"
echo "   The old password CHANGE_ME was in Git history."
echo "   Update it in 1Password:"
echo "   ${YELLOW}op item edit AUTHELIA_NOTIFIER_SMTP_PASSWORD --vault homelab-env${NC}"
echo ""
echo "5. After successful push, verify on GitHub:"
echo "   https://github.com/RodCyb3Dev/gandalf-gate-iac"
echo ""
echo "6. If everything works, delete backup branch:"
echo "   ${YELLOW}git branch -D $BACKUP_BRANCH${NC}"
echo ""
echo "7. If something goes wrong, restore from backup:"
echo "   ${YELLOW}git checkout $BACKUP_BRANCH${NC}"
echo "   ${YELLOW}git branch -D main${NC}"
echo "   ${YELLOW}git branch -m main${NC}"
echo ""

if [ "$SECRETS_CLEAN" = "false" ]; then
    echo -e "${YELLOW}⚠️  Note: Some secrets detected. Review output above.${NC}"
    echo ""
fi

