"""
Borg-based restore module
Replaces scripts/restore.sh
"""

import os
from pathlib import Path
from typing import Optional, List, Dict, Any

from ..config import Config
from ..logging import setup_logging
from ..utils.borg import BorgClient


logger = setup_logging("restore")


class RestoreManager:
    """Manage Borg restores"""

    def __init__(self, config: Config):
        """
        Initialize restore manager

        Args:
            config: Configuration instance
        """
        self.config = config
        self.deploy_path = config.get("deploy_path", "/opt/homelab")

    def list(self, repository: str = "primary") -> List[Dict[str, Any]]:
        """
        List available archives

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

    def extract(
        self,
        archive_name: str,
        target_path: Optional[str] = None,
        repository: str = "primary",
        paths: Optional[List[str]] = None,
    ) -> bool:
        """
        Extract archive

        Args:
            archive_name: Archive name to extract
            target_path: Target directory (default: temporary directory)
            repository: Repository name
            paths: Specific paths to extract (None = all)

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

        if not target_path:
            # Use temporary directory
            import tempfile
            target_path = tempfile.mkdtemp(prefix="homelab-restore-")
            logger.info(f"Extracting to temporary directory: {target_path}")

        passphrase = os.getenv("BORG_PASSPHRASE")
        if not passphrase:
            logger.error("BORG_PASSPHRASE environment variable not set")
            return False

        borg = BorgClient(repo_url, passphrase)

        logger.info(f"Extracting archive '{archive_name}' to {target_path}")
        success = borg.extract(archive_name, target_path, paths)

        if success:
            logger.info(f"Archive extracted successfully to {target_path}")
            logger.info(f"Review contents and manually copy to {self.deploy_path} if needed")
        else:
            logger.error("Archive extraction failed")

        return success

    def verify(self, archive_name: str, repository: str = "primary") -> bool:
        """
        Verify archive integrity

        Args:
            archive_name: Archive name
            repository: Repository name

        Returns:
            True if archive is valid
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

        # List archives to verify the archive exists
        archives = borg.list()
        archive_exists = any(arch.get("name") == archive_name for arch in archives)

        if not archive_exists:
            logger.error(f"Archive '{archive_name}' not found in repository")
            return False

        # Verify repository integrity (includes all archives)
        return borg.check()

    def restore_systemd_files(
        self,
        archive_name: str,
        repository: str = "primary",
        dry_run: bool = False,
    ) -> bool:
        """
        Restore systemd files from backup to /etc/systemd/system/

        Args:
            archive_name: Archive name to restore from
            repository: Repository name
            dry_run: If True, only show what would be restored

        Returns:
            True if successful
        """
        import tempfile
        import shutil
        import subprocess

        # Extract systemd files to temporary directory
        temp_dir = tempfile.mkdtemp(prefix="homelab-systemd-restore-")
        systemd_path = Path(temp_dir) / "opt" / "homelab" / "systemd"

        logger.info(f"Extracting systemd files from archive '{archive_name}'...")
        success = self.extract(
            archive_name=archive_name,
            target_path=temp_dir,
            repository=repository,
            paths=["opt/homelab/systemd"],
        )

        if not success:
            logger.error("Failed to extract systemd files from archive")
            return False

        if not systemd_path.exists():
            logger.warning("No systemd directory found in backup")
            return False

        # Copy systemd files to /etc/systemd/system/
        systemd_target = Path("/etc/systemd/system")
        restored_files = []

        for systemd_file in systemd_path.glob("*"):
            if systemd_file.is_file():
                target_file = systemd_target / systemd_file.name

                if dry_run:
                    logger.info(f"Would restore: {systemd_file.name} -> {target_file}")
                    restored_files.append(systemd_file.name)
                else:
                    try:
                        # Copy file
                        shutil.copy2(systemd_file, target_file)
                        # Set permissions (root:root, 0644)
                        target_file.chmod(0o644)
                        import pwd
                        import grp
                        os.chown(target_file, pwd.getpwnam("root").pw_uid, grp.getgrnam("root").gr_gid)
                        restored_files.append(systemd_file.name)
                        logger.info(f"Restored: {systemd_file.name} -> {target_file}")
                    except Exception as e:
                        logger.error(f"Error restoring {systemd_file.name}: {e}")
                        return False

        if restored_files and not dry_run:
            # Reload systemd daemon
            try:
                subprocess.run(["systemctl", "daemon-reload"], check=True)
                logger.info("Reloaded systemd daemon")
            except Exception as e:
                logger.error(f"Error reloading systemd daemon: {e}")
                return False

        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)

        if restored_files:
            logger.info(f"Restored {len(restored_files)} systemd files")
            return True
        else:
            logger.warning("No systemd files to restore")
            return False
