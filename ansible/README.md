# Ansible Deployment for Homelab

This directory contains Ansible playbooks and roles for deploying and managing the homelab infrastructure.

## Structure

```
ansible/
├── inventory.yml          # Server inventory
├── playbook.yml           # Main deployment playbook
├── ansible.cfg            # Ansible configuration
├── requirements.yml       # Role dependencies
└── roles/
    ├── sync_config/       # Sync configuration files
    ├── sync_secrets/      # Manage secrets and .env file
    ├── deploy_services/   # Deploy docker-compose services
    └── health_check/      # Verify service health
```

## Prerequisites

1. **Ansible installed** (2.9+):

   ```bash
   pip install ansible
   # or
   brew install ansible
   ```

2. **SSH access** to the server:

   ```bash
   ssh deploy@95.216.176.147
   ```

3. **Environment variables** or Ansible vault with secrets:
   - `STORAGE_BOX_PASSWORD`
   - `CROWDSEC_ENROLL_KEY`
   - `CROWDSEC_BOUNCER_KEY`
   - `GRAFANA_ADMIN_PASSWORD`
   - `GOTIFY_ADMIN_PASSWORD`
   - `TS_AUTHKEY`

## Usage

### Local Deployment

```bash
# From project root
cd ansible

# Deploy everything
ansible-playbook playbook.yml

# Deploy specific roles
ansible-playbook playbook.yml --tags sync_config,deploy_services

# Dry run (check mode)
ansible-playbook playbook.yml --check

# Verbose output
ansible-playbook playbook.yml -v
```

### Using Ansible Vault (Recommended)

1. **Create vault file**:

   ```bash
   ansible-vault create ansible/vault.yml
   ```

2. **Edit vault**:

   ```bash
   ansible-vault edit ansible/vault.yml
   ```

3. **Add to vault.yml**:

   ```yaml
   vault_storage_box_password: "your-password"
   vault_crowdsec_enroll_key: "your-key"
   vault_crowdsec_bouncer_key: "your-key"
   vault_grafana_admin_password: "your-password"
   vault_gotify_admin_password: "your-password"
   vault_tailscale_auth_key: "your-key"
   ```

4. **Run with vault**:

   ```bash
   ansible-playbook playbook.yml --ask-vault-pass
   ```

### Using Environment Variables

```bash
export STORAGE_BOX_PASSWORD="your-password"
export CROWDSEC_ENROLL_KEY="your-key"
export CROWDSEC_BOUNCER_KEY="your-key"
export GRAFANA_ADMIN_PASSWORD="your-password"
export GOTIFY_ADMIN_PASSWORD="your-password"
export TS_AUTHKEY="your-key"

ansible-playbook playbook.yml
```

## Roles

### sync_config

- Syncs `docker-compose.yml` to server
- Syncs configuration files (preserves runtime data)
- Ensures proper file permissions

### sync_secrets

- Creates `.env` file from environment variables or vault
- Maps variable names (e.g., `TS_AUTHKEY` → `TAILSCALE_AUTH_KEY`)
- Syncs secret files if provided

### deploy_services

- Pulls latest Docker images
- Deploys services with rolling updates
- Verifies services are running

### health_check

- Waits for services to be healthy
- Verifies critical services (Traefik, CrowdSec, Authelia)
- Checks service endpoints
- Monitors disk usage

## Integration with GitHub Actions

The GitHub Actions workflow uses this Ansible playbook for deployment. See `.github/workflows/deploy.yml` for details.

## Troubleshooting

### Connection Issues

```bash
# Test SSH connection
ansible all -m ping

# Test with verbose output
ansible all -m ping -vvv
```

### Permission Issues

```bash
# Ensure deploy user has sudo access
ansible all -m shell -a "sudo -l" -u deploy
```

### Service Issues

```bash
# Check service status
ansible all -m shell -a "cd /opt/homelab && docker-compose ps" -u deploy
```

## Best Practices

1. **Use Ansible Vault** for secrets (don't commit plaintext secrets)
2. **Test in check mode** before actual deployment: `--check`
3. **Use tags** to run specific parts: `--tags sync_config`
4. **Review changes** with `--diff` flag
5. **Keep inventory updated** with actual server details
