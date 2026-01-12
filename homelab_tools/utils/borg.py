"""
Borg backup wrapper utilities
"""

import subprocess
from pathlib import Path
from typing import List, Optional, Dict, Any


class BorgClient:
    """Borg backup client wrapper"""

    def __init__(self, repository: str, passphrase: Optional[str] = None):
        """
        Initialize Borg client

        Args:
            repository: Borg repository path (e.g., ssh://user@host:23/./backups/repo)
            passphrase: Repository passphrase (if not set, will use BORG_PASSPHRASE env var)
        """
        self.repository = repository
        self.passphrase = passphrase

    def _run_command(
        self, command: List[str], env: Optional[Dict[str, str]] = None
    ) -> tuple:
        """
        Run borg command

        Args:
            command: Command arguments
            env: Environment variables

        Returns:
            Tuple of (exit_code, stdout, stderr)
        """
        env_dict = dict(env) if env else {}
        if self.passphrase:
            env_dict["BORG_PASSPHRASE"] = self.passphrase

        try:
            result = subprocess.run(
                ["borg"] + command,
                capture_output=True,
                text=True,
                env=env_dict,
                check=False,
            )
            return result.returncode, result.stdout, result.stderr
        except FileNotFoundError:
            raise RuntimeError("Borg backup is not installed. Install with: apt install borgbackup")

    def init(self, encryption: str = "repokey") -> bool:
        """
        Initialize Borg repository

        Args:
            encryption: Encryption type (repokey, keyfile, etc.)

        Returns:
            True if successful
        """
        exit_code, stdout, stderr = self._run_command(
            ["init", "--encryption", encryption, self.repository]
        )
        return exit_code == 0

    def create(
        self,
        archive_name: str,
        paths: List[str],
        exclude: Optional[List[str]] = None,
        compression: str = "lz4",
    ) -> bool:
        """
        Create backup archive

        Args:
            archive_name: Archive name (e.g., "2024-01-15")
            paths: Paths to backup
            exclude: Paths to exclude
            compression: Compression algorithm

        Returns:
            True if successful
        """
        command = ["create", f"{self.repository}::{archive_name}"]
        command.extend(["--compression", compression])

        if exclude:
            for pattern in exclude:
                command.extend(["--exclude", pattern])

        command.extend(paths)

        exit_code, stdout, stderr = self._run_command(command)
        return exit_code == 0

    def list(self) -> List[Dict[str, Any]]:
        """
        List archives in repository

        Returns:
            List of archive dictionaries
        """
        exit_code, stdout, stderr = self._run_command(["list", "--json", self.repository])
        if exit_code != 0:
            return []

        import json
        try:
            archives = json.loads(stdout)
            return archives.get("archives", [])
        except json.JSONDecodeError:
            return []

    def prune(
        self,
        keep_daily: int = 14,
        keep_weekly: int = 12,
        keep_monthly: int = 24,
    ) -> bool:
        """
        Prune old archives

        Args:
            keep_daily: Keep daily backups for N days
            keep_weekly: Keep weekly backups for N weeks
            keep_monthly: Keep monthly backups for N months

        Returns:
            True if successful
        """
        command = [
            "prune",
            "--keep-daily", str(keep_daily),
            "--keep-weekly", str(keep_weekly),
            "--keep-monthly", str(keep_monthly),
            "--verbose",
            self.repository,
        ]

        exit_code, stdout, stderr = self._run_command(command)
        return exit_code == 0

    def compact(self) -> bool:
        """
        Compact repository to free space

        Returns:
            True if successful
        """
        exit_code, stdout, stderr = self._run_command(["compact", self.repository])
        return exit_code == 0

    def extract(
        self, archive_name: str, target_path: str, paths: Optional[List[str]] = None
    ) -> bool:
        """
        Extract archive

        Args:
            archive_name: Archive name to extract
            target_path: Target directory
            paths: Specific paths to extract (None = all)

        Returns:
            True if successful
        """
        command = ["extract", f"{self.repository}::{archive_name}"]
        if paths:
            command.extend(paths)

        # Change to target directory
        import os
        original_cwd = os.getcwd()
        try:
            Path(target_path).mkdir(parents=True, exist_ok=True)
            os.chdir(target_path)
            exit_code, stdout, stderr = self._run_command(command)
            return exit_code == 0
        finally:
            os.chdir(original_cwd)

    def check(self) -> bool:
        """
        Verify repository integrity

        Returns:
            True if repository is valid
        """
        exit_code, stdout, stderr = self._run_command(["check", "--verify-data", self.repository])
        return exit_code == 0
