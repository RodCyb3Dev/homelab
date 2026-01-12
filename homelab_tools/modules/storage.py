"""
Storage Box management module
Consolidates all storage box mounting and setup scripts
"""

import os
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any

from ..config import Config
from ..logging import setup_logging
from ..utils.ssh import SSHClient


logger = setup_logging("storage")


class StorageBoxManager:
    """Manage Hetzner Storage Box mounts"""

    def __init__(self, config: Config):
        """
        Initialize Storage Box manager

        Args:
            config: Configuration instance
        """
        self.config = config
        self.storage_boxes = config.get("storage_boxes", {})

    def mount(
        self,
        box: str = "main",
        method: str = "webdav",
        credentials: Optional[Dict[str, str]] = None,
    ) -> bool:
        """
        Mount Storage Box

        Args:
            box: Box name (main, immich)
            method: Mount method (webdav, ssh)
            credentials: Optional credentials dict with 'user' and 'password'

        Returns:
            True if successful
        """
        box_config = self.storage_boxes.get(box)
        if not box_config:
            logger.error(f"Storage box '{box}' not found in configuration")
            return False

        host = box_config["host"]
        user = credentials.get("user") if credentials else box_config["user"]
        password = credentials.get("password") if credentials else None
        mount_point = box_config["mount_point"]

        logger.info(f"Mounting {box} Storage Box ({host}) to {mount_point}")

        # Ensure mount point exists
        Path(mount_point).mkdir(parents=True, exist_ok=True)

        if method == "webdav":
            return self._mount_webdav(host, user, password, mount_point)
        elif method == "ssh":
            return self._mount_ssh(host, user, password, mount_point)
        else:
            logger.error(f"Unknown mount method: {method}")
            return False

    def _mount_webdav(
        self, host: str, user: str, password: Optional[str], mount_point: str
    ) -> bool:
        """Mount via WebDAV"""
        try:
            # Configure davfs2 secrets
            secrets_file = Path("/etc/davfs2/secrets")
            secrets_file.parent.mkdir(parents=True, exist_ok=True)

            # Add or update credentials
            url = f"https://{host}"
            secrets_content = secrets_file.read_text() if secrets_file.exists() else ""

            # Remove existing entry for this host
            lines = [
                line
                for line in secrets_content.split("\n")
                if not line.startswith(url)
            ]

            # Add new entry
            if password:
                lines.append(f"{url} {user} {password}")

            secrets_file.write_text("\n".join(lines) + "\n")
            secrets_file.chmod(0o600)

            # Mount
            result = subprocess.run(
                [
                    "mount",
                    "-t",
                    "davfs",
                    url,
                    mount_point,
                    "-o",
                    "uid=1000,gid=1000,file_mode=0770,dir_mode=0770,noexec,nosuid,nodev,_netdev",
                ],
                check=False,
            )

            if result.returncode == 0:
                logger.info(f"Successfully mounted {host} to {mount_point}")
                return True
            else:
                logger.error(f"Failed to mount {host}: exit code {result.returncode}")
                return False

        except Exception as e:
            logger.error(f"Error mounting WebDAV: {e}")
            return False

    def _mount_ssh(
        self, host: str, user: str, password: Optional[str], mount_point: str
    ) -> bool:
        """Mount via SSH (SSHFS)"""
        try:
            # SSHFS mount
            sshfs_cmd = ["sshfs", f"{user}@{host}:/", mount_point, "-p", "23"]

            if password:
                # Use sshpass if password provided
                sshfs_cmd = ["sshpass", "-p", password] + sshfs_cmd

            result = subprocess.run(
                sshfs_cmd + ["-o", "uid=1000,gid=1000,allow_other"],
                check=False,
            )

            if result.returncode == 0:
                logger.info(f"Successfully mounted {host} via SSH to {mount_point}")
                return True
            else:
                logger.error(f"Failed to mount {host} via SSH: exit code {result.returncode}")
                return False

        except Exception as e:
            logger.error(f"Error mounting SSH: {e}")
            return False

    def unmount(self, box: str = "main") -> bool:
        """
        Unmount Storage Box

        Args:
            box: Box name (main, immich)

        Returns:
            True if successful
        """
        box_config = self.storage_boxes.get(box)
        if not box_config:
            logger.error(f"Storage box '{box}' not found in configuration")
            return False

        mount_point = box_config["mount_point"]

        try:
            result = subprocess.run(["umount", mount_point], check=False)
            if result.returncode == 0:
                logger.info(f"Successfully unmounted {mount_point}")
                return True
            else:
                logger.warning(f"Unmount failed (may not be mounted): {mount_point}")
                return False
        except Exception as e:
            logger.error(f"Error unmounting: {e}")
            return False

    def status(self, box: Optional[str] = None) -> Dict[str, Any]:
        """
        Get mount status

        Args:
            box: Box name (None = all boxes)

        Returns:
            Dictionary with status information
        """
        boxes_to_check = [box] if box else list(self.storage_boxes.keys())
        status = {}

        for box_name in boxes_to_check:
            box_config = self.storage_boxes.get(box_name)
            if not box_config:
                continue

            mount_point = box_config["mount_point"]
            is_mounted = self._is_mounted(mount_point)

            status[box_name] = {
                "host": box_config["host"],
                "mount_point": mount_point,
                "mounted": is_mounted,
            }

            if is_mounted:
                # Get disk usage
                try:
                    result = subprocess.run(
                        ["df", "-h", mount_point],
                        capture_output=True,
                        text=True,
                        check=True,
                    )
                    lines = result.stdout.strip().split("\n")
                    if len(lines) > 1:
                        parts = lines[1].split()
                        status[box_name]["usage"] = {
                            "size": parts[1],
                            "used": parts[2],
                            "available": parts[3],
                            "percent": parts[4],
                        }
                except Exception:
                    pass

        return status

    def _is_mounted(self, mount_point: str) -> bool:
        """Check if mount point is mounted"""
        try:
            result = subprocess.run(
                ["mountpoint", "-q", mount_point],
                check=False,
            )
            return result.returncode == 0
        except Exception:
            return False

    def setup_systemd(
        self, box: str = "main", method: str = "webdav"
    ) -> bool:
        """
        Generate systemd mount and automount units

        Args:
            box: Box name
            method: Mount method (webdav, ssh)

        Returns:
            True if successful
        """
        box_config = self.storage_boxes.get(box)
        if not box_config:
            logger.error(f"Storage box '{box}' not found in configuration")
            return False

        host = box_config["host"]
        mount_point = box_config["mount_point"]
        unit_name = mount_point.replace("/", "-").replace("mnt-", "mnt-")

        # Generate mount unit
        mount_unit = f"""[Unit]
Description=Hetzner Storage Box {box} Mount
Documentation=https://docs.hetzner.com/storage/storage-box/
After=network-online.target
Wants=network-online.target

[Mount]
What=https://{host}
Where={mount_point}
Type=davfs
Options=uid=1000,gid=1000,file_mode=0770,dir_mode=0770,noexec,nosuid,nodev,_netdev

[Install]
WantedBy=multi-user.target
"""

        # Generate automount unit
        automount_unit = f"""[Unit]
Description=Hetzner Storage Box {box} Automount
Documentation=https://docs.hetzner.com/storage/storage-box/
After=network-online.target
Wants=network-online.target

[Automount]
Where={mount_point}
TimeoutIdleSec=300

[Install]
WantedBy=multi-user.target
"""

        # Write units
        systemd_dir = Path("/etc/systemd/system")
        mount_unit_path = systemd_dir / f"{unit_name}.mount"
        automount_unit_path = systemd_dir / f"{unit_name}.automount"

        try:
            mount_unit_path.write_text(mount_unit)
            automount_unit_path.write_text(automount_unit)

            # Reload systemd
            subprocess.run(["systemctl", "daemon-reload"], check=True)

            # Enable automount
            subprocess.run(
                ["systemctl", "enable", f"{unit_name}.automount"],
                check=True,
            )

            logger.info(f"Generated systemd units for {box} Storage Box")
            return True

        except Exception as e:
            logger.error(f"Error generating systemd units: {e}")
            return False

    def sync_systemd_files(self) -> bool:
        """
        Sync systemd files from /etc/systemd/system/ to /opt/homelab/systemd/
        Only syncs files that exist in the project's systemd/ directory (version controlled in git)
        This ensures we only backup our project's systemd files, not all system files

        Returns:
            True if successful
        """
        deploy_path = Path(self.config.get("deploy_path", "/opt/homelab"))
        systemd_source = Path("/etc/systemd/system")
        systemd_target = deploy_path / "systemd"

        try:
            # Get list of systemd files from our project's systemd/ directory
            # The systemd/ directory is in the git repo and should be deployed to /opt/homelab/systemd/
            # We only sync files that are part of our project (exist in the repo's systemd/ directory)
            
            if not systemd_target.exists():
                logger.warning(f"Project systemd directory not found: {systemd_target}")
                logger.info("This directory should exist from the git repo deployment")
                return False

            # Get list of systemd files from our project's systemd/ directory (version controlled)
            project_files = [f.name for f in systemd_target.glob("*") if f.is_file()]
            
            if not project_files:
                logger.warning("No systemd files found in project systemd directory")
                logger.info(f"Expected files in: {systemd_target}")
                return False

            logger.info(f"Found {len(project_files)} systemd files in project: {', '.join(project_files)}")

            # Sync only files that exist in both /etc/systemd/system/ and our project
            copied_files = []
            for filename in project_files:
                source_file = systemd_source / filename
                if source_file.exists() and source_file.is_file() and not source_file.is_symlink():
                    target_file = systemd_target / filename
                    # Copy file (overwrite the repo version with the deployed version)
                    import shutil
                    shutil.copy2(source_file, target_file)
                    # Set permissions (readable by deploy user)
                    target_file.chmod(0o644)
                    copied_files.append(filename)
                    logger.info(f"Synced {filename} from /etc/systemd/system/ to {systemd_target}")
                else:
                    logger.debug(f"Skipping {filename} (not found in /etc/systemd/system/ or is symlink)")

            if copied_files:
                logger.info(f"Synced {len(copied_files)} systemd files to {systemd_target}")
                return True
            else:
                logger.warning("No systemd files found to sync from /etc/systemd/system/")
                return False

        except Exception as e:
            logger.error(f"Error syncing systemd files: {e}")
            return False
