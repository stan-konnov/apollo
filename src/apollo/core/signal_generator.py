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
