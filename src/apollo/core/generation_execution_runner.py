from logging import getLogger

from apollo.processors.generation.parameter_optimizer import ParameterOptimizer
from apollo.processors.generation.signal_generator import SignalGenerator
from apollo.processors.generation.ticker_screener import TickerScreener
from apollo.settings import (
    ParameterOptimizerMode,
)
from apollo.utils.log_controllable import LogControllable
from apollo.utils.market_time_aware import MarketTimeAware

logger = getLogger(__name__)


class GenerationExecutionRunner(MarketTimeAware, LogControllable):
    """
    Generation Execution Runner class.

    Time and market calendar aware.

    A meta class that encapsulates core logic of the system.
    Orchestrates screening, optimization, generation, and execution of trading signals.
    """

    def __init__(self) -> None:
        """
        Construct Generation Execution Runner.

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

    def run_signal_generation_execution(
        self,
        override_market_timing: bool = False,
    ) -> None:
        """
        Run signal generation-execution process.

        :param override_market_timing: If True, will override market timing checks.
        """

        while True:
            # Check if system can generate signals
            can_generate, _ = self._determine_if_generate_or_execute()

            # Run if system can generate
            # or if market timing is overridden
            if can_generate or override_market_timing:
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

                # Reset message logged flag
                self._message_logged = False

            # Log status if not logged yet
            if not self._message_logged:
                self._message_logged = True

                logger.info(
                    "Cannot generate at the moment. "
                    "Market is still open or it is a holiday.",
                )
