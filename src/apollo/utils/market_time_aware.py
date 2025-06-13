from datetime import datetime

import pandas_market_calendars as mcal
from numpy import is_busday
from pandas import to_datetime
from zoneinfo import ZoneInfo

from apollo.settings import DEFAULT_TIME_FORMAT, EXCHANGE, EXCHANGE_TIME_ZONE_AND_HOURS


class MarketTimeAware:
    """
    Marker Time Aware class.

    Is used throughout the system to identify if the
    system can run generation or execution processes.
    """

    def __init__(self) -> None:
        """Construct Market Time Aware.."""

        # Declare a boolean to
        # control logs in child classes
        self._status_logged = False

    def _determine_if_generate_or_execute(self) -> tuple[bool, bool]:
        """
        Determine if the system can generate or execute signals.

        :return: Tuple of booleans indicating if the system can generate or execute.
        """

        # Get current point in time
        # in the configured exchange
        current_datetime_in_exchange = datetime.now(
            tz=ZoneInfo(
                EXCHANGE_TIME_ZONE_AND_HOURS[str(EXCHANGE)]["timezone"],
            ),
        )

        # Current date in the exchange time zone
        current_date = current_datetime_in_exchange.date()

        # Get close point in time
        # in the configured exchange
        close_datetime_in_exchange = datetime.strptime(
            EXCHANGE_TIME_ZONE_AND_HOURS[str(EXCHANGE)]["hours"]["close"],
            DEFAULT_TIME_FORMAT,
        ).astimezone(
            ZoneInfo(
                EXCHANGE_TIME_ZONE_AND_HOURS[str(EXCHANGE)]["timezone"],
            ),
        )

        # Get open point in time
        # in the configured exchange
        open_datetime_in_exchange = datetime.strptime(
            EXCHANGE_TIME_ZONE_AND_HOURS[str(EXCHANGE)]["hours"]["open"],
            DEFAULT_TIME_FORMAT,
        ).astimezone(
            ZoneInfo(
                EXCHANGE_TIME_ZONE_AND_HOURS[str(EXCHANGE)]["timezone"],
            ),
        )

        # Get exchange market holidays calendar
        market_holidays = mcal.get_calendar(str(EXCHANGE)).holidays().holidays  # type: ignore  # noqa: PGH003

        # Transform to regular python datetime objects
        market_holidays = [to_datetime(str(holiday)) for holiday in market_holidays]

        # And limit to dates of the current year
        market_holidays = [
            holiday.date()
            for holiday in market_holidays
            if holiday.year == current_datetime_in_exchange.year
        ]

        # Check if today is a business day in configured exchange
        is_business_day = bool(is_busday(current_date))

        # Check if today is market holiday in configured exchange
        is_market_holiday = current_date in market_holidays

        # System can generate signals
        # on a business day, not a market holiday,
        # after the market close time but before the market open time
        can_generate = (
            is_business_day
            and not is_market_holiday
            and current_datetime_in_exchange >= close_datetime_in_exchange
        )

        # System can execute signals
        # on a business day, not a market holiday,
        # after the market open time, but before the market close time
        can_execute = (
            is_business_day
            and not is_market_holiday
            and current_datetime_in_exchange >= open_datetime_in_exchange
            and current_datetime_in_exchange < close_datetime_in_exchange
        )

        return can_generate, can_execute
