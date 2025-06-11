from logging import getLogger

from apollo.events.emitter import emitter
from apollo.settings import Events

logger = getLogger(__name__)


@emitter.on(Events.POSITION_DISPATCHED.value)
def handle_position_dispatched_event() -> None:
    """
    Handle position dispatched event.

    Serves as a communication link between the
    signal generation process and the Order Manager.
    """

    logger.info("Handling position dispatched event.")
