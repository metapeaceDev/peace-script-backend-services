import logging
import sys

from python_json_logger import jsonlogger


def setup_logging():
    """
    Configures the root logger for the application to use structured JSON logging.
    """
    logger = logging.getLogger()
    
    # Clear existing handlers
    if logger.hasHandlers():
        logger.handlers.clear()

    # Use a handler that outputs to stdout
    log_handler = logging.StreamHandler(sys.stdout)
    
    # Define the format for the JSON logs
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s %(funcName)s %(lineno)d'
    )
    
    log_handler.setFormatter(formatter)
    logger.addHandler(log_handler)
    logger.setLevel(logging.INFO)
    
    # Prevent logging from propagating to the root logger
    logger.propagate = False

# Call setup function when module is imported
setup_logging()

def get_logger(name):
    """
    Returns a logger with the specified name.
    """
    return logging.getLogger(name)
