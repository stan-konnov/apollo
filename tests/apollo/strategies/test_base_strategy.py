from typing import Any, Type

import pandas as pd
import pytest

from apollo.calculations.average_true_range import AverageTrueRangeCalculator
from apollo.settings import NO_SIGNAL
from apollo.strategies.base_strategy import BaseStrategy


@pytest.mark.usefixtures("dataframe", "window_size")
def test__base_strategy__for_inserting_signal_column(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """Test Base Strategy for inserting "signal" column."""

    strategy = BaseStrategy(dataframe, window_size)

    assert "signal" in strategy._dataframe.columns  # noqa: SLF001
    assert strategy._dataframe["signal"].iloc[0] == NO_SIGNAL  # noqa: SLF001


@pytest.mark.usefixtures("dataframe", "window_size")
def test__base_strategy__for_calculating_volatility(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test Base Strategy for properly calculating volatility (ATR).

    Strategy should have "tr" and "atr" columns.
    """

    control_dataframe = dataframe.copy()

    at_calculator = AverageTrueRangeCalculator(control_dataframe, window_size)
    at_calculator.calculate_average_true_range()

    strategy = BaseStrategy(dataframe, window_size)

    assert "tr" in strategy._dataframe.columns  # noqa: SLF001
    assert "atr" in strategy._dataframe.columns  # noqa: SLF001
    pd.testing.assert_series_equal(control_dataframe["atr"], dataframe["atr"])


@pytest.mark.usefixtures("window_size")
def test__base_strategy__with_missing_parameters(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test Base Strategy validating missing parameters.

    Strategy should raise ValueError when parameter is missing.
    """

    strategy = BaseStrategy(
        dataframe=dataframe,
        window_size=window_size,
    )

    parameter_name = "missing_parameter"
    parameters: list[tuple[str, Any, Type]] = [(parameter_name, None, float)]
    exception_message = f"Parameter {parameter_name} is missing"

    with pytest.raises(
        ValueError,
        match=exception_message,
    ) as exception:
        strategy._validate_parameters(parameters)  # noqa: SLF001

    assert str(exception.value) == exception_message


@pytest.mark.usefixtures("window_size")
def test__base_strategy__with_invalid_parameters(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test Base Strategy validating invalid parameters.

    Strategy should raise TypeError when parameter is not of expected type.
    """

    strategy = BaseStrategy(
        dataframe=dataframe,
        window_size=window_size,
    )

    parameter_name = "invalid_parameter"
    exception_message = str(
        f"Parameter {parameter_name} is not of expected type {float.__name__}",
    )

    parameters: list[tuple[str, Any, Type]] = [(parameter_name, "", float)]

    with pytest.raises(
        TypeError,
        match=exception_message,
    ) as exception:
        strategy._validate_parameters(parameters)  # noqa: SLF001

    assert str(exception.value) == exception_message


@pytest.mark.usefixtures("window_size")
def test__base_strategy__for_throwing_error_when_modelling_method_is_not_implemented(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test Base Strategy for throwing NotImplementedError error.

    When model_trading_signals method is not implemented in subclass.
    """

    strategy = BaseStrategy(
        dataframe=dataframe,
        window_size=window_size,
    )

    exception_message = "Method model_trading_signals is not implemented"

    with pytest.raises(
        NotImplementedError,
        match=exception_message,
    ) as exception:
        strategy.model_trading_signals()

    assert str(exception.value) == exception_message
