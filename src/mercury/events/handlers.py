from mercury.events.emitter import emitter
from mercury.settings import Events


@emitter.on(Events.POSITION_OPTIMIZED)
def handle_position_optimized_event() -> None:
    """
    Handle position optimized event.

    Serves as a communication link between the
    signal generation process and the Order Manager.
    """

    print("Position optimized event received. Processing...")  # noqa: T201
