from unittest.mock import Mock

from freezegun import freeze_time

from apollo.core.signal_generator import SignalGenerator


# Assume today date is Monday, 2024-12-30
# Assume current time is after 16:00 ET >= 20:00 UTC
@freeze_time("2024-12-30 21:00:00")
def test__generate_signals__for_correctly_kicking_off_the_process() -> None:
    """
    Test Signal Generator for correctly kicking off the process.

    Signal Generator must correctly kick off the process.
    """

    signal_generator = SignalGenerator()

    signal_generator._ticker_screener = Mock()  # noqa: SLF001
    signal_generator._signal_dispatcher = Mock()  # noqa: SLF001
    signal_generator._parameter_optimizer = Mock()  # noqa: SLF001

    signal_generator.generate_signals()

    signal_generator._ticker_screener.process_in_parallel.assert_called_once()  # noqa: SLF001
    signal_generator._parameter_optimizer.process_in_parallel.assert_called_once()  # noqa: SLF001
    signal_generator._signal_dispatcher.dispatch_signals.assert_called_once()  # noqa: SLF001
