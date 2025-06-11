from datetime import datetime
from logging import getLogger

import pandas_market_calendars as mcal
from numpy import is_busday
from pandas import to_datetime
from zoneinfo import ZoneInfo

from apollo.processors.parameter_optimizer import ParameterOptimizer
from apollo.processors.signal_generator import SignalGenerator
from apollo.processors.ticker_screener import TickerScreener
from apollo.settings import (
    DEFAULT_TIME_FORMAT,
    EXCHANGE,
    EXCHANGE_TIME_ZONE_AND_HOURS,
    ParameterOptimizerMode,
)

logger = getLogger(__name__)


class SignalGenerationRunner:
    """
    Signal Generation Runner class.

    A meta class that encapsulates the signal generation logic.
    Orchestrates screening, optimization, and dispatching of signals.
    """

    def __init__(self) -> None:
        """
        Construct Signal Generation Runner.

        Initialize Ticker Screener.
        Initialize Signal Generator.
        Initialize Parameter Optimizer.
        """

        self._ticker_screener = TickerScreener()
        self._signal_generator = SignalGenerator()
        self._parameter_optimizer = ParameterOptimizer(
            ParameterOptimizerMode.MULTIPLE_STRATEGIES,
        )

        self._running = True

    def run_signal_generation(self) -> None:
        """Run signal generation process."""

        last_logged_hour = None

        while True:
            # Get current point in time
            # in the configured exchange
            current_datetime_in_exchange = datetime.now(
                tz=ZoneInfo(
                    EXCHANGE_TIME_ZONE_AND_HOURS[str(EXCHANGE)]["timezone"],
                ),
            )

            # Current date in the exchange time zone
            current_date = current_datetime_in_exchange.date()
            # Current hour in the exchange time zone
            current_hour = current_datetime_in_exchange.replace(
                minute=0,
                second=0,
                microsecond=0,
            )

            # Get close point in time
            # in the configured exchange
            close_time_in_exchange = datetime.strptime(
                EXCHANGE_TIME_ZONE_AND_HOURS[str(EXCHANGE)]["hours"]["close"],
                DEFAULT_TIME_FORMAT,
            ).time()

            # Get open point in time
            # in the configured exchange
            open_time_in_exchange = datetime.strptime(
                EXCHANGE_TIME_ZONE_AND_HOURS[str(EXCHANGE)]["hours"]["open"],
                DEFAULT_TIME_FORMAT,
            ).time()

            # Get NYSE market holidays calendar
            market_holidays = mcal.get_calendar("NYSE").holidays().holidays  # type: ignore  # noqa: PGH003

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

            if last_logged_hour != current_hour:
                last_logged_hour = current_hour

                logger.info(
                    f"Exchange: {EXCHANGE}"
                    "\n\n"
                    f"Is business day: {is_business_day}"
                    "\n\n"
                    f"Is market holiday: {is_market_holiday}"
                    "\n\n"
                    "Current time: "
                    f"{current_datetime_in_exchange.strftime(DEFAULT_TIME_FORMAT)}"
                    "\n\n"
                    f"Open time: {open_time_in_exchange.strftime(DEFAULT_TIME_FORMAT)}"
                    "\n\n"
                    f"Close time: {close_time_in_exchange.strftime(DEFAULT_TIME_FORMAT)}",  # noqa: E501
                )

            # If process can run,
            # and today is a business day,
            # and today is not a market holiday, and current
            # point in time is after the close, kick off the process
            if (
                self._running
                and is_business_day
                and not is_market_holiday
                and current_datetime_in_exchange.time() >= close_time_in_exchange
            ):
                logger.info("Signal generation process started.")

                # Screen tickers
                self._ticker_screener.process_in_parallel()

                # Optimize parameters for each strategy
                self._parameter_optimizer.process_in_parallel()

                # Generate and dispatch signals
                self._signal_generator.generate_and_dispatch_signals()

                # Flip controls
                self._running = False

                logger.info("Signal generation process completed.")

            # Flip back after market open,
            # but before close, on a business, non-holiday day
            if (
                is_business_day
                and not is_market_holiday
                and current_datetime_in_exchange.time() >= open_time_in_exchange
                and current_datetime_in_exchange.time() < close_time_in_exchange
            ):
                self._running = True
