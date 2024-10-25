"""
Utility functions for loading, saving, and exporting.

Functions
get_root_dir() -> str
    Returns the root directory for the package.
    Returns:
        A string representing the root directory of the package.
"""
import logging
import json
import os

from utils_string import get_timestamp

# Set up logger
logger = logging.getLogger('connections')


class RootDirectoryNotFoundError(Exception):
    """Exception raised when the root directory is not found."""

    def __init__(self, max_depth):
        self.max_depth = max_depth
        self.message = f"Root directory 'parody' not found within depth: {max_depth}"
        super().__init__(self.message)


def get_root_dir(max_depth=10):
    """Returns the root directory for the package."""
    # get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # get the root directory
    depth = 0
    while os.path.basename(current_dir) != 'parody_v2' and depth < max_depth:
        current_dir = os.path.dirname(current_dir)
        depth += 1
    if os.path.basename(current_dir) == 'parody_v2':
        return current_dir
    else:
        raise RootDirectoryNotFoundError(max_depth)