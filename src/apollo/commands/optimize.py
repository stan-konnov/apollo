import logging

from apollo.processors.generation.parameter_optimizer import ParameterOptimizer
from apollo.settings import ParameterOptimizerMode
from apollo.utils.common import ensure_environment_is_configured

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s %(asctime)s:\n\n%(message)s\n",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Run optimization process for individual strategy."""

    ensure_environment_is_configured()

    parameter_optimizer = ParameterOptimizer(
        ParameterOptimizerMode.SINGLE_STRATEGY,
    )
    parameter_optimizer.optimize_parameters()


if __name__ == "__main__":
    main()
