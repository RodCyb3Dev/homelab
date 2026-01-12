"""
Logging integration with Loki
"""

import json
import logging
import socket
import sys
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

import requests


class LokiHandler(logging.Handler):
    """Logging handler that sends logs to Loki"""

    def __init__(
        self,
        loki_url: str,
        service: str = "homelab-tools",
        labels: Optional[Dict[str, str]] = None,
        timeout: int = 5,
        max_retries: int = 3,
    ):
        """
        Initialize Loki handler

        Args:
            loki_url: Loki API URL (e.g., http://loki:3100)
            service: Service name for labels
            labels: Additional labels to include
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
        """
        super().__init__()
        self.loki_url = loki_url.rstrip("/")
        self.service = service
        self.labels = labels or {}
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()

        # Get hostname
        try:
            self.hostname = socket.gethostname()
        except Exception:
            self.hostname = "unknown"

    def emit(self, record: logging.LogRecord) -> None:
        """Send log record to Loki"""
        try:
            # Format log message
            message = self.format(record)

            # Create labels
            labels = {
                "service": self.service,
                "host": self.hostname,
                "level": record.levelname.lower(),
            }
            labels.update(self.labels)

            # Add module name if available
            if record.module:
                labels["module"] = record.module

            # Create Loki log entry
            log_entry = {
                "streams": [
                    {
                        "stream": labels,
                        "values": [[str(int(record.created * 1e9)), message]],
                    }
                ]
            }

            # Send to Loki
            url = f"{self.loki_url}/loki/api/v1/push"
            for attempt in range(self.max_retries):
                try:
                    response = self.session.post(
                        url, json=log_entry, timeout=self.timeout
                    )
                    response.raise_for_status()
                    return
                except requests.RequestException as e:
                    if attempt == self.max_retries - 1:
                        # Fallback to stderr on final failure
                        print(f"Failed to send log to Loki: {e}", file=sys.stderr)
                        print(f"Log message: {message}", file=sys.stderr)
                    else:
                        continue

        except Exception:
            # Prevent logging errors from breaking the application
            self.handleError(record)


def setup_logging(
    module: str,
    loki_url: Optional[str] = None,
    level: str = "INFO",
    log_file: Optional[str] = None,
) -> logging.Logger:
    """
    Set up logging with Loki integration

    Args:
        module: Module name for labels
        loki_url: Loki URL (default: from config or environment)
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for fallback logging

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(f"homelab-tools.{module}")
    logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers
    logger.handlers.clear()

    # Console handler (always enabled)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler (if specified)
    if log_file:
        file_path = Path(log_file)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(file_path)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    # Loki handler (if URL provided)
    if loki_url:
        loki_handler = LokiHandler(loki_url, labels={"module": module})
        loki_handler.setLevel(logging.DEBUG)
        logger.addHandler(loki_handler)

    return logger
