#!/bin/bash
##############################################################################
# 1PASSWORD INTEGRATION SETUP
# Sets up 1Password CLI for secure secret management
##############################################################################

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  1PASSWORD SETUP FOR HOMELAB${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

##############################################################################
# CHECK 1PASSWORD CLI
##############################################################################

if ! command -v op &> /dev/null; then
    echo -e "${YELLOW}1Password CLI not found. Installing...${NC}"
    
    # Detect OS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        brew install 1password-cli
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        curl -sS https://downloads.1password.com/linux/keys/1password.asc | \
            sudo gpg --dearmor --output /usr/share/keyrings/1password-archive-keyring.gpg
        echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/1password-archive-keyring.gpg] https://downloads.1password.com/linux/debian/$(dpkg --print-architecture) stable main" | \
            sudo tee /etc/apt/sources.list.d/1password.list
        sudo mkdir -p /etc/debsig/policies/AC2D62742012EA22/
        curl -sS https://downloads.1password.com/linux/debian/debsig/1password.pol | \
            sudo tee /etc/debsig/policies/AC2D62742012EA22/1password.pol
        sudo mkdir -p /usr/share/debsig/keyrings/AC2D62742012EA22
        curl -sS https://downloads.1password.com/linux/keys/1password.asc | \
            sudo gpg --dearmor --output /usr/share/debsig/keyrings/AC2D62742012EA22/debsig.gpg
        sudo apt update && sudo apt install 1password-cli
    else
        echo -e "${RED}Unsupported OS. Please install 1Password CLI manually.${NC}"
        echo "https://developer.1password.com/docs/cli/get-started/"
        exit 1
    fi
fi

echo -e "${GREEN}✅ 1Password CLI installed${NC}"
echo ""

##############################################################################
# SIGN IN
##############################################################################

echo -e "${YELLOW}Signing into 1Password...${NC}"
echo "Please follow the prompts to sign in."
echo ""

eval "$(op signin)"

echo -e "${GREEN}✅ Signed into 1Password${NC}"
echo ""

##############################################################################
# CREATE VAULT STRUCTURE
##############################################################################

echo -e "${YELLOW}Setting up homelab vault structure...${NC}"
echo ""

VAULT_NAME="homelab"

# Check if vault exists
if ! op vault get "$VAULT_NAME" &>/dev/null; then
    echo "Creating vault: $VAULT_NAME"
    op vault create "$VAULT_NAME"
fi

##############################################################################
# CREATE ITEMS
##############################################################################

create_item() {
    local item_name=$1
    local category=$2
    shift 2
    
    echo -n "Creating item: $item_name... "
    
    if op item get "$item_name" --vault="$VAULT_NAME" &>/dev/null; then
        echo -e "${YELLOW}exists${NC}"
    else
        op item create \
            --category="$category" \
            --title="$item_name" \
            --vault="$VAULT_NAME" \
            "$@" &>/dev/null
        echo -e "${GREEN}created${NC}"
    fi
}

echo "Creating credential items..."

# Hetzner Storage Box
create_item "hetzner-storage-box" "password" \
    "password=changeme"

# Cloudflare
create_item "cloudflare" "api-credential" \
    "api-token=changeme"

# Tailscale
create_item "tailscale" "api-credential" \
    "auth-key=changeme"

# CrowdSec
create_item "crowdsec" "api-credential" \
    "enroll-key=changeme" \
    "bouncer-api-key=changeme"

# Authelia
JWT_SECRET=$(openssl rand -hex 32)
SESSION_SECRET=$(openssl rand -hex 32)
STORAGE_KEY=$(openssl rand -hex 32)

create_item "authelia" "api-credential" \
    "jwt-secret=$JWT_SECRET" \
    "session-secret=$SESSION_SECRET" \
    "storage-encryption-key=$STORAGE_KEY"

# SMTP
create_item "smtp" "login" \
    "username=changeme" \
    "password=changeme"

# Grafana
GRAFANA_PASS=$(openssl rand -base64 32)
create_item "grafana" "login" \
    "username=admin" \
    "admin-password=$GRAFANA_PASS"

# Gotify
GOTIFY_PASS=$(openssl rand -base64 32)
create_item "gotify" "login" \
    "username=admin" \
    "admin-password=$GOTIFY_PASS"

