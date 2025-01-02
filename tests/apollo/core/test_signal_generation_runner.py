import contextlib
from unittest.mock import Mock

import timeout_decorator
from freezegun import freeze_time

from apollo.core.signal_generation_runner import SignalGenerationRunner


# Assume today date is Monday, 2024-12-30
# Assume current time is after 16:00 ET >= 20:00 UTC
@timeout_decorator.timeout(3)
@freeze_time("2024-12-30 21:00:00")
def test__run_signal_generation__for_correctly_kicking_off_the_process() -> None:
    """
    Test Signal Generation Runner for correctly kicking off the process.

    Signal Generation Runner must correctly kick off the process.
    """

    signal_generation_runner = SignalGenerationRunner()

    signal_generation_runner._ticker_screener = Mock()  # noqa: SLF001
    signal_generation_runner._signal_dispatcher = Mock()  # noqa: SLF001
    signal_generation_runner._parameter_optimizer = Mock()  # noqa: SLF001

    with contextlib.suppress(timeout_decorator.TimeoutError):
        signal_generation_runner.run_signal_generation()

    signal_generation_runner._ticker_screener.process_in_parallel.assert_any_call()  # noqa: SLF001
    signal_generation_runner._parameter_optimizer.process_in_parallel.assert_any_call()  # noqa: SLF001
    signal_generation_runner._signal_dispatcher.dispatch_signals.assert_any_call()  # noqa: SLF001


# Assume today date is Thursday, 2025-01-02
# Assume current time is after 09:30 and before 16:00 ET
@timeout_decorator.timeout(3)
@freeze_time("2025-01-02 14:30:00")
def test__run_signal_generation__for_correctly_skipping_the_process() -> None:
    """
    Test Signal Generation Runner for correctly skipping the process.

    Signal Generation Runner must correctly skip the process.
    """

    signal_generation_runner = SignalGenerationRunner()

    signal_generation_runner._ticker_screener = Mock()  # noqa: SLF001
    signal_generation_runner._signal_dispatcher = Mock()  # noqa: SLF001
    signal_generation_runner._parameter_optimizer = Mock()  # noqa: SLF001

    with contextlib.suppress(timeout_decorator.TimeoutError):
        signal_generation_runner.run_signal_generation()

    signal_generation_runner._ticker_screener.process_in_parallel.assert_not_called()  # noqa: SLF001
    signal_generation_runner._parameter_optimizer.process_in_parallel.assert_not_called()  # noqa: SLF001
    signal_generation_runner._signal_dispatcher.dispatch_signals.assert_not_called()  # noqa: SLF001


# Assume today date is Saturday, 2025-01-04
# Assume current time is after 16:00 ET >= 20:00 UTC
@timeout_decorator.timeout(3)
@freeze_time("2025-01-04 21:00:00")
def test__run_signal_generation__for_correctly_skipping_the_process_on_weekend() -> (
    None
):
    """
    Test Signal Generation Runner for correctly skipping the process.

    Signal Generation Runner must correctly skip the process.
    """

    signal_generation_runner = SignalGenerationRunner()

    signal_generation_runner._ticker_screener = Mock()  # noqa: SLF001
    signal_generation_runner._signal_dispatcher = Mock()  # noqa: SLF001
    signal_generation_runner._parameter_optimizer = Mock()  # noqa: SLF001

    with contextlib.suppress(timeout_decorator.TimeoutError):
        signal_generation_runner.run_signal_generation()

    signal_generation_runner._ticker_screener.process_in_parallel.assert_not_called()  # noqa: SLF001
    signal_generation_runner._parameter_optimizer.process_in_parallel.assert_not_called()  # noqa: SLF001
    signal_generation_runner._signal_dispatcher.dispatch_signals.assert_not_called()  # noqa: SLF001


# Assume today date is Wednesday, 2025-01-01
# Assume current time is after 16:00 ET >= 20:00 UTC
@timeout_decorator.timeout(3)
@freeze_time("2025-01-01, 21:00:00")
def test__run_signal_generation__for_correctly_skipping_the_process_on_mh() -> None:
    """
    Test Signal Generation Runner for correctly skipping the process.

    Signal Generation Runner must correctly skip the process.
    """

    signal_generation_runner = SignalGenerationRunner()

    signal_generation_runner._ticker_screener = Mock()  # noqa: SLF001
    signal_generation_runner._signal_dispatcher = Mock()  # noqa: SLF001
    signal_generation_runner._parameter_optimizer = Mock()  # noqa: SLF001

    with contextlib.suppress(timeout_decorator.TimeoutError):
        signal_generation_runner.run_signal_generation()

    signal_generation_runner._ticker_screener.process_in_parallel.assert_not_called()  # noqa: SLF001
    signal_generation_runner._parameter_optimizer.process_in_parallel.assert_not_called()  # noqa: SLF001
    signal_generation_runner._signal_dispatcher.dispatch_signals.assert_not_called()  # noqa: SLF001
