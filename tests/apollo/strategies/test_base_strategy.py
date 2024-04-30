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

    assert "signal" in strategy.dataframe.columns
    assert strategy.dataframe["signal"].iloc[0] == NO_SIGNAL


@pytest.mark.usefixtures("dataframe", "window_size")
def test__base_strategy__for_calculating_volatility(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """Test Base Strategy for properly calculating volatility (ATR)."""

    control_dataframe = dataframe.copy()

    at_calculator = AverageTrueRangeCalculator(control_dataframe, window_size)
    at_calculator.calculate_average_true_range()

    strategy = BaseStrategy(dataframe, window_size)

    assert "atr" in strategy.dataframe.columns

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

    parameters: list[tuple[str, Any, Type]] = [("missing_parameter", None, float)]

    with pytest.raises(
        ValueError,
        match="Parameter missing_parameter is missing",
    ) as exception:
        strategy._validate_parameters(parameters)  # noqa: SLF001

    assert str(exception.value) == "Parameter missing_parameter is missing"


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
        f"Parameter {parameter_name} is "
        f"not of expected type {float.__name__}",
    )

    parameters: list[tuple[str, Any, Type]] = [(parameter_name, "", float)]

    with pytest.raises(
        TypeError,
        match=exception_message,
    ) as exception:
        strategy._validate_parameters(parameters)  # noqa: SLF001

    assert str(exception.value) == exception_message
