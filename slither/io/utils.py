"""Utilities for input and output related code."""
from datetime import datetime


def datetime_from_iso8601(date_str):
    """Convert ISO 8601 datetime string to datetime.

    See `ISO 8601 (Wikipedia) <https://en.wikipedia.org/wiki/ISO_8601>`_.

    Parameters
    ----------
    date_str : str
        Example: 2016-12-11T10:00:00.000Z

    Returns
    -------
    dt : datetime
        Datetime representation
    """
    date_str = date_str[:-5]  # remove milliseconds: '.000Z'
    return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")


def to_utf8(content):
    """Convert string to UTF-8.

    Parameters
    ----------
    content : str
        String in windows-1252 or utf-8.

    Returns
    -------
    utf8 : str
        String in utf-8.
    """
    try:
        content = content.decode("windows-1252")
    finally:
        return content.encode("utf-8")