# ProtonVPN
create_item "protonvpn" "api-credential" \
    "wireguard-private-key=changeme"

# GitHub
create_item "github" "api-credential" \
    "container-registry-token=changeme"

echo ""
echo -e "${GREEN}✅ Vault structure created${NC}"
echo ""

##############################################################################
# GENERATE .ENV FILE
##############################################################################

echo -e "${YELLOW}Generating .env file from 1Password...${NC}"

cat > .env.template << 'EOF'
# Generated from 1Password - Do not edit manually
TZ=Europe/Helsinki
DOMAIN=rodneyops.com
PUID=1000
PGID=1000

# Hetzner Storage Box
STORAGE_BOX_PASSWORD=op://homelab/hetzner-storage-box/password

# Cloudflare
CF_API_TOKEN=op://homelab/cloudflare/api-token

# Tailscale
TAILSCALE_AUTH_KEY=op://homelab/tailscale/auth-key
TAILSCALE_DOMAIN=kooka-lake.ts.net

# CrowdSec
CROWDSEC_ENROLL_KEY=op://homelab/crowdsec/enroll-key
CROWDSEC_BOUNCER_KEY=op://homelab/crowdsec/bouncer-api-key

# Authelia
AUTHELIA_JWT_SECRET=op://homelab/authelia/jwt-secret
AUTHELIA_SESSION_SECRET=op://homelab/authelia/session-secret
AUTHELIA_STORAGE_ENCRYPTION_KEY=op://homelab/authelia/storage-encryption-key

# SMTP
SMTP_HOST=smtp.protonmail.ch
SMTP_PORT=587
SMTP_USERNAME=op://homelab/smtp/username
SMTP_PASSWORD=op://homelab/smtp/password

# Grafana
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=op://homelab/grafana/admin-password

# Gotify
GOTIFY_ADMIN_USER=admin
GOTIFY_ADMIN_PASSWORD=op://homelab/gotify/admin-password

# VPN (Gluetun)
VPN_PROVIDER=protonvpn
VPN_PRIVATE_KEY=op://homelab/protonvpn/wireguard-private-key
VPN_ADDRESSES=10.2.0.2/32
VPN_COUNTRIES=Netherlands

# Jellyfin
JELLYFIN_PUBLISHED_URL=https://jellyfin.kooka-lake.ts.net

# Kamal Deployment
KAMAL_REGISTRY=ghcr.io
KAMAL_REGISTRY_USERNAME=your-github-username
KAMAL_REGISTRY_PASSWORD=op://homelab/github/container-registry-token
EOF

# Inject secrets
op inject -i .env.template -o .env

echo -e "${GREEN}✅ .env file generated${NC}"
echo ""

##############################################################################
# CREATE SECRET FILES
##############################################################################

echo -e "${YELLOW}Creating secret files...${NC}"

mkdir -p config/authelia config/traefik

# Cloudflare API token
op read "op://homelab/cloudflare/api-token" > config/traefik/cf_api_token.txt
chmod 600 config/traefik/cf_api_token.txt

# Authelia secrets
op read "op://homelab/authelia/jwt-secret" > config/authelia/jwt_secret.txt
op read "op://homelab/authelia/session-secret" > config/authelia/session_secret.txt
op read "op://homelab/authelia/storage-encryption-key" > config/authelia/storage_encryption_key.txt
chmod 600 config/authelia/*.txt

echo -e "${GREEN}✅ Secret files created${NC}"
echo ""

##############################################################################
# SUMMARY
##############################################################################

echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✅ 1PASSWORD SETUP COMPLETE${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "Next steps:"
echo ""
echo "1. Update credentials in 1Password:"
echo "   op item edit hetzner-storage-box --vault=homelab password=YOUR_ACTUAL_PASSWORD"
echo ""
echo "2. View your secrets:"
echo "   op item list --vault=homelab"
echo ""
echo "3. Run docker-compose with injected secrets:"
echo "   op run -- docker-compose up -d"
echo ""
echo "4. Deploy with Kamal:"
echo "   op run -- kamal deploy"
echo ""
echo "5. Regenerate .env anytime:"
echo "   op inject -i .env.template -o .env"
echo ""
echo -e "${YELLOW}IMPORTANT: Never commit .env or .env.template to git!${NC}"
echo ""

