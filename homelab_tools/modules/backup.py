"""
Borg-based backup module
Replaces scripts/backup.sh
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

from ..config import Config
from ..logging import setup_logging
from ..utils.borg import BorgClient


logger = setup_logging("backup")


class BackupManager:
    """Manage Borg backups"""

    def __init__(self, config: Config):
        """
        Initialize backup manager

        Args:
            config: Configuration instance
        """
        self.config = config
        self.deploy_path = config.get("deploy_path", "/opt/homelab")

    def create(
        self,
        backup_type: str = "full",
        repository: str = "primary",
        passphrase: Optional[str] = None,
    ) -> bool:
        """
        Create backup

        Args:
            backup_type: Backup type (full, config, database)
            repository: Repository name (primary, secondary)
            passphrase: Repository passphrase

        Returns:
            True if successful
        """
        repo_config = self.config.get(f"backup.{repository}")
        if not repo_config:
            logger.error(f"Backup repository '{repository}' not found in configuration")
            return False

        repo_url = repo_config.get("repository")
        if not repo_url:
            logger.error(f"Repository URL not configured for '{repository}'")
            return False

        if not passphrase:
            passphrase = os.getenv("BORG_PASSPHRASE")
            if not passphrase:
                logger.error("Borg passphrase not provided (set BORG_PASSPHRASE env var)")
                return False

        # Initialize Borg client
        borg = BorgClient(repo_url, passphrase)

        # Determine paths to backup
        paths = self._get_backup_paths(backup_type)
        if not paths:
            logger.error(f"No paths to backup for type '{backup_type}'")
            return False

        # Create archive name
        archive_name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        logger.info(f"Creating {backup_type} backup: {archive_name}")

        # Exclude patterns (relative to backup paths)
        # Exclude logs, temporary files, Python cache, git, venv
        # Note: /dev, /proc, /sys, /tmp, /run, /media, /mnt are system directories
        # that won't be in /opt/homelab, so we don't need to exclude them
        # Also exclude Python tools if they somehow end up in the backup path
        exclude = [
            "*.log",
            "*.db-shm",
            "*.db-wal",
            "*.tmp",
            "__pycache__",
            ".git",
            ".venv",
            "venv",
            "*.pyc",
            "*.pyo",
            "homelab_tools",  # Exclude Python tools directory if present
            "homelab_tools.egg-info",  # Exclude build artifacts
            "*.egg-info",
        ]

        # Create backup
        success = borg.create(archive_name, paths, exclude=exclude)

        if success:
            logger.info(f"Backup created successfully: {archive_name}")

            # Prune old backups
            logger.info("Pruning old backups...")
            borg.prune(keep_daily=14, keep_weekly=12, keep_monthly=24)

            # Compact repository
            logger.info("Compacting repository...")
            borg.compact()

            return True
        else:
            logger.error("Backup creation failed")
            return False

    def _get_backup_paths(self, backup_type: str) -> List[str]:
        """
        Get paths to backup based on type

        Args:
            backup_type: Backup type (full, config, database)

        Returns:
            List of paths to backup
        """
        paths = []

        if backup_type in ["full", "config"]:
            # Backup entire /opt/homelab directory (simpler approach)
            # This includes: Caddyfile, config/, docker-compose files, .env, systemd/
            deploy_path = Path(self.deploy_path)
            if deploy_path.exists():
                paths.append(str(deploy_path))

        if backup_type in ["full", "database"]:
            # Database backups (if they exist)
            # Note: Databases should be backed up separately via service-specific backup scripts
            pass

        return paths

    def list(self, repository: str = "primary") -> List[Dict[str, Any]]:
        """
        List backups in repository

        Args:
            repository: Repository name (primary, secondary)

        Returns:
            List of archive dictionaries
        """
        repo_config = self.config.get(f"backup.{repository}")
        if not repo_config:
            logger.error(f"Backup repository '{repository}' not found")
            return []

        repo_url = repo_config.get("repository")
        if not repo_url:
            logger.error(f"Repository URL not configured")
            return []

        passphrase = os.getenv("BORG_PASSPHRASE")
        borg = BorgClient(repo_url, passphrase)
        return borg.list()

    def prune(
        self,
        repository: str = "primary",
        keep_daily: int = 14,
        keep_weekly: int = 12,
        keep_monthly: int = 24,
    ) -> bool:
        """
        Prune old backups

        Args:
            repository: Repository name
            keep_daily: Keep daily backups for N days
            keep_weekly: Keep weekly backups for N weeks
            keep_monthly: Keep monthly backups for N months

        Returns:
            True if successful
        """
        repo_config = self.config.get(f"backup.{repository}")
        if not repo_config:
            logger.error(f"Backup repository '{repository}' not found")
            return False

        repo_url = repo_config.get("repository")
        if not repo_url:
            logger.error(f"Repository URL not configured")
            return False

        passphrase = os.getenv("BORG_PASSPHRASE")
        borg = BorgClient(repo_url, passphrase)
        return borg.prune(keep_daily, keep_weekly, keep_monthly)

    def verify(self, repository: str = "primary") -> bool:
        """
        Verify repository integrity

        Args:
            repository: Repository name

        Returns:
            True if repository is valid
        """
        repo_config = self.config.get(f"backup.{repository}")
        if not repo_config:
            logger.error(f"Backup repository '{repository}' not found")
            return False

        repo_url = repo_config.get("repository")
        if not repo_url:
            logger.error(f"Repository URL not configured")
            return False

        passphrase = os.getenv("BORG_PASSPHRASE")
        borg = BorgClient(repo_url, passphrase)
        return borg.check()
