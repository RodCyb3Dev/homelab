"""
Git hooks module
Replaces scripts/setup-git-hooks.sh
"""

import os
import subprocess
from pathlib import Path
from typing import List, Optional

from ..config import Config
from ..logging import setup_logging


logger = setup_logging("git_hooks")


class GitHooksManager:
    """Manage Git hooks"""

    def __init__(self, config: Optional[Config] = None):
        """
        Initialize Git hooks manager

        Args:
            config: Configuration instance (optional)
        """
        self.config = config
        self.project_root = self._find_git_root()
        self.hooks_dir = self.project_root / ".git" / "hooks" if self.project_root else None

    def _find_git_root(self) -> Optional[Path]:
        """Find Git repository root"""
        current = Path.cwd()
        while current != current.parent:
            if (current / ".git").exists():
                return current
            current = current.parent
        return None

    def install(self) -> bool:
        """
        Install Git hooks

        Returns:
            True if successful
        """
        if not self.hooks_dir:
            logger.error("Not in a Git repository")
            return False

        self.hooks_dir.mkdir(parents=True, exist_ok=True)

        # Install pre-commit hook
        pre_commit_path = self.hooks_dir / "pre-commit"
        pre_commit_content = self._generate_pre_commit_hook()
        pre_commit_path.write_text(pre_commit_content)
        pre_commit_path.chmod(0o755)

        # Install pre-push hook
        pre_push_path = self.hooks_dir / "pre-push"
        pre_push_content = self._generate_pre_push_hook()
        pre_push_path.write_text(pre_push_content)
        pre_push_path.chmod(0o755)

        logger.info("Git hooks installed successfully")
        return True

    def uninstall(self) -> bool:
        """
        Remove Git hooks

        Returns:
            True if successful
        """
        if not self.hooks_dir:
            logger.error("Not in a Git repository")
            return False

        hooks = ["pre-commit", "pre-push"]
        for hook in hooks:
            hook_path = self.hooks_dir / hook
            if hook_path.exists():
                hook_path.unlink()
                logger.info(f"Removed {hook} hook")

        return True

    def _generate_pre_commit_hook(self) -> str:
        """Generate pre-commit hook script"""
        return """#!/usr/bin/env python3
import sys
import subprocess
from pathlib import Path

# Add homelab_tools to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from homelab_tools.modules.git_hooks import run_pre_commit_checks

if __name__ == "__main__":
    success = run_pre_commit_checks()
    sys.exit(0 if success else 1)
"""

    def _generate_pre_push_hook(self) -> str:
        """Generate pre-push hook script"""
        return """#!/usr/bin/env python3
import sys
import subprocess
from pathlib import Path

# Add homelab_tools to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from homelab_tools.modules.git_hooks import run_pre_push_checks

if __name__ == "__main__":
    success = run_pre_push_checks()
    sys.exit(0 if success else 1)
"""

    def test(self) -> bool:
        """
        Test Git hooks locally

        Returns:
            True if all checks pass
        """
        logger.info("Testing pre-commit checks...")
        pre_commit_ok = self._run_pre_commit_checks()

        logger.info("Testing pre-push checks...")
        pre_push_ok = self._run_pre_push_checks()

        return pre_commit_ok and pre_push_ok

    def _run_pre_commit_checks(self) -> bool:
        """Run pre-commit checks"""
        checks = [
            ("gitleaks", ["gitleaks", "protect", "--staged", "--verbose"]),
            ("yamllint", ["yamllint", ".github/workflows/", "ansible/"]),
            ("shellcheck", ["shellcheck", "scripts/*.sh"]),
        ]

        all_passed = True
        for name, command in checks:
            if not self._command_exists(command[0]):
                logger.warning(f"{name} not found, skipping")
                continue

            logger.info(f"Running {name}...")
            try:
                result = subprocess.run(command, capture_output=True, text=True, check=False)
                if result.returncode != 0:
                    logger.error(f"{name} failed:")
                    logger.error(result.stderr)
                    all_passed = False
                else:
                    logger.info(f"{name} passed")
            except Exception as e:
                logger.error(f"Error running {name}: {e}")
                all_passed = False

        return all_passed

    def _run_pre_push_checks(self) -> bool:
        """Run pre-push checks"""
        checks = [
            ("gitleaks", ["gitleaks", "protect", "--staged", "--verbose"]),
            ("TODO check", self._check_todos),
        ]

        all_passed = True
        for name, check in checks:
            if callable(check):
                logger.info(f"Running {name}...")
                if not check():
                    all_passed = False
            else:
                if not self._command_exists(check[0]):
                    logger.warning(f"{name} not found, skipping")
                    continue

                logger.info(f"Running {name}...")
                try:
                    result = subprocess.run(check, capture_output=True, text=True, check=False)
                    if result.returncode != 0:
                        logger.error(f"{name} failed")
                        all_passed = False
                except Exception as e:
                    logger.error(f"Error running {name}: {e}")
                    all_passed = False

        return all_passed

    def _check_todos(self) -> bool:
        """Check for unresolved TODOs"""
        if not self.project_root:
            return True

        # Check staged files for TODOs
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True,
            text=True,
            check=True,
        )

        staged_files = result.stdout.strip().split("\n")
        todos_found = []

        for file_path in staged_files:
            if not file_path:
                continue

            full_path = self.project_root / file_path
            if not full_path.exists():
                continue

            try:
                content = full_path.read_text()
                if "TODO" in content or "FIXME" in content:
                    todos_found.append(file_path)
            except Exception:
                pass

        if todos_found:
            logger.warning(f"Found TODOs/FIXMEs in staged files: {', '.join(todos_found)}")
            return False

        return True

    def _command_exists(self, command: str) -> bool:
        """Check if command exists"""
        try:
            subprocess.run(["which", command], capture_output=True, check=True)
            return True
        except Exception:
            return False


def run_pre_commit_checks() -> bool:
    """Run pre-commit checks (called by hook)"""
    manager = GitHooksManager()
    return manager._run_pre_commit_checks()


def run_pre_push_checks() -> bool:
    """Run pre-push checks (called by hook)"""
    manager = GitHooksManager()
    return manager._run_pre_push_checks()
