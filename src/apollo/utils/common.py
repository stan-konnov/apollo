from numpy import datetime64
from pandas import to_datetime

from apollo.settings import (
    DEFAULT_DATE_FORMAT,
    END_DATE,
    EXCHANGE,
    FREQUENCY,
    INFLUXDB_BUCKET,
    INFLUXDB_MEASUREMENT,
    INFLUXDB_ORG,
    INFLUXDB_TOKEN,
    INFLUXDB_URL,
    POSTGRES_URL,
    START_DATE,
    STRATEGY,
    TICKER,
)


def to_default_date_string(date: datetime64) -> str:
    """
    Convert a numpy datetime64 object to a string in the YYYY-MM-DD format.

    :param date: The date to convert.
    :returns: The date as a string in the YYYY-MM-DD format.
    """

    timestamp = to_datetime(str(date))

    return timestamp.strftime(DEFAULT_DATE_FORMAT)


def ensure_environment_is_configured() -> None:
    """
    Ensure that all necessary environment variables are configured.

    Is run at the start of every command.

    :raises ValueError: If any of the environment variables are not configured.
    """

    required_variables = {
        "TICKER": TICKER,
        "EXCHANGE": EXCHANGE,
        "STRATEGY": STRATEGY,
        "START_DATE": START_DATE,
        "END_DATE": END_DATE,
        "FREQUENCY": FREQUENCY,
        "POSTGRES_URL": POSTGRES_URL,
        "INFLUXDB_BUCKET": INFLUXDB_BUCKET,
        "INFLUXDB_ORG": INFLUXDB_ORG,
        "INFLUXDB_TOKEN": INFLUXDB_TOKEN,
        "INFLUXDB_URL": INFLUXDB_URL,
        "INFLUXDB_MEASUREMENT": INFLUXDB_MEASUREMENT,
    }

    if any(not variable for variable in required_variables.values()):
        raise ValueError(
            f"{', '.join(required_variables)} environment variables must be set.",
        )
