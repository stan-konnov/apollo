from logging import getLogger

from apollo.core.market_orders_manager import MarketOrdersManager
from apollo.events.emitter import emitter
from apollo.models.signal_notification import SignalNotification
from apollo.settings import Events

logger = getLogger(__name__)


@emitter.on(Events.SIGNAL_GENERATED.value)
def handle_signal_generated_event(signal: SignalNotification) -> None:
    """Handle open position recalculated event."""

    market_orders_manager = MarketOrdersManager()

    if signal.dispatched_position:
        market_orders_manager.handle_dispatched_position()
