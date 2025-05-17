import logging
from torchft.marduk.config import Config

def setup_logger(name: str = __name__, log_file: str = Config.LOG_FILE, format_log: bool = Config.FORMAT_LOG) -> logging.Logger:
    """
    Setup a logger that logs to a file and the console.
    """
    # Create a logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # Set the minimum log level
    
    # Create a formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Create a console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)  # The console only shows INFO and above
    
    # Create a file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)  # The file records all levels

    if format_log:
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
    
    # Clear existing handlers (to avoid duplicates)
    if logger.hasHandlers():
        logger.handlers.clear()
    
    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

logger = setup_logger()

debug_manager_logger = setup_logger(name="manager", log_file="/srv/apps/warren/torchft/torchft/marduk/logging/manager.log", format_log=True)