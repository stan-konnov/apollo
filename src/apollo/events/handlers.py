from logging import getLogger

from apollo.core.market_orders_manager import MarketOrdersManager
from apollo.events.emitter import emitter
from apollo.models.signal_notification import SignalNotification
from apollo.settings import Events

logger = getLogger(__name__)


@emitter.on(Events.SIGNAL_GENERATED.value)
def handle_signal_generated_event(signal: SignalNotification) -> None:
    """Handle signal generated event."""

    market_orders_manager = MarketOrdersManager()

    if signal.dispatched_position and not signal.open_position:
        logger.info("Handling dispatched position signal.")

        market_orders_manager.handle_dispatched_position()

    if signal.open_position and not signal.dispatched_position:
        logger.info("Handling open position signal.")

    if signal.open_position and signal.dispatched_position:
        logger.info("Handling open position and dispatched position signals.")
