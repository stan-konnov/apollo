from numpy import datetime64
from pandas import to_datetime

from apollo.core.strategy_catalogue_map import STRATEGY_CATALOGUE_MAP
from apollo.settings import (
    DEFAULT_DATE_FORMAT,
    END_DATE,
    EXCHANGE,
    EXCHANGE_TIME_ZONE_AND_HOURS,
    FREQUENCY,
    INFLUXDB_BUCKET,
    INFLUXDB_MEASUREMENT,
    INFLUXDB_ORG,
    INFLUXDB_TOKEN,
    INFLUXDB_URL,
    POSTGRES_URL,
    SCREENING_LIQUIDITY_THRESHOLD,
    SCREENING_WINDOW_SIZE,
    SP500_COMPONENTS_URL,
    SP500_FUTURES_TICKER,
    START_DATE,
    STRATEGY,
    SUPPORTED_DATA_ENHANCERS,
    TICKER,
    VIX_TICKER,
    YahooApiFrequencies,
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
    :raises ValueError: If the strategy is not a valid strategy.
    :raises ValueError: If the exchange is not a valid exchange.
    :raises ValueError: If the frequency is not a valid frequency.
    """

    required_variables = {
        "TICKER": TICKER,
        "EXCHANGE": EXCHANGE,
        "STRATEGY": STRATEGY,
        "START_DATE": START_DATE,
        "END_DATE": END_DATE,
        "FREQUENCY": FREQUENCY,
        "VIX_TICKER": VIX_TICKER,
        "POSTGRES_URL": POSTGRES_URL,
        "INFLUXDB_URL": INFLUXDB_URL,
        "INFLUXDB_ORG": INFLUXDB_ORG,
        "INFLUXDB_TOKEN": INFLUXDB_TOKEN,
        "INFLUXDB_BUCKET": INFLUXDB_BUCKET,
        "INFLUXDB_MEASUREMENT": INFLUXDB_MEASUREMENT,
        "SP500_COMPONENTS_URL": SP500_COMPONENTS_URL,
        "SP500_FUTURES_TICKER": SP500_FUTURES_TICKER,
        "SCREENING_WINDOW_SIZE": SCREENING_WINDOW_SIZE,
        "SUPPORTED_DATA_ENHANCERS": SUPPORTED_DATA_ENHANCERS,
        "SCREENING_LIQUIDITY_THRESHOLD": SCREENING_LIQUIDITY_THRESHOLD,
    }

    # Check if any of the required variables are not set
    if any(not variable for variable in required_variables.values()):
        raise ValueError(
            f"{', '.join(required_variables)} environment variables must be set.",
        )

    # Check if strategy is a valid strategy
    if STRATEGY not in STRATEGY_CATALOGUE_MAP:
        raise ValueError(
            f"Invalid STRATEGY environment variable: {STRATEGY}. "
            f"Accepted values: {', '.join(STRATEGY_CATALOGUE_MAP)}",
        )

    # Check if exchange is a valid exchange
    if EXCHANGE not in EXCHANGE_TIME_ZONE_AND_HOURS:
        raise ValueError(
            f"Invalid EXCHANGE environment variable: {EXCHANGE}. "
            f"Accepted values: {', '.join(EXCHANGE_TIME_ZONE_AND_HOURS)}",
        )

    # Check if the frequency is a valid Yahoo Finance API frequency
    if FREQUENCY not in YahooApiFrequencies:
        raise ValueError(
            f"Invalid FREQUENCY environment variable: {FREQUENCY}. "
            f"Accepted values: {', '.join([f.value for f in YahooApiFrequencies])}",
        )
