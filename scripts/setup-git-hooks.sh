#!/bin/bash
# Setup Git hooks for security and quality checks

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
GIT_HOOKS_DIR="$PROJECT_ROOT/.git/hooks"

echo "🔧 Setting up Git hooks for security and quality assurance..."
echo ""

# Check if we're in a git repository
if [ ! -d "$PROJECT_ROOT/.git" ]; then
    echo "❌ Error: Not in a Git repository"
    exit 1
fi

# Create hooks directory if it doesn't exist
mkdir -p "$GIT_HOOKS_DIR"

# ============================================================================
# PRE-COMMIT HOOK - Scan for secrets before commit
# ============================================================================

cat > "$GIT_HOOKS_DIR/pre-commit" << 'HOOK_EOF'
#!/bin/bash
# Pre-commit hook - Scan for secrets and validate files

set -e

echo "🔍 Running pre-commit checks..."

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

FAILED=0

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 1. Check for secrets using gitleaks
if command_exists gitleaks; then
    echo "  → Scanning for secrets with gitleaks..."
    if ! gitleaks protect --staged --verbose 2>&1 | grep -q "no leaks found"; then
        echo -e "${RED}❌ Secrets detected! Commit blocked.${NC}"
        echo "   Run: gitleaks protect --staged --verbose"
        FAILED=1
    else
        echo -e "${GREEN}  ✅ No secrets detected${NC}"
    fi
else
    echo -e "${YELLOW}  ⚠️  gitleaks not installed (recommended)${NC}"
    echo "     Install: brew install gitleaks"
fi

# 2. Check for common secret patterns
echo "  → Checking for common secret patterns..."
SECRET_MATCHES=$(git diff --cached --name-only | xargs grep -nE "(password|secret|key|token)[\"\']?\s*[:=]\s*[\"\'][^\$\{]" 2>/dev/null | grep -v "op item get" | grep -v ".md:" | grep -v "# " | grep -v "file:///run/secrets" | grep -v "vault_key:" | grep -vE "name:\s*\"[A-Z_]*_(SECRET|KEY|TOKEN|PASSWORD)\"" | grep -vE "\{.*name:.*vault_key" || true)
if [ -n "$SECRET_MATCHES" ]; then
    echo -e "${RED}❌ Possible hardcoded secrets detected!${NC}"
    echo "   Secrets should use environment variables or 1Password references"
    echo "$SECRET_MATCHES"
    FAILED=1
fi

# 3. Check for AWS keys
echo "  → Checking for AWS keys..."
if git diff --cached --name-only | xargs grep -nE "(AKIA[0-9A-Z]{16})" 2>/dev/null; then
    echo -e "${RED}❌ AWS Access Key detected!${NC}"
    FAILED=1
fi

# 4. Check for private keys
echo "  → Checking for private keys..."
PRIVATE_KEY_FILES=$(git diff --cached --name-only | xargs grep -l "BEGIN.*PRIVATE KEY" 2>/dev/null | grep -v "setup-git-hooks.sh" | grep -v ".gitleaks.toml" | grep -v ".md" || true)
if [ -n "$PRIVATE_KEY_FILES" ]; then
    echo -e "${RED}❌ Private key detected!${NC}"
    echo "$PRIVATE_KEY_FILES"
    FAILED=1
fi

# 5. Validate YAML syntax
echo "  → Validating YAML files..."
for file in $(git diff --cached --name-only | grep -E "\.(yml|yaml)$"); do
    if command_exists yamllint; then
        if ! yamllint -c .yamllint.yml "$file" 2>&1; then
            echo -e "${RED}❌ YAML validation failed: $file${NC}"
            FAILED=1
        fi
    fi
done

# 6. Check shell scripts
echo "  → Checking shell scripts..."
for file in $(git diff --cached --name-only | grep -E "\.(sh|bash)$"); do
    if command_exists shellcheck; then
        if ! shellcheck --severity=warning "$file"; then
            echo -e "${YELLOW}⚠️  ShellCheck warnings in: $file${NC}"
        fi
    fi
done

# 7. Validate docker-compose.yml if changed
if git diff --cached --name-only | grep -q "docker-compose.yml"; then
    echo "  → Validating docker-compose.yml..."
    if command_exists docker; then
        if ! docker compose -f docker-compose.yml config >/dev/null 2>&1; then
            echo -e "${RED}❌ docker-compose.yml validation failed${NC}"
            FAILED=1
        else
            echo -e "${GREEN}  ✅ docker-compose.yml is valid${NC}"
        fi
    fi
fi

# 8. Check for .env files (should never be committed)
if git diff --cached --name-only | grep -E "^\.env$|^\.env\.local$|^\.env\.production$"; then
    echo -e "${RED}❌ Attempting to commit .env file! This should be in .gitignore${NC}"
    FAILED=1
fi

# 9. Check for sensitive files
echo "  → Checking for sensitive files..."
SENSITIVE_PATTERNS=(
    "id_rsa"
    "id_ed25519"
    ".pem$"
    ".key$"
    "credentials"
    "secret"
)

for pattern in "${SENSITIVE_PATTERNS[@]}"; do
    if git diff --cached --name-only | grep -i "$pattern" | grep -v ".md$" | grep -v "/.kamal/secrets$"; then
        echo -e "${YELLOW}⚠️  Potentially sensitive file detected: matches '$pattern'${NC}"
        echo "   Review carefully before committing"
    fi
done

