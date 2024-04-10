from numpy import datetime64
from pandas import to_datetime

from apollo.settings import DEFAULT_DATE_FORMAT


def to_default_date_string(date: datetime64) -> str:
    """Convert a numpy datetime64 object to a string in the YYYY-MM-DD format."""

    timestamp = to_datetime(str(date))

    return timestamp.strftime(DEFAULT_DATE_FORMAT)
