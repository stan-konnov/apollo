import logging

from apollo.backtesting.parameter_optimizer import ParameterOptimizer
from apollo.utils.common import ensure_environment_is_configured

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s %(asctime)s:\n\n%(message)s\n",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Run optimization process."""

    ensure_environment_is_configured()

    parameter_optimizer = ParameterOptimizer()
    parameter_optimizer.process_in_parallel()


if __name__ == "__main__":
    main()