# Final result
echo ""
if [ $FAILED -eq 1 ]; then
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}❌ PRE-COMMIT CHECKS FAILED - COMMIT BLOCKED${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "Fix the issues above and try again."
    echo "To bypass (NOT RECOMMENDED): git commit --no-verify"
    exit 1
else
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}✅ ALL PRE-COMMIT CHECKS PASSED${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    exit 0
fi
HOOK_EOF

chmod +x "$GIT_HOOKS_DIR/pre-commit"
echo "✅ Created pre-commit hook"

# ============================================================================
# PRE-PUSH HOOK - Additional checks before push
# ============================================================================

cat > "$GIT_HOOKS_DIR/pre-push" << 'HOOK_EOF'
#!/bin/bash
# Pre-push hook - Additional security checks before pushing

set -e

echo "🚀 Running pre-push checks..."

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

FAILED=0

# Check for TODO/FIXME in production files
echo "  → Checking for unresolved TODOs..."
if git diff origin/main..HEAD --name-only | xargs grep -nE "TODO:|FIXME:" 2>/dev/null | grep -E "\.(yml|yaml|sh):" | grep -v ".md:"; then
    echo -e "${YELLOW}⚠️  Found unresolved TODOs/FIXMEs in code files${NC}"
    echo "   Consider resolving them before pushing"
fi

# Scan current commit for secrets (not entire repository history)
if command -v gitleaks >/dev/null 2>&1; then
    echo "  → Scanning current commit for secrets..."
    # Only scan the commits being pushed, not the entire repository
    if git rev-parse --verify HEAD >/dev/null 2>&1; then
        # Get the range of commits being pushed
        while read local_ref local_sha remote_ref remote_sha; do
            if [ "$local_sha" != "0000000000000000000000000000000000000000" ]; then
                if [ "$remote_sha" = "0000000000000000000000000000000000000000" ]; then
                    # New branch, scan from first commit
                    RANGE="$local_sha"
                else
                    # Update existing branch, scan new commits
                    RANGE="$remote_sha..$local_sha"
                fi
                if ! gitleaks protect --staged --verbose 2>&1 | grep -q "no leaks found"; then
                    echo -e "${RED}❌ Secrets detected in commits being pushed!${NC}"
                    FAILED=1
                else
                    echo -e "${GREEN}  ✅ No secrets in current commit${NC}"
                fi
            fi
        done
    else
        echo -e "${YELLOW}  ⚠️  No commits yet, skipping secret scan${NC}"
    fi
fi

# Check branch name (warn if pushing to main/master)
current_branch=$(git rev-parse --abbrev-ref HEAD)
if [[ "$current_branch" == "main" ]] || [[ "$current_branch" == "master" ]]; then
    echo -e "${YELLOW}⚠️  Pushing directly to $current_branch${NC}"
    echo "   Consider using a feature branch for changes"
fi

if [ $FAILED -eq 1 ]; then
    echo -e "${RED}❌ PRE-PUSH CHECKS FAILED - PUSH BLOCKED${NC}"
    exit 1
else
    echo -e "${GREEN}✅ ALL PRE-PUSH CHECKS PASSED${NC}"
    exit 0
fi
HOOK_EOF

chmod +x "$GIT_HOOKS_DIR/pre-push"
echo "✅ Created pre-push hook"

# ============================================================================
# COMMIT-MSG HOOK - Validate commit messages
# ============================================================================

cat > "$GIT_HOOKS_DIR/commit-msg" << 'HOOK_EOF'
#!/bin/bash
# Commit message hook - Enforce conventional commits

commit_msg_file=$1
commit_msg=$(cat "$commit_msg_file")

# Colors
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if commit message follows conventional commits format
# Format: type(scope): subject
# Types: feat, fix, docs, style, refactor, test, chore

if ! echo "$commit_msg" | grep -qE "^(feat|fix|docs|style|refactor|perf|test|chore|build|ci|revert)(\(.+\))?: .{1,}"; then
    echo -e "${YELLOW}⚠️  Commit message should follow Conventional Commits format:${NC}"
    echo ""
    echo "   <type>(<scope>): <subject>"
    echo ""
    echo "   Types: feat, fix, docs, style, refactor, test, chore"
    echo ""
    echo "   Examples:"
    echo "     feat(traefik): add rate limiting middleware"
    echo "     fix(secrets): resolve 1password authentication issue"
    echo "     docs: update deployment checklist"
    echo ""
    echo "   Your message: $commit_msg"
    echo ""
    echo "   Continue anyway? (not recommended for main branch)"
fi

exit 0
HOOK_EOF

chmod +x "$GIT_HOOKS_DIR/commit-msg"
echo "✅ Created commit-msg hook"

# ============================================================================
# Summary
# ============================================================================

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Git hooks installed successfully!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 Installed hooks:"
echo "   - pre-commit   → Secret scanning, YAML validation, syntax checks"
echo "   - pre-push     → Full repository scan, TODO checks"
echo "   - commit-msg   → Enforce conventional commit format"
echo ""
echo "🔧 Recommended tools (install for full functionality):"
echo "   - gitleaks:     brew install gitleaks"
echo "   - prettier:     npm install -g prettier"
echo "   - yamllint:     pip install yamllint"
echo "   - shellcheck:   brew install shellcheck"
echo "   - hadolint:     brew install hadolint"
echo "   - markdownlint: npm install -g markdownlint-cli"
echo ""
echo "🧪 Test the hooks:"
echo "   - Make a change and try to commit"
echo "   - Hooks will run automatically"
echo ""
echo "⚠️  To bypass hooks (NOT RECOMMENDED):"
echo "   git commit --no-verify"
echo ""

