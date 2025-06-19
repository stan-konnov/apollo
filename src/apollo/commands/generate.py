import logging

# NOTE: we require this unused import
# to be able to register event handlers
import apollo.events.event_handlers  # noqa: F401
from apollo.core.generation_execution_runner import GenerationExecutionRunner
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
    """Run signal generation-execution process."""

    ensure_environment_is_configured()

    generation_execution_runner = GenerationExecutionRunner()
    generation_execution_runner.run_signal_generation_execution()


if __name__ == "__main__":
    main()
