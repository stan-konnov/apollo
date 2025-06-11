from logging import getLogger

from mercury.events.emitter import emitter
from mercury.settings import Events

logger = getLogger(__name__)


@emitter.on(Events.POSITION_OPTIMIZED.value)
def handle_position_optimized_event() -> None:
    """
    Handle position optimized event.

    Serves as a communication link between the
    signal generation process and the Order Manager.
    """

    logger.info("Handling position optimized event.")
