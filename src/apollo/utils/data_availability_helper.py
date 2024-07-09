from datetime import datetime, timedelta

from numpy import is_busday
from zoneinfo import ZoneInfo

from apollo.settings import (
    DEFAULT_DATE_FORMAT,
    DEFAULT_TIME_FORMAT,
    EXCHANGE,
    EXCHANGE_TIME_ZONE_AND_HOURS,
)


class DataAvailabilityHelper:
    """
    Data Availability Helper class.

    Determines if data should be re-queried from the source
    based on provided last record date and current point in time.
    """

    @staticmethod
    def check_if_price_data_needs_update(last_record_date: str) -> bool:
        """
        Identify if prices need to be re-queried.

        Re-query prices if either:

        * Last record date is before previous business day.
        * Last record date is previous business day and data available from exchange.

        :param last_record_date: Last record date in string format.
        :returns: Boolean indicating if prices need to be re-queried.

        :raises ValueError: If provided last record date is not in the correct format.
        """

        try:
            datetime.strptime(last_record_date, DEFAULT_DATE_FORMAT)

        except ValueError as error:
            raise ValueError(
                f"Last record date format must be {DEFAULT_DATE_FORMAT}.",
            ) from error

        # Get current point in time
        now = datetime.now(tz=ZoneInfo("UTC"))

        # Get previous business day
        previous_business_day = now - timedelta(days=1)

        # If minus one day offset falls on weekend
        # loop back until we get to the previous business day
        while not is_busday(previous_business_day.date()):
            previous_business_day -= timedelta(days=1)

        # Get date string from previous business day
        previous_business_day = previous_business_day.strftime(
            DEFAULT_DATE_FORMAT,
        )

        # Check if the data is available from the exchange
        data_available_from_exchange = (
            DataAvailabilityHelper._check_if_data_available_from_exchange(now)
        )

        # Re-query prices
        # if last record date is before previous business day
        # or last record date is previous business day and data available from exchange
        return last_record_date < previous_business_day or (
            last_record_date == previous_business_day and data_available_from_exchange
        )

    @staticmethod
    def _check_if_data_available_from_exchange(now: datetime) -> bool:
        """
        Check if price data is available from the exchange.

        :param now: Current point in time.
        :returns: Boolean indicating if data available from exchange.
        """

        # Check if today is a business day
        is_business_day = bool(is_busday(now.date()))

        # Get the time in configured exchange
        configured_exchange_time = datetime.now(
            tz=ZoneInfo(EXCHANGE_TIME_ZONE_AND_HOURS[str(EXCHANGE)]["timezone"]),
        ).strftime(DEFAULT_TIME_FORMAT)

        # Get configured exchange closing hours
        configured_exchange_close = EXCHANGE_TIME_ZONE_AND_HOURS[str(EXCHANGE)][
            "hours"
        ]["close"]

        # Check if it is after hours on business day
        # assuming that, therefore, data is available from exchange
        return is_business_day and configured_exchange_time >= configured_exchange_close
