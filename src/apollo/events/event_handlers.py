from apollo.events.event_emitter import event_emitter
from apollo.models.signal_notification import SignalNotification
from apollo.processors.execution.disp_pos_order_manager import (
    DispatchedPositionOrderManager,
)
from apollo.settings import Events


@event_emitter.on(Events.SIGNAL_GENERATED.value)
def handle_signal_generated_event(signal: SignalNotification) -> None:
    """Handle signal generated event."""

    if signal.dispatched_position and not signal.open_position:
        dispatched_position_order_manager = DispatchedPositionOrderManager()
        dispatched_position_order_manager.handle_dispatched_position()

    if signal.open_position and not signal.dispatched_position:
        pass

    if signal.open_position and signal.dispatched_position:
        pass
