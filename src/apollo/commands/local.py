import logging

from apollo.backtesting.parameter_optimizer import ParameterOptimizer

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s %(asctime)s:\n\n%(message)s\n",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Run local scripts to quickly iterate on code."""

    parameter_optimizer = ParameterOptimizer()
    parameter_optimizer.process()


if __name__ == "__main__":
    main()
