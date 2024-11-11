"""
This module contains utility functions for string manipulation and formatting

Functions

get_timestamp() -> str
    Returns a timestamp in the format YYYY_MM_DD_HH_MM_SS.
    Returns:
        A string representing the current timestamp.

get_date() -> str
    Returns a date in the format YYYY_MM_DD.
    Returns:
        A string representing the current date.

"""
import logging
from datetime import datetime

# Set up logger
logger = logging.getLogger('method-actors')


def get_timestamp():
    """Return a timestamp in the format YYYY_MM_DD_HH_MM_SS."""
    now = datetime.now()
    yearmonthdaytime = now.strftime("%Y_%m_%d_%H_%M_%S")
    return yearmonthdaytime


def get_date():
    """Return a date in the format YYYY_MM_DD."""
    now = datetime.now()
    yearmonthday = now.strftime("%Y_%m_%d")
    return yearmonthday
