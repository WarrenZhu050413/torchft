
import logging

def setup_logger(name: str = __name__, log_file: str = "marduk.log") -> logging.Logger:
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
    console_handler.setFormatter(formatter)
    
    # Create a file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)  # The file records all levels
    file_handler.setFormatter(formatter)
    
    # Clear existing handlers (to avoid duplicates)
    if logger.hasHandlers():
        logger.handlers.clear()
    
    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

logger = setup_logger()