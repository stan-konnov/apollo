from logging import getLogger

from apollo.events.event_emitter import event_emitter
from apollo.models.signal_notification import SignalNotification
from apollo.processors.execution.order_manager import OrderManager
from apollo.settings import Events

logger = getLogger(__name__)


@event_emitter.on(Events.SIGNAL_GENERATED.value)
def handle_signal_generated_event(signal: SignalNotification) -> None:
    """Handle signal generated event."""

    order_manager = OrderManager()

    if signal.dispatched_position and not signal.open_position:
        logger.info("Handling dispatched position signal.")

        order_manager.handle_dispatched_position()

    if signal.open_position and not signal.dispatched_position:
        logger.info("Handling open position signal.")

    if signal.open_position and signal.dispatched_position:
        logger.info("Handling open position and dispatched position signals.")
