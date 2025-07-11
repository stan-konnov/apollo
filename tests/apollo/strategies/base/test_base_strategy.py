from typing import Any

import pandas as pd
import pytest

from apollo.settings import NO_SIGNAL
from apollo.strategies.base.base_strategy import BaseStrategy


@pytest.mark.usefixtures("dataframe", "window_size")
def test__base_strategy__for_inserting_signal_column(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """Test Base Strategy for inserting "signal" column."""

    BaseStrategy(dataframe, window_size)

    assert "signal" in dataframe.columns
    assert all(dataframe["signal"] == NO_SIGNAL)


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
    parameters: list[tuple[str, Any, type]] = [(parameter_name, None, float)]
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

    parameters: list[tuple[str, Any, type]] = [(parameter_name, "", float)]

    with pytest.raises(
        TypeError,
        match=exception_message,
    ) as exception:
        strategy._validate_parameters(parameters)  # noqa: SLF001

    assert str(exception.value) == exception_message


@pytest.mark.usefixtures("window_size")
def test__base_strategy__for_raising_error_when_modelling_method_is_not_implemented(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test Base Strategy for raising NotImplementedError error.

    When model_trading_signals method is not implemented in subclass.
    """

    strategy = BaseStrategy(
        dataframe=dataframe,
        window_size=window_size,
    )

    exception_message = "Method model_trading_signals is not implemented."

    with pytest.raises(
        NotImplementedError,
        match=exception_message,
    ) as exception:
        strategy.model_trading_signals()

    assert str(exception.value) == exception_message


@pytest.mark.usefixtures("dataframe", "window_size")
def test__base_strategy__for_precalculating_shared_values(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test Base Strategy for precalculating shared values.

    Dataframe should have "prev_close" column.
    """

    control_dataframe = dataframe.copy()

    control_dataframe["prev_close"] = control_dataframe["adj close"].shift(1)

    strategy = BaseStrategy(dataframe, window_size)

    strategy._precalculate_shared_values()  # noqa: SLF001

    assert "prev_close" in dataframe.columns

    pd.testing.assert_series_equal(
        dataframe["prev_close"],
        control_dataframe["prev_close"],
    )
