import logging, coloredlogs
import os
from datetime import datetime


def get_logger():
    """Get logger instance."""
    logger = logging.getLogger('logger')

    # Check if logger already has handlers and if so, remove them
    if logger.hasHandlers():
        logger.handlers.clear()

    logger.setLevel(logging.DEBUG)

    formatter = coloredlogs.ColoredFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(formatter)

    if not os.path.exists('logs/'):
        os.makedirs('logs/')

    file_handler = logging.FileHandler(f"logs/{datetime.now().strftime('%Y-%m-%d')}.log")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Add handler
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)

    return logger
