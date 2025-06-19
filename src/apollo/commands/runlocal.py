import logging

# NOTE: we require this unused import
# to be able to register event handlers
import apollo.events.event_handlers  # noqa: F401
from apollo.processors.generation.signal_generator import SignalGenerator
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
    """Run isolated logic for development purposes."""

    ensure_environment_is_configured()

    signal_generator = SignalGenerator()
    signal_generator.generate_signals()


if __name__ == "__main__":
    main()
