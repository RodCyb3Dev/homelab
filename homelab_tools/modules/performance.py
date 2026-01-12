"""
Performance monitoring module
Replaces scripts/jellyfin-performance-check.sh
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Any

import requests

from ..config import Config
from ..logging import setup_logging
from ..utils.docker import DockerClient


logger = setup_logging("performance")


class PerformanceMonitor:
    """Performance monitoring and reporting"""

    def __init__(self, config: Config):
        """
        Initialize performance monitor

        Args:
            config: Configuration instance
        """
        self.config = config
        try:
            self.docker = DockerClient()
        except Exception as e:
            logger.warning(f"Could not initialize Docker client: {e}")
            self.docker = None

    def check(self, service: Optional[str] = None) -> Dict[str, Any]:
        """
        Check performance metrics

        Args:
            service: Service name to check (None = all)

        Returns:
            Dictionary with performance metrics
        """
        results = {
            "timestamp": datetime.now().isoformat(),
            "system": self._check_system(),
            "containers": self._check_containers(service),
        }

        if service == "jellyfin" or service is None:
            results["jellyfin"] = self._check_jellyfin()

        return results

    def _check_system(self) -> Dict[str, Any]:
        """Check system performance"""
        try:
            import psutil

            cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")
            load_avg = psutil.getloadavg()

            return {
                "cpu": {
                    "percent": sum(cpu_percent) / len(cpu_percent),
                    "per_cpu": cpu_percent,
                    "count": psutil.cpu_count(),
                    "load_avg": load_avg,
                },
                "memory": {
                    "total": memory.total,
                    "used": memory.used,
                    "available": memory.available,
                    "percent": memory.percent,
                },
                "disk": {
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free,
                    "percent": disk.percent,
                },
            }
        except ImportError:
            logger.warning("psutil not available, skipping system metrics")
            return {"error": "psutil not installed"}
        except Exception as e:
            logger.error(f"System check failed: {e}")
            return {"error": str(e)}

    def _check_containers(self, service: Optional[str] = None) -> Dict[str, Any]:
        """Check container performance"""
        if not self.docker:
            return {"error": "Docker client not available"}

        containers = {}
        try:
            if service:
                container = self.docker.get_container(service)
                if container:
                    stats = self.docker.get_container_stats(service)
                    if stats:
                        containers[service] = self._parse_stats(stats)
            else:
                all_containers = self.docker.list_containers()
                for container in all_containers:
                    stats = self.docker.get_container_stats(container.name)
                    if stats:
                        containers[container.name] = self._parse_stats(stats)
        except Exception as e:
            logger.error(f"Container check failed: {e}")
            return {"error": str(e)}

        return containers

    def _parse_stats(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Docker stats into readable format"""
        try:
            # Calculate CPU percentage
            cpu_delta = stats["cpu_stats"]["cpu_usage"]["total_usage"] - stats["precpu_stats"]["cpu_usage"]["total_usage"]
            system_delta = stats["cpu_stats"]["system_cpu_usage"] - stats["precpu_stats"]["system_cpu_usage"]
            cpu_percent = (cpu_delta / system_delta) * len(stats["cpu_stats"]["cpu_usage"]["percpu_usage"]) * 100.0

            # Memory
            memory_usage = stats["memory_stats"].get("usage", 0)
            memory_limit = stats["memory_stats"].get("limit", 0)
            memory_percent = (memory_usage / memory_limit * 100) if memory_limit > 0 else 0

            # Network
            networks = stats.get("networks", {})
            network_rx = sum(net.get("rx_bytes", 0) for net in networks.values())
            network_tx = sum(net.get("tx_bytes", 0) for net in networks.values())

            return {
                "cpu_percent": round(cpu_percent, 2),
                "memory": {
                    "usage": memory_usage,
                    "limit": memory_limit,
                    "percent": round(memory_percent, 2),
                },
                "network": {
                    "rx_bytes": network_rx,
                    "tx_bytes": network_tx,
                },
            }
        except Exception as e:
            logger.error(f"Failed to parse stats: {e}")
            return {"error": str(e)}

    def _check_jellyfin(self) -> Dict[str, Any]:
        """Check Jellyfin-specific metrics"""
        if not self.docker:
            return {"error": "Docker client not available"}

        results = {}

        # Check if Jellyfin container is running
        if not self.docker.is_container_running("jellyfin"):
            return {"error": "Jellyfin container not running"}

        # Get active sessions
        try:
            response = requests.get("http://localhost:8096/Sessions", timeout=5)
            if response.status_code == 200:
                sessions = response.json()
                results["sessions"] = {
                    "count": len(sessions),
                    "active": [s.get("UserName") for s in sessions],
                }
        except Exception as e:
            logger.warning(f"Could not get Jellyfin sessions: {e}")

        # Get transcoding cache usage
        try:
            exit_code, stdout, stderr = self.docker.client.containers.get("jellyfin").exec_run(
                "df -h /config/data/transcodes"
            )
            if exit_code == 0:
                results["transcoding_cache"] = stdout.decode("utf-8")
        except Exception as e:
            logger.warning(f"Could not get transcoding cache info: {e}")

        return results

    def generate_report(
        self,
        format: str = "json",
        output_file: Optional[str] = None,
        service: Optional[str] = None,
    ) -> str:
        """
        Generate performance report

        Args:
            format: Report format (json, html, slack)
            output_file: Output file path (None = stdout)
            service: Service to report on (None = all)

        Returns:
            Report content
        """
        data = self.check(service)

        if format == "json":
            content = json.dumps(data, indent=2)
        elif format == "html":
            content = self._generate_html_report(data)
        elif format == "slack":
            content = self._generate_slack_report(data)
        else:
            raise ValueError(f"Unknown format: {format}")

        if output_file:
            with open(output_file, "w") as f:
                f.write(content)
            logger.info(f"Report written to {output_file}")
        else:
            print(content)

        return content

    def _generate_html_report(self, data: Dict[str, Any]) -> str:
        """Generate HTML report"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Homelab Performance Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        .metric {{ margin: 10px 0; padding: 10px; background: #f5f5f5; border-radius: 5px; }}
        .error {{ color: red; }}
        .warning {{ color: orange; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #4CAF50; color: white; }}
    </style>
</head>
<body>
    <h1>Homelab Performance Report</h1>
    <p>Generated: {data.get('timestamp', 'Unknown')}</p>
    
    <h2>System Metrics</h2>
    <div class="metric">
        <pre>{json.dumps(data.get('system', {}), indent=2)}</pre>
    </div>
    
    <h2>Container Metrics</h2>
    <div class="metric">
        <pre>{json.dumps(data.get('containers', {}), indent=2)}</pre>
    </div>
</body>
</html>
"""
        return html

    def _generate_slack_report(self, data: Dict[str, Any]) -> str:
        """Generate Slack webhook payload"""
        system = data.get("system", {})
        containers = data.get("containers", {})

        # Build Slack message
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "📊 Homelab Performance Report",
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Generated:* {data.get('timestamp', 'Unknown')}",
                },
            },
        ]

        # System metrics
        if "cpu" in system:
            cpu = system["cpu"]
            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*CPU Usage:* {cpu.get('percent', 0):.1f}%\n*Load Average:* {', '.join(map(str, cpu.get('load_avg', [])))}",
                    },
                }
            )

        if "memory" in system:
            memory = system["memory"]
            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Memory Usage:* {memory.get('percent', 0):.1f}% ({memory.get('used', 0) / 1024**3:.2f} GB / {memory.get('total', 0) / 1024**3:.2f} GB)",
                    },
                }
            )

        # Container summary
        if containers:
            container_count = len(containers)
            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Containers Monitored:* {container_count}",
                    },
                }
            )

        payload = {"blocks": blocks}

        return json.dumps(payload)

    def send_slack_report(self, service: Optional[str] = None) -> bool:
        """
        Send performance report to Slack

        Args:
            service: Service to report on (None = all)

        Returns:
            True if successful
        """
        webhook_url = self.config.get("slack.webhook_url")
        if not webhook_url:
            logger.error("Slack webhook URL not configured")
            return False

        payload_json = self._generate_slack_report(self.check(service))
        payload = json.loads(payload_json)

        try:
            response = requests.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            logger.info("Slack report sent successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to send Slack report: {e}")
            return False
