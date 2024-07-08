from datetime import datetime

from zoneinfo import ZoneInfo

from apollo.settings import DEFAULT_TIME_FORMAT, EXCHANGE, EXCHANGE_TIME_ZONE_AND_HOURS


def check_if_configured_exchange_is_closed() -> bool:
    """
    Check if the configured exchange is currently closed.

    :returns: Boolean indicating if the exchange is closed.

    :raises ValueError: If the exchange environment variable is not set.
    """

    if not EXCHANGE:
        raise ValueError("EXCHANGE environment variable must be set.")

    # Get the time in configured exchange
    configured_exchange_time = datetime.now(
        tz=ZoneInfo(EXCHANGE_TIME_ZONE_AND_HOURS[EXCHANGE]["timezone"]),
    ).strftime(DEFAULT_TIME_FORMAT)

    # Get configured exchange closing hours
    configured_exchange_close = EXCHANGE_TIME_ZONE_AND_HOURS[EXCHANGE]["hours"]["close"]

    # Check if the exchange is closed
    return configured_exchange_time > configured_exchange_close
