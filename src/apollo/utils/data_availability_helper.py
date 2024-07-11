from datetime import date, datetime, timedelta

from numpy import is_busday
from zoneinfo import ZoneInfo

from apollo.settings import (
    DEFAULT_TIME_FORMAT,
    EXCHANGE,
    EXCHANGE_TIME_ZONE_AND_HOURS,
)


class DataAvailabilityHelper:
    """
    Data Availability Helper class.

    Determines if data should be re-queried from the source
    based on provided last record date and current point in time.
    Determines if queried price data includes intraday values that should be avoided.

    NOTE: This does not yet factor in exchange holidays or partial trading days.
    """

    @staticmethod
    def check_if_price_data_needs_update(last_record_date: date) -> bool:
        """
        Identify if prices need to be re-queried.

        Re-query prices if either:

        * Last record date is before previous business day.
        * Last record date is previous business day and data available from exchange.

        :param last_record_date: Last record date.
        :returns: Boolean indicating if prices need to be re-queried.
        """

        # Get current date
        now_date = datetime.now(tz=ZoneInfo("UTC")).date()

        # Get previous business day
        previous_business_day = now_date - timedelta(days=1)

        # If minus one day offset falls on weekend
        # loop back until we get to the previous business day
        while not is_busday(previous_business_day):
            previous_business_day -= timedelta(days=1)

        # Check if the data is available from the exchange
        data_available_from_exchange = (
            DataAvailabilityHelper.check_if_price_data_available_from_exchange(now_date)
        )

        # Re-query prices
        # if last record date is before previous business day
        # or last record date is previous business day and data available from exchange
        return last_record_date < previous_business_day or (
            last_record_date == previous_business_day and data_available_from_exchange
        )

    @staticmethod
    def check_if_price_data_available_from_exchange(now_date: date) -> bool:
        """
        Check if price data is available from the exchange.

        :param now_date: Current date.
        :returns: Boolean indicating if data available from exchange.
        """

        # Check if today is a business day
        is_business_day = bool(is_busday(now_date))

        # Get the time in configured exchange
        configured_exchange_time = datetime.now(
            tz=ZoneInfo(EXCHANGE_TIME_ZONE_AND_HOURS[str(EXCHANGE)]["timezone"]),
        ).time()

        # Get configured exchange closing hours
        configured_exchange_close = datetime.strptime(
            EXCHANGE_TIME_ZONE_AND_HOURS[str(EXCHANGE)]["hours"]["close"],
            DEFAULT_TIME_FORMAT,
        ).time()

        # Check if it is after hours on business day
        # assuming that, therefore, data is available from exchange
        return is_business_day and configured_exchange_time >= configured_exchange_close

    @staticmethod
    def check_if_price_data_includes_intraday(last_queried_date: date) -> bool:
        """
        Check if queried price data includes intraday.

        :param last_queried_date: Last queried date.
        :returns: Boolean indicating if queried price data includes intraday.
        """

        # Get current date
        now_date = datetime.now(tz=ZoneInfo("UTC")).date()

        # Check if today is a business day
        is_business_day = bool(is_busday(now_date))

        # Get the time in configured exchange
        configured_exchange_time = datetime.now(
            tz=ZoneInfo(EXCHANGE_TIME_ZONE_AND_HOURS[str(EXCHANGE)]["timezone"]),
        ).time()

        # Get configured exchange opening hours
        configured_exchange_open = datetime.strptime(
            EXCHANGE_TIME_ZONE_AND_HOURS[str(EXCHANGE)]["hours"]["open"],
            DEFAULT_TIME_FORMAT,
        ).time()

        # Get configured exchange closing hours
        configured_exchange_close = datetime.strptime(
            EXCHANGE_TIME_ZONE_AND_HOURS[str(EXCHANGE)]["hours"]["close"],
            DEFAULT_TIME_FORMAT,
        ).time()

        # Check if last queried date is today
        # and if the data was queried during exchange hours
        return last_queried_date == now_date and (
            is_business_day
            and configured_exchange_open
            <= configured_exchange_time
            <= configured_exchange_close
        )
