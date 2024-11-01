import logging

def get_logger(name):
    """Set up and return the logger."""
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(name)
    return logger
