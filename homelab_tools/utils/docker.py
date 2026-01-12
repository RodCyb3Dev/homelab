"""
Docker API utilities
"""

from pathlib import Path
from typing import Dict, List, Optional, Any

import docker


class DockerClient:
    """Docker client wrapper"""

    def __init__(self, base_url: Optional[str] = None):
        """
        Initialize Docker client

        Args:
            base_url: Docker daemon URL (default: unix://var/run/docker.sock)
        """
        if base_url is None:
            # Try to detect Docker socket
            if Path("/var/run/docker.sock").exists():
                base_url = "unix://var/run/docker.sock"
            else:
                base_url = "unix://var/run/docker.sock"  # Default

        try:
            self.client = docker.DockerClient(base_url=base_url)
            self.client.ping()  # Test connection
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Docker daemon: {e}")

    def get_container(self, name: str) -> Optional[docker.models.containers.Container]:
        """Get container by name"""
        try:
            return self.client.containers.get(name)
        except docker.errors.NotFound:
            return None

    def is_container_running(self, name: str) -> bool:
        """Check if container is running"""
        container = self.get_container(name)
        return container is not None and container.status == "running"

    def get_container_health(self, name: str) -> Optional[str]:
        """Get container health status"""
        container = self.get_container(name)
        if container:
            return container.attrs.get("State", {}).get("Health", {}).get("Status")
        return None

    def get_container_stats(self, name: str) -> Optional[Dict[str, Any]]:
        """Get container statistics"""
        container = self.get_container(name)
        if container:
            try:
                stats = container.stats(stream=False)
                return stats
            except Exception:
                return None
        return None

    def list_containers(self, all: bool = False) -> List[docker.models.containers.Container]:
        """List all containers"""
        return self.client.containers.list(all=all)

    def get_container_logs(self, name: str, tail: int = 100) -> str:
        """Get container logs"""
        container = self.get_container(name)
        if container:
            try:
                logs = container.logs(tail=tail, timestamps=True)
                return logs.decode("utf-8")
            except Exception as e:
                return f"Error reading logs: {e}"
        return "Container not found"
