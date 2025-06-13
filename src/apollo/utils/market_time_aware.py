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

        # Get timezone of the configured exchange
        exchange_timezone = EXCHANGE_TIME_ZONE_AND_HOURS[str(EXCHANGE)]["timezone"]

        # Get current point in time
        # in the configured exchange
        current_datetime_in_exchange = datetime.now(
            tz=ZoneInfo(exchange_timezone),
        )

        # Get current date in the configured exchange
        current_date = current_datetime_in_exchange.date()

        # Get open point in time
        # in the configured exchange
        open_datetime_in_exchange = datetime.combine(
            current_date,
            datetime.strptime(
                EXCHANGE_TIME_ZONE_AND_HOURS[str(EXCHANGE)]["hours"]["open"],
                DEFAULT_TIME_FORMAT,
            ).time(),
        ).replace(tzinfo=ZoneInfo(exchange_timezone))

        # Get close point in time
        # in the configured exchange
        close_datetime_in_exchange = datetime.combine(
            current_date,
            datetime.strptime(
                EXCHANGE_TIME_ZONE_AND_HOURS[str(EXCHANGE)]["hours"]["close"],
                DEFAULT_TIME_FORMAT,
            ).time(),
        ).replace(tzinfo=ZoneInfo(exchange_timezone))

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

        # Check if current time in exchange
        # is within the market open and close times
        is_trading_hours = (
            open_datetime_in_exchange
            <= current_datetime_in_exchange
            < close_datetime_in_exchange
        )

        # System can generate signals
        # on any day that is not a market holiday,
        # and outside of the market open and close times
        can_generate = not is_market_holiday and not is_trading_hours

        # System can execute signals
        # on a trading day, not a market holiday,
        # and within of the market open and close times
        can_execute = is_business_day and not is_market_holiday and is_trading_hours

        return can_generate, can_execute
