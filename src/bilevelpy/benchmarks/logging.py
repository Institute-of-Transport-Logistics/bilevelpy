"""
Simple JSON logging setup for benchmark runner.
Uses standard Python logging with a custom JSON formatter for structured structured logs.
"""
import json
import logging
import os
from datetime import datetime


def setup_logger(log_dir: str = "logs", log_name: str = "benchmark") -> logging.Logger:
    """Sets up a structured JSON logging pipeline using standard Python logging.

    Args:
        log_dir: Directory to store logs
        log_name: Name of the logger and log file

    Returns:
        A configured logging.Logger instance that outputs JSON
    """
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"{log_name}.log")

    logger = logging.getLogger(log_name)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    # Reset existing handlers to prevent duplicate logging
    logger.handlers.clear()

    class JsonFormatter(logging.Formatter):
        """Custom formatter that outputs structured JSON logs."""

        def format(self, record: logging.LogRecord) -> str:

            log_data = {
                "timestamp": datetime.now(datetime.UTC).isoformat().replace("+00:00", "Z"),
                "level": record.levelname.lower(),
                "logger": record.name,
                "event": record.getMessage(),
            }

            # 2. Safely merge dictionary parameters passed via extra=
            extra_data = getattr(record, "kwargs", {})
            if isinstance(extra_data, dict):
                for k, v in extra_data.items():
                    # Unpack nested scenario fields straight to top-level columns
                    if k == "scenario" and isinstance(v, dict):
                        for sk, sv in v.items():
                            if not callable(sv):
                                log_data[sk] = sv
                    elif not callable(v):  # Skip non-serializable lambdas/functions
                        try:
                            # Try to serialize to ensure it's JSON-safe
                            json.dumps(v)
                            log_data[k] = v
                        except (TypeError, ValueError):
                            # Fall back to string representation for complex objects
                            log_data[k] = str(v)

            return json.dumps(log_data)

    # Attach to both Console and File with JSON formatting
    formatter = JsonFormatter()

    # File handler for persistent logs
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console handler for real-time logs
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


def log_event(logger: logging.Logger, event: str, level: str = "info", **kwargs) -> None:
    """Logs an event with structured keyword arguments.

    Args:
        logger: The logger instance
        event: Event name/message
        level: Log level (debug, info, warning, error, critical)
        **kwargs: Structured data to include in the log

    Example:
        log_event(logger, "Method starting", level="info",
                  run_idx=0, method="Fast Lagrange", scenario=scenario_dict)
    """
    log_func = getattr(logger, level.lower(), logger.info)

    log_func(event, extra={"kwargs": kwargs})
