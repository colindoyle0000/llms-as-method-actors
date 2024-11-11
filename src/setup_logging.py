""" This module sets up the logging for "LLMs as Method Actors" package.
"""
import logging
import os


def setup_logger():
    """ Set up the logging for the "LLMs as Method Actors" package.
    """
    # Set up logger
    logger = logging.getLogger('method-actors')
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)

        # Create a log directory if it doesn't exist
        if not os.path.exists('log'):
            os.makedirs('log')

        # Create a file handler
        file_handler = logging.FileHandler(
            os.path.join('log', 'method-actors.log'))
        file_handler.setLevel(logging.DEBUG)

        # Create a console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)

        # Create a formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(filename)s:%(lineno)d - %(levelname)s - %(message)s')

        # Add the formatter to the handlers
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add the handlers to the logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
