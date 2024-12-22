import logging

from apollo.processors.parameter_optimizer import ParameterOptimizer
from apollo.processors.signal_dispatcher import SignalDispatcher
from apollo.processors.ticker_screener import TickerScreener
from apollo.settings import (
    ParameterOptimizerMode,
)
from apollo.utils.common import (
    ensure_environment_is_configured,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s %(asctime)s:\n\n%(message)s\n",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Run signal generation process."""

    ensure_environment_is_configured()

    ticker_screener = TickerScreener()
    ticker_screener.process_in_parallel()

    parameter_optimizer = ParameterOptimizer(
        ParameterOptimizerMode.MULTIPLE_STRATEGIES,
    )
    parameter_optimizer.process_in_parallel()

    signal_dispatcher = SignalDispatcher()
    signal_dispatcher.dispatch_signals()


if __name__ == "__main__":
    main()
