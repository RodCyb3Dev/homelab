"""
Health check module
Replaces scripts/health-check.sh
"""

import socket
import ssl
from datetime import datetime
from typing import Dict, List, Optional, Any

import requests

from ..config import Config
from ..logging import setup_logging
from ..utils.docker import DockerClient
from ..utils.ssh import SSHClient


logger = setup_logging("health_check")


class HealthChecker:
    """Service health checker"""

    def __init__(self, config: Config, local: bool = True):
        """
        Initialize health checker

        Args:
            config: Configuration instance
            local: Whether to run locally (True) or via SSH (False)
        """
        self.config = config
        self.local = local
        self.deploy_path = config.get("deploy_path", "/opt/homelab")
        self.errors = []

        if local:
            try:
                self.docker = DockerClient()
            except Exception as e:
                logger.warning(f"Could not initialize Docker client: {e}")
                self.docker = None
        else:
            self.docker = None

    def check_all(self) -> Dict[str, Any]:
        """
        Run all health checks

        Returns:
            Dictionary with check results
        """
        results = {
            "timestamp": datetime.now().isoformat(),
            "docker": self._check_docker(),
            "containers": self._check_containers(),
            "services": self._check_services(),
            "resources": self._check_resources(),
            "storage": self._check_storage(),
            "ssl": self._check_ssl(),
            "errors": self.errors,
        }

        return results

    def _check_docker(self) -> Dict[str, Any]:
        """Check Docker daemon"""
        if not self.docker:
            return {"status": "unknown", "message": "Docker client not available"}

        try:
            self.docker.client.ping()
            return {"status": "healthy", "version": self.docker.client.version()}
        except Exception as e:
            self.errors.append(f"Docker check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}

    def _check_containers(self) -> Dict[str, List[Dict[str, Any]]]:
        """Check container status"""
        if not self.docker:
            return {"running": [], "stopped": []}

        containers = {
            "running": [],
            "stopped": [],
        }

        try:
            all_containers = self.docker.list_containers(all=True)
            for container in all_containers:
                container_info = {
                    "name": container.name,
                    "status": container.status,
                    "health": self.docker.get_container_health(container.name),
                }
                if container.status == "running":
                    containers["running"].append(container_info)
                else:
                    containers["stopped"].append(container_info)
        except Exception as e:
            self.errors.append(f"Container check failed: {e}")

        return containers

    def _check_services(self) -> Dict[str, Dict[str, Any]]:
        """Check service endpoints"""
        services = {
            "prometheus": {"url": "http://localhost:9090/-/healthy", "expected": 200},
            "grafana": {"url": "http://localhost:3000/api/health", "expected": 200},
            "loki": {"url": "http://localhost:3100/ready", "expected": 200},
            "authelia": {"url": "http://localhost:9091/api/health", "expected": 200},
        }

        results = {}
        for name, config in services.items():
            try:
                response = requests.get(config["url"], timeout=5)
                status = "healthy" if response.status_code == config["expected"] else "unhealthy"
                results[name] = {
                    "status": status,
                    "code": response.status_code,
                }
            except Exception as e:
                results[name] = {"status": "unreachable", "error": str(e)}
                self.errors.append(f"Service {name} check failed: {e}")

        return results

    def _check_resources(self) -> Dict[str, Any]:
        """Check system resources"""
        import psutil

        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()

            # Memory
            memory = psutil.virtual_memory()
            memory_percent = memory.percent

            # Disk
            disk = psutil.disk_usage("/")
            disk_percent = disk.percent

            # Load average
            load_avg = psutil.getloadavg()

            results = {
                "cpu": {
                    "percent": cpu_percent,
                    "count": cpu_count,
                    "load_avg": load_avg,
                },
                "memory": {
                    "total": memory.total,
                    "used": memory.used,
                    "available": memory.available,
                    "percent": memory_percent,
                },
                "disk": {
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free,
                    "percent": disk_percent,
                },
            }

            # Check for warnings
            if memory_percent > 90:
                self.errors.append(f"High memory usage: {memory_percent}%")
            if disk_percent > 90:
                self.errors.append(f"High disk usage: {disk_percent}%")

            return results

        except Exception as e:
            self.errors.append(f"Resource check failed: {e}")
            return {"error": str(e)}

    def _check_storage(self) -> Dict[str, Any]:
        """Check Storage Box mounts"""
        storage_boxes = self.config.get("storage_boxes", {})
        results = {}

        for box_name, box_config in storage_boxes.items():
            mount_point = box_config.get("mount_point", "")
            is_mounted = self._is_mounted(mount_point)

            results[box_name] = {
                "mount_point": mount_point,
                "mounted": is_mounted,
            }

            if not is_mounted:
                self.errors.append(f"Storage Box {box_name} not mounted at {mount_point}")

        return results

    def _is_mounted(self, mount_point: str) -> bool:
        """Check if mount point is mounted"""
        import subprocess

        try:
            result = subprocess.run(
                ["mountpoint", "-q", mount_point],
                check=False,
            )
            return result.returncode == 0
        except Exception:
            return False

    def _check_ssl(self) -> Dict[str, Any]:
        """Check SSL certificate expiry"""
        domain = self.config.get("domain", "")
        if not domain:
            return {"status": "skipped", "message": "No domain configured"}

        try:
            context = ssl.create_default_context()
            with socket.create_connection((domain, 443), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    not_after = cert.get("notAfter")
                    if not_after:
                        # Parse expiry date
                        from datetime import datetime
                        expiry = datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z")
                        days_left = (expiry - datetime.now()).days

                        return {
                            "status": "valid" if days_left > 0 else "expired",
                            "expiry": expiry.isoformat(),
                            "days_left": days_left,
                        }

        except Exception as e:
            self.errors.append(f"SSL check failed: {e}")
            return {"status": "error", "error": str(e)}

        return {"status": "unknown"}

    def check_remote(self, host: Optional[str] = None) -> Dict[str, Any]:
        """
        Run health checks on remote server via SSH

        Args:
            host: SSH host (default: from config)

        Returns:
            Dictionary with check results
        """
        if not host:
            host = self.config.get("ssh_host")
            if not host:
                logger.error("SSH host not configured")
                return {"error": "SSH host not configured"}

        user = self.config.get("ssh_user", "rodkode")
        key_path = self.config.get("ssh_key", "~/.ssh/ansible_key")

        logger.info(f"Running health checks on remote server: {user}@{host}")

        try:
            with SSHClient(host, user, key_path) as ssh:
                # Run health check script on remote server
                command = f"cd {self.deploy_path} && python3 -m homelab_tools health-check --local --json"
                exit_code, stdout, stderr = ssh.execute(command)

                if exit_code == 0:
                    import json
                    return json.loads(stdout)
                else:
                    logger.error(f"Remote health check failed: {stderr}")
                    return {"error": stderr}

        except Exception as e:
            logger.error(f"SSH connection failed: {e}")
            return {"error": str(e)}
