.PHONY: help init up down restart logs backup restore health security-scan clean

##############################################################################
# SECURE HOMELAB INFRASTRUCTURE - Makefile
##############################################################################

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

init: ## Initialize the infrastructure (first-time setup)
	@echo "Initializing homelab infrastructure..."
	@bash scripts/init-setup.sh

check-env: ## Check if .env file exists
	@if [ ! -f .env ]; then \
		echo "Error: .env file not found. Copy .env.example to .env and configure it."; \
		exit 1; \
	fi

generate-secrets: ## Generate random secrets for Authelia
	@echo "Generating secrets..."
	@mkdir -p config/authelia config/traefik
	@openssl rand -hex 32 > config/authelia/jwt_secret.txt
	@openssl rand -hex 32 > config/authelia/session_secret.txt
	@openssl rand -hex 32 > config/authelia/storage_encryption_key.txt
	@chmod 600 config/authelia/*.txt
	@echo "Secrets generated in config/authelia/"

setup-acme: ## Setup ACME certificate file
	@mkdir -p config/traefik
	@touch config/traefik/acme.json
	@chmod 600 config/traefik/acme.json
	@echo "ACME certificate file created"

up: check-env ## Start all services
	@echo "Starting homelab infrastructure..."
	@docker-compose up -d
	@echo "Services started. Run 'make logs' to view logs"

down: ## Stop all services
	@echo "Stopping homelab infrastructure..."
	@docker-compose down

restart: ## Restart all services
	@echo "Restarting homelab infrastructure..."
	@docker-compose restart

stop: ## Stop all services without removing containers
	@docker-compose stop

logs: ## View logs from all services
	@docker-compose logs -f --tail=100

logs-traefik: ## View Traefik logs
	@docker-compose logs -f traefik

logs-crowdsec: ## View CrowdSec logs
	@docker-compose logs -f crowdsec

logs-authelia: ## View Authelia logs
	@docker-compose logs -f authelia

ps: ## Show running services
	@docker-compose ps

health: ## Check health of all services
	@echo "Checking service health..."
	@python3 -m homelab_tools health-check --local

backup: ## Backup configurations and databases
	@echo "Running backup..."
	@python3 -m homelab_tools backup create --type full

restore: ## Restore from backup
	@echo "Running restore..."
	@python3 -m homelab_tools restore list
	@echo "Use 'python3 -m homelab_tools restore extract <archive-name>' to restore"

security-scan: ## Run security vulnerability scan
	@echo "Running security scan..."
	@docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy image --severity HIGH,CRITICAL $(shell docker-compose config --services)

update: ## Pull latest images and restart
	@echo "Pulling latest images..."
	@docker-compose pull
	@echo "Recreating containers with new images..."
	@docker-compose up -d --force-recreate
	@echo "Cleanup old images..."
	@docker image prune -f

crowdsec-decisions: ## Show CrowdSec active decisions (bans)
	@docker exec crowdsec cscli decisions list

crowdsec-metrics: ## Show CrowdSec metrics
	@docker exec crowdsec cscli metrics

crowdsec-add-bouncer: ## Add a new CrowdSec bouncer
	@docker exec crowdsec cscli bouncers add traefik-bouncer

authelia-users: ## List Authelia users
	@docker exec authelia authelia storage user list

clean: ## Remove all stopped containers and unused volumes
	@echo "Cleaning up..."
	@docker-compose down -v
	@docker system prune -f
	@echo "Cleanup complete"

clean-all: ## WARNING: Remove all data including volumes
	@echo "WARNING: This will remove ALL data including volumes!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose down -v; \
		docker system prune -af --volumes; \
		echo "All data removed"; \
	fi

monitor: ## Open monitoring dashboard URLs
	@echo "Opening monitoring dashboards..."
	@echo "Traefik: https://traefik.${DOMAIN}"
	@echo "Grafana: https://grafana.${DOMAIN}"
	@echo "Status: https://status.${DOMAIN}"

setup-storage-box: ## Mount Hetzner Storage Box
	@python3 -m homelab_tools storage mount --box all

storage-status: ## Show Storage Box status
	@python3 -m homelab_tools storage status

##############################################################################
# Development Commands
##############################################################################

validate: ## Validate docker-compose.yml syntax
	@docker-compose config > /dev/null
	@echo "docker-compose.yml is valid"

test-traefik: ## Test Traefik configuration
	@docker-compose exec traefik traefik healthcheck --ping

install-deps: ## Install required system dependencies
	@echo "Installing dependencies..."
	@sudo apt-get update
	@sudo apt-get install -y cifs-utils docker.io docker-compose make
	@echo "Dependencies installed"

##############################################################################
# 1Password Integration
##############################################################################

setup-1password: ## Setup 1Password CLI and create vault structure
	@bash scripts/setup-1password.sh

inject-secrets: ## Inject secrets from 1Password into .env
	@echo "Injecting secrets from 1Password..."
	@op inject -i .env.template -o .env
	@echo "✅ Secrets injected"

run-with-1password: ## Run docker-compose with 1Password secrets
	@op run -- docker-compose up -d

##############################################################################
# Ansible Deployment Commands
##############################################################################

ansible-install: ## Install Ansible
	@echo "Installing Ansible..."
	@pip install ansible
	@echo "✅ Ansible installed"

ansible-check: ## Check Ansible syntax
	@cd ansible && ansible-playbook --syntax-check playbook.yml
	@cd ansible && ansible-inventory --list

ansible-deploy: ansible-deploy-core ## Deploy core infrastructure (default)

ansible-deploy-core: ## Deploy core infrastructure (Tailscale, Security, Monitoring)
	@echo "Deploying core infrastructure with Ansible..."
	@set -a && . .env && set +a && cd ansible && ansible-playbook playbook.yml -v

ansible-deploy-arr: ## Deploy Jellyfin, Jellyseerr,and Arr stack (Gluetun + all Arr services)
	@echo "Deploying Arr stack with Ansible..."
	@set -a && . .env && set +a && cd ansible && ansible-playbook playbooks/deploy-arr-stack.yml -v

ansible-deploy-immich: ## Deploy Immich photo management
	@echo "Deploying Immich stack with Ansible..."
	@set -a && . .env && set +a && cd ansible && ansible-playbook playbooks/deploy-immich.yml -v

ansible-deploy-pdf: ## Deploy PDF document management
	@echo "Deploying PDF management stack with Ansible..."
	@set -a && . .env && set +a && cd ansible && ansible-playbook playbooks/deploy-pdf.yml -v

ansible-deploy-media: ## Deploy media services (Audiobookshelf & Navidrome)
	@echo "Deploying media services stack with Ansible..."
	@set -a && . .env && set +a && cd ansible && ansible-playbook playbooks/deploy-media.yml -v

ansible-deploy-monitoring: ## Deploy monitoring stack (Prometheus, Grafana, Loki, Promtail, etc.)
	@echo "Deploying monitoring stack with Ansible..."
	@set -a && . .env && set +a && cd ansible && ansible-playbook playbooks/deploy-monitoring.yml -v

ansible-deploy-all: ## Deploy all services (core + all stacks)
	@echo "Deploying all services with Ansible..."
	@set -a && . .env && set +a && cd ansible && \
		ansible-playbook playbook.yml -v && \
		ansible-playbook playbooks/deploy-jellyfin.yml -v && \
		ansible-playbook playbooks/deploy-arr-stack.yml -v && \
		ansible-playbook playbooks/deploy-immich.yml -v && \
		ansible-playbook playbooks/deploy-pdf.yml -v

ansible-deploy-check: ## Dry run deployment (check mode) - core only
	@set -a && . .env && set +a && cd ansible && ansible-playbook playbook.yml --check

ansible-deploy-tags: ## Deploy specific tags (usage: make ansible-deploy-tags TAGS=sync_config,deploy_services)
	@set -a && . .env && set +a && cd ansible && ansible-playbook playbook.yml --tags $(TAGS)

ansible-vault-create: ## Create Ansible vault file
	@set -a && . .env && set +a && cd ansible && ansible-vault create vault.yml

ansible-vault-edit: ## Edit Ansible vault file
	@set -a && . .env && set +a && cd ansible && ansible-vault edit vault.yml

ansible-vault-view: ## View Ansible vault file
	@set -a && . .env && set +a && cd ansible && ansible-vault view vault.yml

ansible-ping: ## Test Ansible connection to server
	@set -a && . .env && set +a && cd ansible && ansible all -m ping

ansible-setup-server: ## Create Hetzner server and Storage Box, then configure everything
	@echo "🚀 Setting up new Hetzner server and Storage Box..."
	@echo "⚠️  This will create a new server and Storage Box via Hetzner API"
	@echo "📋 Make sure HETZNER_API_TOKEN is set in vault.yml or environment"
	@set -a && . .env && set +a && cd ansible && ansible-playbook playbooks/setup-server.yml -v

##############################################################################
# QA & Security Checks
##############################################################################

setup-git-hooks: ## Setup Git hooks for security and QA
	@python3 -m homelab_tools git-hooks install

scan-secrets: ## Scan for hardcoded secrets
	@echo "🔍 Scanning for secrets..."
	@if command -v gitleaks >/dev/null 2>&1; then \
		gitleaks detect --source . --verbose; \
	else \
		echo "❌ gitleaks not installed. Install with: brew install gitleaks"; \
	fi

verify-secrets: ## Verify 1Password secrets are accessible
	@echo "🔍 Verifying secrets..."
	@if command -v op >/dev/null 2>&1; then \
		op inject -i .env.template -o .env.test && echo "✅ Secrets accessible" && rm -f .env.test; \
	else \
		echo "⚠️  1Password CLI not installed"; \
	fi

test-1password: ## Test 1Password integration
	@bash scripts/test-1password-secrets.sh

lint-yaml: ## Lint all YAML files
	@echo "📝 Linting YAML files..."
	@if command -v yamllint >/dev/null 2>&1; then \
		yamllint -c .yamllint.yml .; \
	else \
		echo "❌ yamllint not installed. Install with: pip install yamllint"; \
	fi

lint-shell: ## Lint shell scripts
	@echo "🐚 Linting shell scripts..."
	@if command -v shellcheck >/dev/null 2>&1; then \
		find scripts -type f -name "*.sh" -exec shellcheck {} \;; \
	else \
		echo "❌ shellcheck not installed. Install with: brew install shellcheck"; \
	fi

lint-markdown: ## Lint Markdown files
	@echo "📄 Linting Markdown files..."
	@if command -v markdownlint >/dev/null 2>&1; then \
		markdownlint -c .markdownlint.json .; \
	else \
		echo "⚠️  markdownlint not installed. Install with: npm install -g markdownlint-cli"; \
	fi

lint-dockerfile: ## Lint Dockerfile
	@echo "🐳 Linting Dockerfile..."
	@if command -v hadolint >/dev/null 2>&1; then \
		hadolint Dockerfile; \
	else \
		echo "❌ hadolint not installed. Install with: brew install hadolint"; \
	fi

format-check: ## Check formatting with Prettier (no changes)
	@echo "🎨 Checking code formatting..."
	@if command -v prettier >/dev/null 2>&1; then \
		prettier --config .prettierrc --ignore-path .prettierignore --check "**/*.{yml,yaml,md,json}"; \
	else \
		echo "❌ prettier not installed. Install with: npm install -g prettier"; \
	fi

