"""
SSH connection utilities
"""

import os
from pathlib import Path
from typing import Optional, List, Tuple

import paramiko


class SSHClient:
    """SSH client wrapper for remote operations"""

    def __init__(
        self,
        host: str,
        user: str,
        key_path: Optional[str] = None,
        password: Optional[str] = None,
        port: int = 22,
    ):
        """
        Initialize SSH client

        Args:
            host: SSH hostname or IP
            user: SSH username
            key_path: Path to SSH private key
            password: SSH password (if not using key)
            port: SSH port
        """
        self.host = host
        self.user = user
        self.port = port
        self.client: Optional[paramiko.SSHClient] = None

        # Resolve key path
        if key_path:
            key_path = Path(key_path).expanduser()
            if not key_path.exists():
                raise FileNotFoundError(f"SSH key not found: {key_path}")
            self.key_path = str(key_path)
        else:
            self.key_path = None

        self.password = password

    def connect(self) -> None:
        """Establish SSH connection"""
        if self.client and self.client.get_transport() and self.client.get_transport().is_active():
            return  # Already connected

        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            if self.key_path:
                # Use key-based authentication
                self.client.connect(
                    hostname=self.host,
                    username=self.user,
                    key_filename=self.key_path,
                    port=self.port,
                    timeout=10,
                )
            elif self.password:
                # Use password authentication
                self.client.connect(
                    hostname=self.host,
                    username=self.user,
                    password=self.password,
                    port=self.port,
                    timeout=10,
                )
            else:
                raise ValueError("Either key_path or password must be provided")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to {self.user}@{self.host}:{self.port}: {e}")

    def disconnect(self) -> None:
        """Close SSH connection"""
        if self.client:
            self.client.close()
            self.client = None

    def execute(self, command: str, sudo: bool = False) -> Tuple[int, str, str]:
        """
        Execute command on remote host

        Args:
            command: Command to execute
            sudo: Whether to run with sudo

        Returns:
            Tuple of (exit_code, stdout, stderr)
        """
        if not self.client:
            self.connect()

        if sudo:
            command = f"sudo {command}"

        stdin, stdout, stderr = self.client.exec_command(command)
        exit_code = stdout.channel.recv_exit_status()
        stdout_text = stdout.read().decode("utf-8")
        stderr_text = stderr.read().decode("utf-8")

        return exit_code, stdout_text, stderr_text

    def upload_file(self, local_path: str, remote_path: str) -> None:
        """
        Upload file to remote host

        Args:
            local_path: Local file path
            remote_path: Remote file path
        """
        if not self.client:
            self.connect()

        sftp = self.client.open_sftp()
        sftp.put(local_path, remote_path)
        sftp.close()

    def download_file(self, remote_path: str, local_path: str) -> None:
        """
        Download file from remote host

        Args:
            remote_path: Remote file path
            local_path: Local file path
        """
        if not self.client:
            self.connect()

        sftp = self.client.open_sftp()
        sftp.get(remote_path, local_path)
        sftp.close()

    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()
