from datetime import datetime
from logging import getLogger

import pandas_market_calendars as mcal
from pandas import to_datetime
from zoneinfo import ZoneInfo

from apollo.processors.parameter_optimizer import ParameterOptimizer
from apollo.processors.signal_dispatcher import SignalDispatcher
from apollo.processors.ticker_screener import TickerScreener
from apollo.settings import (
    DEFAULT_TIME_FORMAT,
    EXCHANGE,
    EXCHANGE_TIME_ZONE_AND_HOURS,
    ParameterOptimizerMode,
)

logger = getLogger(__name__)


class SignalGenerator:
    """
    Signal Generator class.

    A meta class that encapsulates the signal generation logic.
    Orchestrates screening, optimization, and dispatching of signals.
    """

    def __init__(self) -> None:
        """
        Construct Signal Generator.

        Initialize Ticker Screener.
        Initialize Signal Dispatcher.
        Initialize Parameter Optimizer.
        """

        self._ticker_screener = TickerScreener()
        self._signal_dispatcher = SignalDispatcher()
        self._parameter_optimizer = ParameterOptimizer(
            ParameterOptimizerMode.MULTIPLE_STRATEGIES,
        )

        self._running = True

    def generate_signals(self) -> None:
        """
        Generate signals.

        Run the signal generation process.
        """

        while self._running:
            # Get current point in time
            # in the configured exchange
            current_datetime_in_exchange = datetime.now(
                tz=ZoneInfo(
                    EXCHANGE_TIME_ZONE_AND_HOURS[str(EXCHANGE)]["timezone"],
                ),
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

            logger.info(
                f"Exchange: {EXCHANGE}"
                "\n\n"
                "Current time: "
                f"{current_datetime_in_exchange.strftime(DEFAULT_TIME_FORMAT)}"
                "\n\n"
                f"Open time: {open_time_in_exchange.strftime(DEFAULT_TIME_FORMAT)}"
                "\n\n"
                f"Close time: {close_time_in_exchange.strftime(DEFAULT_TIME_FORMAT)}",
            )

            # If today is not a market holiday, and current
            # point in time is after the close, kick off the process
            if (
                current_datetime_in_exchange.date() not in market_holidays
                and current_datetime_in_exchange.time() >= close_time_in_exchange
            ):
                logger.info("Signal generation process started.")

                # Screen tickers
                self._ticker_screener.process_in_parallel()

                # Optimize parameters for each strategy
                self._parameter_optimizer.process_in_parallel()

                # Dispatch signals
                self._signal_dispatcher.dispatch_signals()

                # Flip controls
                self._running = False

                logger.info("Signal generation process completed.")

            # Flip back after market open
            # NOTE: including non-business days (e.g., Sunday)
            if current_datetime_in_exchange.time() >= open_time_in_exchange:
                self._running = True
