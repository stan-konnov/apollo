from datetime import datetime

import pandas_market_calendars as mcal
from zoneinfo import ZoneInfo

from apollo.processors.parameter_optimizer import ParameterOptimizer
from apollo.processors.signal_dispatcher import SignalDispatcher
from apollo.processors.ticker_screener import TickerScreener
from apollo.settings import ParameterOptimizerMode


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

    def generate_signals(self) -> None:
        """
        Generate signals.

        Run the signal generation process.
        """

        # Get NYSE market holidays calendar
        _market_holidays = mcal.get_calendar("NYSE").holidays().holidays  # type: ignore  # noqa: PGH003

        # It's a non-interruptable process
        # we do not require exit condition
        while True:
            # Get current point in time
            _current_time = datetime.now(tz=ZoneInfo("UTC"))

            # Screen tickers
            self._ticker_screener.process_in_parallel()

            # Optimize parameters for each strategy
            self._parameter_optimizer.process_in_parallel()

            # Dispatch signals
            self._signal_dispatcher.dispatch_signals()