format-fix: ## Fix formatting with Prettier
	@echo "🎨 Formatting code with Prettier..."
	@if command -v prettier >/dev/null 2>&1; then \
		prettier --config .prettierrc --ignore-path .prettierignore --write "**/*.{yml,yaml,md,json}"; \
		echo "✅ Files formatted!"; \
	else \
		echo "❌ prettier not installed. Install with: npm install -g prettier"; \
	fi

format-yaml: ## Format YAML files only
	@echo "🎨 Formatting YAML files..."
	@if command -v prettier >/dev/null 2>&1; then \
		prettier --config .prettierrc --write "**/*.{yml,yaml}"; \
	else \
		echo "❌ prettier not installed. Install with: npm install -g prettier"; \
	fi

format-markdown: ## Format Markdown files only
	@echo "🎨 Formatting Markdown files..."
	@if command -v prettier >/dev/null 2>&1; then \
		prettier --config .prettierrc --write "**/*.md"; \
	else \
		echo "❌ prettier not installed. Install with: npm install -g prettier"; \
	fi

lint-all: lint-yaml lint-shell lint-markdown lint-dockerfile ## Run all linters

qa-check: scan-secrets format-check lint-all validate ## Run all QA checks (including format check)
	@echo ""
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "✅ All QA checks completed!"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

pre-commit: qa-check verify-secrets ## Run pre-commit checks
	@echo "✅ Ready to commit!"

pre-deploy: qa-check verify-secrets health ## Run pre-deployment checks
	@echo "✅ Ready to deploy!"

##############################################################################
# Cleanup Commands
##############################################################################

cleanup-old: ## Cleanup old docker-compose directories (deprecated - no longer needed)
	@echo "⚠️  This command is deprecated. Old directories have been removed."
