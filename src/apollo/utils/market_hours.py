from datetime import datetime

from numpy import is_busday
from zoneinfo import ZoneInfo

from apollo.settings import DEFAULT_TIME_FORMAT, EXCHANGE, EXCHANGE_TIME_ZONE_AND_HOURS


def check_if_data_available_from_exchange() -> bool:
    """
    Check if price data is available from the exchange.

    :returns: Boolean indicating if data available from exchange.
    """

    if not EXCHANGE:
        raise ValueError("EXCHANGE environment variable must be set.")

    # Check if today is a business day
    is_business_day = bool(
        is_busday(datetime.now(tz=ZoneInfo("UTC")).date()),
    )

    # Get the time in configured exchange
    configured_exchange_time = datetime.now(
        tz=ZoneInfo(EXCHANGE_TIME_ZONE_AND_HOURS[EXCHANGE]["timezone"]),
    ).strftime(DEFAULT_TIME_FORMAT)

    # Get configured exchange closing hours
    configured_exchange_close = EXCHANGE_TIME_ZONE_AND_HOURS[EXCHANGE]["hours"]["close"]

    # Check if it is after hours on business day
    # assuming that, therefore, data is available from exchange
    return is_business_day and configured_exchange_time >= configured_exchange_close
