# Security Guide

Comprehensive security documentation for the homelab infrastructure.

## Table of Contents

- [Security Architecture](#security-architecture)
- [Pre-Deployment Security Checklist](#pre-deployment-security-checklist)
- [Code Quality & Secret Prevention](#code-quality--secret-prevention)
- [Authentication & Authorization](#authentication--authorization)
- [Network Security](#network-security)
- [Monitoring & Incident Response](#monitoring--incident-response)
- [Security Best Practices](#security-best-practices)

## Security Architecture

### Defense-in-Depth Strategy

The infrastructure implements 6 layers of security:

```
Layer 1: Cloudflare CDN/WAF
    ↓
Layer 2: Traefik Edge Security
    ↓
Layer 3: CrowdSec IDS/IPS
    ↓
Layer 4: Authelia SSO + 2FA
    ↓
Layer 5: Fail2ban System Protection
    ↓
Layer 6: Tailscale Zero-Trust VPN
```

### Layer 1: Cloudflare Protection

**Features:**

- DDoS protection (automatic)
- Web Application Firewall (WAF)
- Bot management
- Rate limiting (5000 req/min globally)
- Geo-blocking (configurable)

**Configuration:**

1. Enable "Under Attack" mode for maximum protection
2. Configure WAF rules: Security → WAF → Managed Rules
3. Enable Bot Fight Mode: Security → Bots
4. Configure rate limiting: Security → Rate Limiting

### Layer 2: Caddy Edge Security

**Features:**

- TLS 1.3 encryption (minimum)
- Security headers (HSTS, CSP, X-Frame-Options)
- Automatic HTTPS redirect
- Rate limiting per service
- IP whitelisting for admin interfaces

### Layer 3: CrowdSec IDS/IPS

**Features:**

- Real-time threat detection
- Community-sourced threat intelligence
- Automatic IP blocking
- Scenario-based detection

**Management:**

```bash
# View active decisions (bans)
docker exec crowdsec cscli decisions list

# View metrics
docker exec crowdsec cscli metrics

# Unban an IP
docker exec crowdsec cscli decisions delete -i <IP_ADDRESS>
```

### Layer 4: Authelia SSO + 2FA

**Features:**

- Single Sign-On (SSO) for all public services
- Time-based One-Time Password (TOTP) 2FA
- Session management
- Failed login protection (5 attempts = 10 min ban)

### Layer 5: Fail2ban System Protection

**Features:**

- SSH brute-force protection
- Docker socket protection
- Traefik authentication failure protection
- HTTP DoS protection

**Jail Configuration:**

- `sshd`: 3 failures = 1 hour ban
- `caddy-auth`: 5 failures = 1 hour ban
- `authelia`: 5 failures = 1 hour ban

### Layer 6: Tailscale Zero-Trust VPN

**Features:**

- Zero-trust network access
- End-to-end encrypted
- MagicDNS for service discovery
- ACLs for fine-grained access control

## Pre-Deployment Security Checklist

### 🔐 Secrets Management

- [ ] All secrets stored in 1Password or encrypted
- [ ] `.env` file gitignored (never committed)
- [ ] No hardcoded passwords in any files
- [ ] SSH keys have strong passphrases
- [ ] API tokens rotated from defaults
- [ ] ACME certificate file has correct permissions (600)

### 🔒 Authentication

- [ ] Strong admin passwords (16+ characters)
- [ ] 2FA enabled for all admin users
- [ ] Authelia configured with TOTP
- [ ] Default passwords changed for all services
- [ ] Password policy enforced (min 12 chars)

### 🌐 Network Security

- [ ] Firewall configured (only ports 22, 80, 443 open)
- [ ] SSH key-based authentication only
- [ ] Private services only via Tailscale
- [ ] Network segmentation configured

### 🛡️ Service Configuration

- [ ] Traefik dashboard behind Authelia + IP whitelist
- [ ] CrowdSec enrolled and active
- [ ] Fail2ban jails configured and active
- [ ] Security headers enabled (HSTS, CSP, etc.)
- [ ] TLS 1.3 minimum enforced
- [ ] Rate limiting configured

### 📊 Monitoring & Alerting

- [ ] Grafana alerts configured
- [ ] Gotify notifications working
- [ ] Log aggregation to Loki enabled
- [ ] Failed login attempts monitored

### 💾 Backup & Recovery

- [ ] Automated daily backups configured
- [ ] Backup tested (can restore)
- [ ] Backup stored offsite (Storage Box)
- [ ] Recovery procedure documented

## Code Quality & Secret Prevention

### Protection Layers

1. **Git Hooks** - Local pre-commit checks
2. **Pre-commit Framework** - Automated checks and formatters
3. **Gitleaks** - Secret detection scanner
4. **GitHub Actions** - CI/CD automated validation
5. **Linters** - YAML, Shell, Markdown, Dockerfile validation

### Setup

```bash
# Setup Git hooks
make setup-git-hooks

# Run all QA checks
make qa-check

# Format code
make format-fix
```

### Secret Detection

**Patterns detected:**

- API keys (Cloudflare, GitHub, AWS, etc.)
- Auth tokens (Tailscale, Grafana, JWT)
- Database passwords
- Private keys (SSH, TLS)
- Session secrets

**Best Practices:**

```yaml
# ✅ GOOD - Environment variable
password: ${POSTGRES_PASSWORD}

# ✅ GOOD - 1Password reference
password: "op://homelab-env/POSTGRES_PASSWORD/password"

# ❌ BAD - Hardcoded secret
password: "mySecretPassword123"
```

### Code Validation

| File Type  | Tool         | Checks                          |
| ---------- | ------------ | ------------------------------- |
| YAML       | yamllint     | Syntax, indentation, duplicates |
| Shell      | shellcheck   | Syntax errors, best practices   |
| Markdown   | markdownlint | Formatting, links, headers      |
| Dockerfile | hadolint     | Best practices, security        |

## Authentication & Authorization

### Password Policy

- **Minimum length**: 12 characters
- **Required**: Uppercase, lowercase, number, special character
- **Hashing**: Argon2id (industry standard)
- **Rotation**: Recommended every 90 days

### Two-Factor Authentication (2FA)

**Setup:**

1. Login to https://auth.rodneyops.com
2. Navigate to "Two-Factor Authentication"
3. Scan QR code with authenticator app
4. Enter verification code
5. Save backup codes securely

**Supported Apps:** Google Authenticator, Authy, 1Password, Bitwarden

### Session Management

- **Session duration**: 1 hour active, 5 min inactive
- **Remember me**: 30 days (optional)
- **Session storage**: SQLite (upgradeable to Redis)

## Network Security

### Network Segmentation

| Network    | Subnet        | Purpose                  | Access             |
| ---------- | ------------- | ------------------------ | ------------------ |
| Public     | 172.20.0.0/24 | Internet-facing services | Internet → Traefik |
| Private    | 172.21.0.0/24 | Internal services        | Tailscale only     |
| Monitoring | 172.22.0.0/24 | Observability stack      | Internal only      |
| Security   | 172.23.0.0/24 | Security services        | Internal only      |

### Firewall Rules

```bash
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp     # SSH
ufw allow 80/tcp     # HTTP
ufw allow 443/tcp    # HTTPS
ufw enable
```

### SSL/TLS Configuration

- **Provider**: Let's Encrypt (via Cloudflare DNS-01)
- **Protocol**: TLS 1.3 (minimum)
- **HSTS**: Enabled (2 years, includeSubDomains, preload)

## Monitoring & Incident Response

### Security Monitoring

**What's Monitored:**

- Failed login attempts (Authelia)
- Banned IPs (CrowdSec, Fail2ban)
- Unusual traffic patterns (Traefik)
- Container security events (Docker)

**Log Aggregation:**

- All logs → Loki
- Retention: 30 days
- Query via Grafana

### Incident Response

**In case of security incident:**

1. **Identify** - Check Grafana security dashboard
2. **Contain** - Block attacker via CrowdSec
3. **Investigate** - Review logs in Grafana/Loki
4. **Recover** - Restore from backup if needed
5. **Review** - Update security rules

## Security Best Practices

### For Administrators

1. Use strong, unique passwords for all services
2. Enable 2FA on all accounts
3. Regularly review access logs and security alerts
4. Keep systems updated (automated via GitHub Actions)
5. Rotate credentials every 90 days
6. Backup regularly (automated daily)

### Security Checklist

- [ ] All services behind Authelia 2FA
- [ ] Strong passwords (12+ characters)
- [ ] 2FA enabled for all admin users
- [ ] Firewall configured (only 22, 80, 443 exposed)
- [ ] CrowdSec connected and active
- [ ] Fail2ban jails active
- [ ] SSL certificates valid and auto-renewing
- [ ] Daily backups configured and tested
- [ ] Security scanning enabled (GitHub Actions)
- [ ] Audit logs enabled and monitored

---

**Last Updated**: January 2026  
**Next Review**: April 2026
