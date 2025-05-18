import logging
from torchft.marduk.config import Config

def setup_logger(name: str = __name__, log_file: str = Config.LOG_FILE, format_log: bool = Config.FORMAT_LOG, print_to_console: bool = True) -> logging.Logger:
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
    
    # Clear existing handlers (to avoid duplicates)
    if logger.hasHandlers():
        logger.handlers.clear()
    
    # Ensure propagation is disabled to prevent output from reaching parent loggers
    logger.propagate = False
    
    # Create a console handler
    if print_to_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)  # The console only shows INFO and above
        if format_log:
            console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # Create a file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)  # The file records all levels
    if format_log:
        file_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    
    return logger

logger = setup_logger()

# Set debug_manager_logger to explicitly disable console output
debug_manager_logger = setup_logger(name="manager", log_file="/srv/apps/warren/torchft/torchft/marduk/logging/manager.log", format_log=True, print_to_console=False)