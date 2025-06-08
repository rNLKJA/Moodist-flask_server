"""Logger utility."""

import logging
import os

def setup_logger(app_name="flask_server"):
    """Set up application logger.
    
    Args:
        app_name: Name of the application
        
    Returns:
        logging.Logger: Configured logger
    """
    logger = logging.getLogger(app_name)
    
    # Set log level from environment or default to INFO
    log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
    logger.setLevel(getattr(logging, log_level))
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level))
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    return logger 