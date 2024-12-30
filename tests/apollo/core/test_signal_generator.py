import signal
from types import FrameType
from typing import Any
from unittest.mock import Mock

from freezegun import freeze_time

from apollo.core.signal_generator import SignalGenerator


class ForcedInterruptError(Exception):
    """A dummy exception to interrupt the process."""


def timeout_handler(_signal: int, _frame: FrameType | None) -> Any:  # noqa: ANN401
    """Raise ForcedInterruptError to interrupt the process."""
    raise ForcedInterruptError


# Assume today date is Monday, 2024-12-30
# Assume current time is after 16:00 ET >= 20:00 UTC
@freeze_time("2024-12-30 21:00:00")
def test__generate_signals__for_correctly_kicking_off_the_process() -> None:
    """
    Test Signal Generator for correctly kicking off the process.

    Signal Generator must correctly kick off the process.
    """
    signal.signal(signal.SIGALRM, timeout_handler)

    signal_generator = SignalGenerator()

    signal_generator._ticker_screener = Mock()  # noqa: SLF001
    signal_generator._signal_dispatcher = Mock()  # noqa: SLF001
    signal_generator._parameter_optimizer = Mock()  # noqa: SLF001

    try:
        signal.alarm(3)  # Set a timeout of 2 seconds
        signal_generator.generate_signals()
    except ForcedInterruptError:
        signal.alarm(0)

    signal_generator._ticker_screener.process_in_parallel.assert_called_once()  # noqa: SLF001
    signal_generator._parameter_optimizer.process_in_parallel.assert_called_once()  # noqa: SLF001
    signal_generator._signal_dispatcher.dispatch_signals.assert_called_once()  # noqa: SLF001
