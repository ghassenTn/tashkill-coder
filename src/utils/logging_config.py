"""Logging configuration utilities"""

import logging
import os
from typing import Optional

from ..config import get_settings


def setup_logging(
    log_file: Optional[str] = None,
    log_level: Optional[str] = None,
    clear_existing: bool = True
) -> logging.Logger:
    """
    Set up logging configuration
    
    Args:
        log_file: Path to log file (defaults to settings)
        log_level: Logging level (defaults to settings)
        clear_existing: Whether to clear existing log file
        
    Returns:
        Configured logger instance
    """
    settings = get_settings()
    
    log_file = log_file or settings.log_file
    log_level = log_level or settings.log_level
    
    # Clear existing log file if requested
    if clear_existing and os.path.exists(log_file):
        os.remove(log_file)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create logger
    logger = logging.getLogger('tashkil_coder')
    
    # Add file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(getattr(logging, log_level.upper()))
    
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    
    # Suppress warnings
    import warnings
    warnings.filterwarnings("ignore")
    
    return logger