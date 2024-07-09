from numpy import datetime64
from pandas import to_datetime

from apollo.settings import (
    DEFAULT_DATE_FORMAT,
    END_DATE,
    EXCHANGE,
    INFLUXDB_BUCKET,
    INFLUXDB_ORG,
    INFLUXDB_TOKEN,
    INFLUXDB_URL,
    START_DATE,
    STRATEGY,
    TICKER,
)


def to_default_date_string(date: datetime64) -> str:
    """Convert a numpy datetime64 object to a string in the YYYY-MM-DD format."""

    timestamp = to_datetime(str(date))

    return timestamp.strftime(DEFAULT_DATE_FORMAT)


def ensure_environment_is_configured() -> None:
    """
    Ensure that all necessary environment variables are configured.

    Is run at the start of every command.

    :raises ValueError: If any of the environment variables are not configured.
    """

    if None or "" in (
        TICKER,
        EXCHANGE,
        STRATEGY,
        START_DATE,
        END_DATE,
        INFLUXDB_BUCKET,
        INFLUXDB_ORG,
        INFLUXDB_TOKEN,
        INFLUXDB_URL,
    ):
        raise ValueError(
            "TICKER, EXCHANGE, STRATEGY, START_DATE, END_DATE, "
            "INFLUXDB_BUCKET, INFLUXDB_ORG, INFLUXDB_TOKEN, INFLUXDB_URL "
            "environment variables must be set.",
        )
