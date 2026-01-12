"""
Configuration management for homelab-tools
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional


class Config:
    """Configuration manager for homelab-tools"""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration
        
        Args:
            config_path: Path to config file (default: ~/.homelab/config.yaml)
        """
        if config_path is None:
            config_dir = Path.home() / ".homelab"
            config_path = config_dir / "config.yaml"
        else:
            config_path = Path(config_path)

        self.config_path = config_path
        self.config: Dict[str, Any] = {}
        self.load()

    def load(self) -> None:
        """Load configuration from file or environment variables"""
        # Default configuration
        self.config = {
            "deploy_path": os.getenv("DEPLOY_PATH", "/opt/homelab"),
            "ssh_user": os.getenv("SSH_USER", "rodkode"),
            "ssh_host": os.getenv("SSH_HOST", ""),
            "ssh_key": os.getenv("SSH_KEY", "~/.ssh/ansible_key"),
            "loki_url": os.getenv("LOKI_URL", "http://loki:3100"),
            "prometheus_url": os.getenv("PROMETHEUS_URL", "http://prometheus:9090"),
            "storage_boxes": {
                "main": {
                    "host": os.getenv("STORAGE_BOX_HOST", "u529830.your-storagebox.de"),
                    "user": os.getenv("STORAGE_BOX_USER", "u529830"),
                    "mount_point": "/mnt/storagebox",
                },
                "immich": {
                    "host": os.getenv("IMMICH_SB_HOST", "u527847.your-storagebox.de"),
                    "user": os.getenv("IMMICH_SB_USER", "u527847"),
                    "mount_point": "/mnt/storagebox-immich",
                },
            },
            "backup": {
                "primary": {
                    "type": "storagebox",
                    "host": os.getenv("BACKUP_PRIMARY_HOST", ""),
                    "user": os.getenv("BACKUP_PRIMARY_USER", ""),
                    "repository": os.getenv("BACKUP_PRIMARY_REPO", ""),
                },
                "secondary": {
                    "type": "server",
                    "host": os.getenv("BACKUP_SECONDARY_HOST", ""),
                    "user": os.getenv("BACKUP_SECONDARY_USER", ""),
                    "repository": os.getenv("BACKUP_SECONDARY_REPO", ""),
                },
            },
            "slack": {
                "webhook_url": os.getenv("SLACK_WEBHOOK_URL", ""),
            },
        }

        # Load from file if it exists
        if self.config_path.exists():
            with open(self.config_path, "r") as f:
                file_config = yaml.safe_load(f) or {}
                self._deep_update(self.config, file_config)

    def _deep_update(self, base: Dict, update: Dict) -> None:
        """Recursively update nested dictionaries"""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_update(base[key], value)
            else:
                base[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation (e.g., 'backup.primary.host')"""
        keys = key.split(".")
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def set(self, key: str, value: Any) -> None:
        """Set configuration value using dot notation"""
        keys = key.split(".")
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value

    def save(self) -> None:
        """Save configuration to file"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w") as f:
            yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)
