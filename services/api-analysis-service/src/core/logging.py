"""
Logging configuration for API Analysis Service
"""

import logging
import sys
from typing import Optional


def setup_logging(level: Optional[str] = None, format_string: Optional[str] = None):
    """
    Setup logging configuration
    """
    # Default log level
    log_level = level or "INFO"
    
    # Default format
    log_format = format_string or (
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Setup logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.StreamHandler(sys.stderr),
        ]
    )
    
    # Set specific logger levels
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("aiohttp").setLevel(logging.WARNING)
    
    # Create specific logger for our service
    logger = logging.getLogger("api_analysis_service")
    logger.info(f"Logging configured with level: {log_level}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name
    """
    return logging.getLogger(name)