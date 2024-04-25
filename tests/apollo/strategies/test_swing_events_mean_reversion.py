import pandas as pd
import pytest

from apollo.calculations.swing_events import SwingEventsCalculator
from apollo.settings import LONG_SIGNAL, SHORT_SIGNAL
from apollo.strategies.swing_events_mean_reversion import SwingEventsMeanReversion


@pytest.mark.usefixtures("dataframe", "window_size")
def test__swing_events_mean_reversion__with_missing_parameters(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test Swing Events Mean Reversion with missing parameters.

    Strategy should raise ValueError when parameter is missing.
    """

    invalid_param_set = {
        "swing_filter": None,
    }

    with pytest.raises(
        ValueError,
        match="Parameter swing_filter is missing",
    ) as exception:
        SwingEventsMeanReversion(
            dataframe=dataframe,
            window_size=window_size,
            swing_filter=invalid_param_set.get("swing_filter"),  # type: ignore[assignment]
        )

    assert str(exception.value) == "Parameter swing_filter is missing"


@pytest.mark.usefixtures("dataframe", "window_size")
def test__swing_events_mean_reversion__with_invalid_parameters(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test Swing Events Mean Reversion with invalid parameters.

    Strategy should raise TypeError when parameter is not of expected type.
    """

    invalid_param_set = {
        "swing_filter": "invalid",
    }

    exception_message = str(
        "Parameter swing_filter is "
        f"not of expected type {float.__name__}",
    )

    with pytest.raises(
        TypeError,
        match=exception_message,
    ) as exception:
        SwingEventsMeanReversion(
            dataframe=dataframe,
            window_size=window_size,
            swing_filter=invalid_param_set.get("swing_filter"),  # type: ignore[assignment]
        )

    assert str(exception.value) == exception_message


@pytest.mark.usefixtures("dataframe", "window_size")
def test__swing_events_mean_reversion__with_valid_parameters(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test Swing Events Mean Reversion with valid parameters.

    Strategy should have relevant columns: "signal", "se".

    Strategy should properly calculate trading signals.
    """

    swing_filter = 0.01

    control_dataframe = dataframe.copy()
    control_dataframe["signal"] = 0

    se_calculator = SwingEventsCalculator(
        dataframe=control_dataframe,
        window_size=window_size,
        swing_filter=swing_filter,
    )
    se_calculator.calculate_swing_events()

    control_dataframe.loc[
        control_dataframe["se"] == se_calculator.DOWN_SWING,
        "signal",
    ] = LONG_SIGNAL

    control_dataframe.loc[
        control_dataframe["se"] == se_calculator.UP_SWING,
        "signal",
    ] = SHORT_SIGNAL

    control_dataframe.dropna(inplace=True)

    swing_events_mean_reversion = SwingEventsMeanReversion(
        dataframe=dataframe,
        window_size=window_size,
        swing_filter=swing_filter,
    )

    swing_events_mean_reversion.model_trading_signals()

    assert "signal" in swing_events_mean_reversion.dataframe.columns
    assert "se" in swing_events_mean_reversion.dataframe.columns

    pd.testing.assert_series_equal(dataframe["signal"], control_dataframe["signal"])
