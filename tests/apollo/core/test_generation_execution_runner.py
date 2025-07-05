import contextlib
from unittest.mock import Mock

import timeout_decorator

from apollo.core.generation_execution_runner import GenerationExecutionRunner


@timeout_decorator.timeout(3)
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

    generation_execution_runner._determine_if_generate_or_execute = Mock(  # noqa: SLF001
        return_value=(True, False),
    )

    with contextlib.suppress(timeout_decorator.TimeoutError):
        generation_execution_runner.run_signal_generation_execution()

    generation_execution_runner._ticker_screener.screen_tickers.assert_any_call()  # noqa: SLF001
    generation_execution_runner._parameter_optimizer.optimize_parameters.assert_any_call()  # noqa: SLF001
    generation_execution_runner._signal_generator.generate_signals.assert_any_call()  # noqa: SLF001


@timeout_decorator.timeout(3)
def test__run_signal_generation_execution__for_correctly_skipping_the_process() -> None:
    """
    Test Generation Execution Runner for correctly skipping the process.

    Generation Execution Runner must correctly skip the process.
    """

    generation_execution_runner = GenerationExecutionRunner()

    generation_execution_runner._ticker_screener = Mock()  # noqa: SLF001
    generation_execution_runner._signal_generator = Mock()  # noqa: SLF001
    generation_execution_runner._parameter_optimizer = Mock()  # noqa: SLF001

    generation_execution_runner._determine_if_generate_or_execute = Mock(  # noqa: SLF001
        return_value=(False, False),
    )

    with contextlib.suppress(timeout_decorator.TimeoutError):
        generation_execution_runner.run_signal_generation_execution()

    generation_execution_runner._ticker_screener.screen_tickers.assert_not_called()  # noqa: SLF001
    generation_execution_runner._parameter_optimizer.optimize_parameters.assert_not_called()  # noqa: SLF001
    generation_execution_runner._signal_generator.generate_signals.assert_not_called()  # noqa: SLF001


@timeout_decorator.timeout(3)
def test__run_signal_generation_execution__for_correctly_skipping_the_process_on_the_weekend() -> (  # noqa: E501
    None
):
    """
    Test Generation Execution Runner for correctly skipping the process on weekend.

    Generation Execution Runner must correctly skip the process on weekend.
    """

    generation_execution_runner = GenerationExecutionRunner()

    generation_execution_runner._ticker_screener = Mock()  # noqa: SLF001
    generation_execution_runner._signal_generator = Mock()  # noqa: SLF001
    generation_execution_runner._parameter_optimizer = Mock()  # noqa: SLF001

    generation_execution_runner._determine_if_generate_or_execute = Mock(  # noqa: SLF001
        return_value=(False, False),
    )

    with contextlib.suppress(timeout_decorator.TimeoutError):
        generation_execution_runner.run_signal_generation_execution()

    generation_execution_runner._ticker_screener.screen_tickers.assert_not_called()  # noqa: SLF001
    generation_execution_runner._parameter_optimizer.optimize_parameters.assert_not_called()  # noqa: SLF001
    generation_execution_runner._signal_generator.generate_signals.assert_not_called()  # noqa: SLF001


@timeout_decorator.timeout(3)
def test__run_signal_generation_execution__for_correctly_skipping_the_process_on_mh() -> (  # noqa: E501
    None
):
    """
    Test Generation Execution Runner for correctly skipping the process on MH.

    Generation Execution Runner must correctly skip the process on market holidays.
    """

    generation_execution_runner = GenerationExecutionRunner()

    generation_execution_runner._ticker_screener = Mock()  # noqa: SLF001
    generation_execution_runner._signal_generator = Mock()  # noqa: SLF001
    generation_execution_runner._parameter_optimizer = Mock()  # noqa: SLF001

    generation_execution_runner._determine_if_generate_or_execute = Mock(  # noqa: SLF001
        return_value=(False, False),
    )

    with contextlib.suppress(timeout_decorator.TimeoutError):
        generation_execution_runner.run_signal_generation_execution()

    generation_execution_runner._ticker_screener.screen_tickers.assert_not_called()  # noqa: SLF001
    generation_execution_runner._parameter_optimizer.optimize_parameters.assert_not_called()  # noqa: SLF001
    generation_execution_runner._signal_generator.generate_signals.assert_not_called()  # noqa: SLF001


@timeout_decorator.timeout(3)
def test__run_signal_generation_execution__for_correctly_kicking_off_the_process_on_the_weekend_overridden() -> (  # noqa: E501
    None
):
    """
    Test Generation Execution Runner for correctly kicking off the process on weekend.

    Generation Execution Runner must correctly
    kick off the process on weekend when overridden.
    """

    generation_execution_runner = GenerationExecutionRunner()

    generation_execution_runner._ticker_screener = Mock()  # noqa: SLF001
    generation_execution_runner._signal_generator = Mock()  # noqa: SLF001
    generation_execution_runner._parameter_optimizer = Mock()  # noqa: SLF001

    generation_execution_runner._determine_if_generate_or_execute = Mock(  # noqa: SLF001
        return_value=(False, False),
    )

    with contextlib.suppress(timeout_decorator.TimeoutError):
        generation_execution_runner.run_signal_generation_execution(
            override_market_timing=True,
        )

    generation_execution_runner._ticker_screener.screen_tickers.assert_any_call()  # noqa: SLF001
    generation_execution_runner._parameter_optimizer.optimize_parameters.assert_any_call()  # noqa: SLF001
    generation_execution_runner._signal_generator.generate_signals.assert_any_call()  # noqa: SLF001


@timeout_decorator.timeout(3)
def test__run_signal_generation_execution__for_correctly_kicking_off_the_process_on_mh_overridden() -> (  # noqa: E501
    None
):
    """
    Test Generation Execution Runner for correctly kicking off the process on MH.

    Generation Execution Runner must correctly skip the process on market holidays.
    """

    generation_execution_runner = GenerationExecutionRunner()

    generation_execution_runner._ticker_screener = Mock()  # noqa: SLF001
    generation_execution_runner._signal_generator = Mock()  # noqa: SLF001
    generation_execution_runner._parameter_optimizer = Mock()  # noqa: SLF001

    generation_execution_runner._determine_if_generate_or_execute = Mock(  # noqa: SLF001
        return_value=(False, False),
    )

    with contextlib.suppress(timeout_decorator.TimeoutError):
        generation_execution_runner.run_signal_generation_execution(
            override_market_timing=True,
        )

    generation_execution_runner._ticker_screener.screen_tickers.assert_any_call()  # noqa: SLF001
    generation_execution_runner._parameter_optimizer.optimize_parameters.assert_any_call()  # noqa: SLF001
    generation_execution_runner._signal_generator.generate_signals.assert_any_call()  # noqa: SLF001
