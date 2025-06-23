class LogControllable:
    """
    Log Controllable class.

    Contains a simple boolean flag to allow child
    classes to control logging behavior and improve log hygiene.
    """

    def __init__(self) -> None:
        """Construct Log Controllable."""

        self._message_logged = False
