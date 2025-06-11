from logging import getLogger

from apollo.events.emitter import emitter
from apollo.models.dispatchable_signal import DispatchableSignal
from apollo.settings import Events

logger = getLogger(__name__)


@emitter.on(Events.SIGNAL_GENERATED.value)
def handle_signal_generated_event(signal: DispatchableSignal) -> None:
    """Handle open position recalculated event."""

    logger.info(signal)
