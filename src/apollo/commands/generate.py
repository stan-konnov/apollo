import logging

# NOTE: we require this unused import
# to be able to register event handlers
import apollo.events.event_handlers  # noqa: F401
from apollo.core.signal_generation_runner import SignalGenerationRunner
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

    signal_generation_runner = SignalGenerationRunner()
    signal_generation_runner.run_signal_generation()


if __name__ == "__main__":
    main()
