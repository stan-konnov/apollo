from logging import getLogger

from apollo.processors.parameter_optimizer import ParameterOptimizer
from apollo.processors.signal_generator import SignalGenerator
from apollo.processors.ticker_screener import TickerScreener
from apollo.settings import (
    ParameterOptimizerMode,
)
from apollo.utils.market_time_aware import MarketTimeAware

logger = getLogger(__name__)


class SignalGenerationRunner(MarketTimeAware):
    """
    Signal Generation Runner class.

    Time and market calendar aware.

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

        super().__init__()

        self._ticker_screener = TickerScreener()
        self._signal_generator = SignalGenerator()
        self._parameter_optimizer = ParameterOptimizer(
            ParameterOptimizerMode.MULTIPLE_STRATEGIES,
        )

    def run_signal_generation(self) -> None:
        """Run signal generation process."""

        while True:
            # Check if system can generate signals
            can_generate, _ = self._determine_if_generate_or_execute()

            if can_generate:
                # Screen tickers
                self._ticker_screener.screen_tickers()

                # Optimize parameters for each strategy
                self._parameter_optimizer.optimize_parameters()

                # Generate signals
                #
                # NOTE: this would also kick off
                # execution of the signals on the market
                # and will return the control flow back here
                # once orders are places and state is synchronized
                self._signal_generator.generate_signals()

                # Reset status logged flag
                self._status_logged = False

            # Log status if not logged yet
            if not self._status_logged:
                self._status_logged = True

                logger.info(
                    "Cannot generate at the moment. Waiting for the market to close.",
                )
