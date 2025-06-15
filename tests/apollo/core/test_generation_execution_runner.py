import contextlib
from unittest.mock import Mock

import timeout_decorator
from freezegun import freeze_time

from apollo.core.generation_execution_runner import GenerationExecutionRunner


# Assume today date is Monday, 2024-12-30
# Assume current time is after 16:00 ET >= 20:00 UTC
@timeout_decorator.timeout(3)
@freeze_time("2024-12-30 21:00:00")
def test__run_signal_generation_execution__for_correctly_kicking_off_the_process() -> (
    None
):
    """
    Test Generation Execution Runner for correctly kicking off the process.

    Generation Execution Runner must correctly kick off the process.
    """

    generation_execution_runner = GenerationExecutionRunner()

    generation_execution_runner._ticker_screener = Mock()  # noqa: SLF001
    generation_execution_runner._signal_generator = Mock()  # noqa: SLF001
    generation_execution_runner._parameter_optimizer = Mock()  # noqa: SLF001

    with contextlib.suppress(timeout_decorator.TimeoutError):
        generation_execution_runner.run_signal_generation_execution()

    generation_execution_runner._ticker_screener.screen_tickers.assert_any_call()  # noqa: SLF001
    generation_execution_runner._parameter_optimizer.optimize_parameters.assert_any_call()  # noqa: SLF001
    generation_execution_runner._signal_generator.generate_signals.assert_any_call()  # noqa: SLF001


# Assume today date is Saturday, 2025-01-04
# Assume current time is after 16:00 ET >= 20:00 UTC
@timeout_decorator.timeout(3)
@freeze_time("2025-01-04 21:00:00")
def test__run_signal_generation_execution__for_correctly_kicking_off_the_process_on_weekend() -> (  # noqa: E501
    None
):
    """
    Test Generation Execution Runner for correctly kicking off the process on weekend.

    Generation Execution Runner must correctly kick off the process on weekend.
    """

    generation_execution_runner = GenerationExecutionRunner()

    generation_execution_runner._ticker_screener = Mock()  # noqa: SLF001
    generation_execution_runner._signal_generator = Mock()  # noqa: SLF001
    generation_execution_runner._parameter_optimizer = Mock()  # noqa: SLF001

    with contextlib.suppress(timeout_decorator.TimeoutError):
        generation_execution_runner.run_signal_generation_execution()

    generation_execution_runner._ticker_screener.screen_tickers.assert_any_call()  # noqa: SLF001
    generation_execution_runner._parameter_optimizer.optimize_parameters.assert_any_call()  # noqa: SLF001
    generation_execution_runner._signal_generator.generate_signals.assert_any_call()  # noqa: SLF001


# Assume today date is Thursday, 2025-01-02
# Assume current time is after 09:30 and before 16:00 ET
@timeout_decorator.timeout(3)
@freeze_time("2025-01-02 14:30:00")
def test__run_signal_generation_execution__for_correctly_skipping_the_process() -> None:
    """
    Test Generation Execution Runner for correctly skipping the process.

    Generation Execution Runner must correctly skip the process.
    """

    generation_execution_runner = GenerationExecutionRunner()

    generation_execution_runner._ticker_screener = Mock()  # noqa: SLF001
    generation_execution_runner._signal_generator = Mock()  # noqa: SLF001
    generation_execution_runner._parameter_optimizer = Mock()  # noqa: SLF001

    with contextlib.suppress(timeout_decorator.TimeoutError):
        generation_execution_runner.run_signal_generation_execution()

    generation_execution_runner._ticker_screener.screen_tickers.assert_not_called()  # noqa: SLF001
    generation_execution_runner._parameter_optimizer.optimize_parameters.assert_not_called()  # noqa: SLF001
    generation_execution_runner._signal_generator.generate_signals.assert_not_called()  # noqa: SLF001


# Assume today date is Wednesday, 2025-01-01
# Assume current time is after 16:00 ET >= 20:00 UTC
@timeout_decorator.timeout(3)
@freeze_time("2025-01-01, 21:00:00")
def test__run_signal_generation_execution__for_correctly_skipping_the_process_on_mh() -> (  # noqa: E501
    None
):
    """
    Test Generation Execution Runner for correctly skipping the process.

    Generation Execution Runner must correctly skip the process.
    """

    generation_execution_runner = GenerationExecutionRunner()

    generation_execution_runner._ticker_screener = Mock()  # noqa: SLF001
    generation_execution_runner._signal_generator = Mock()  # noqa: SLF001
    generation_execution_runner._parameter_optimizer = Mock()  # noqa: SLF001

    with contextlib.suppress(timeout_decorator.TimeoutError):
        generation_execution_runner.run_signal_generation_execution()

    generation_execution_runner._ticker_screener.screen_tickers.assert_not_called()  # noqa: SLF001
    generation_execution_runner._parameter_optimizer.optimize_parameters.assert_not_called()  # noqa: SLF001
    generation_execution_runner._signal_generator.generate_signals.assert_not_called()  # noqa: SLF001
