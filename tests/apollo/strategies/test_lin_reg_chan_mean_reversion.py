import pandas as pd
import pytest

from apollo.calculations.linear_regression_channel import (
    LinearRegressionChannelCalculator,
)
from apollo.settings import LONG_SIGNAL, SHORT_SIGNAL
from apollo.strategies.lin_reg_chan_mean_reversion import (
    LinearRegressionChannelMeanReversion,
)


@pytest.mark.usefixtures("dataframe", "window_size")
def test__lin_reg_chan_mean_reversion__with_missing_parameters(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test Skewness Kurtosis Volatility Trend Following with missing parameters.

    Strategy should raise ValueError when parameter is missing.
    """

    invalid_param_set = {
        "channel_sd_spread": None,
    }

    with pytest.raises(
        ValueError,
        match="Parameter channel_sd_spread is missing",
    ) as exception:
        LinearRegressionChannelMeanReversion(
            dataframe=dataframe,
            window_size=window_size,
            channel_sd_spread=invalid_param_set.get("channel_sd_spread"),  # type: ignore[assignment]
        )

    assert str(exception.value) == "Parameter channel_sd_spread is missing"


@pytest.mark.usefixtures("dataframe", "window_size")
def test__lin_reg_chan_mean_reversion__with_invalid_parameters(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test Linear Regression Channel Mean Reversion with invalid parameters.

    Strategy should raise TypeError when parameter is not of expected type.
    """

    invalid_param_set = {
        "channel_sd_spread": "invalid",
    }

    exception_message = str(
        "Parameter channel_sd_spread is "
        f"not of expected type {float.__name__}",
    )

    with pytest.raises(
        TypeError,
        match=exception_message,
    ) as exception:
        LinearRegressionChannelMeanReversion(
            dataframe=dataframe,
            window_size=window_size,
            channel_sd_spread=invalid_param_set.get("channel_sd_spread"),  # type: ignore[assignment]
        )

    assert str(exception.value) == exception_message


@pytest.mark.usefixtures("dataframe", "window_size")
def test__lin_reg_chan_mean_reversion__with_valid_parameters(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test Linear Regression Channel Mean Reversion with valid parameters.

    Strategy should have relevant columns:
    "signal", "l_bound", "u_bound", "slope", "prev_slope".

    Strategy should properly calculate trading signals.
    """

    channel_sd_spread = 0.5

    control_dataframe = dataframe.copy()
    control_dataframe["signal"] = 0

    lrc_calculator = LinearRegressionChannelCalculator(
        dataframe=control_dataframe,
        window_size=window_size,
        channel_sd_spread=channel_sd_spread,
    )
    lrc_calculator.calculate_linear_regression_channel()

    long = (control_dataframe["adj close"] <= control_dataframe["l_bound"]) & (
        control_dataframe["slope"] <= control_dataframe["prev_slope"]
    )
    control_dataframe.loc[long, "signal"] = LONG_SIGNAL

    short = (control_dataframe["adj close"] >= control_dataframe["u_bound"]) & (
        control_dataframe["slope"] >= control_dataframe["prev_slope"]
    )
    control_dataframe.loc[short, "signal"] = SHORT_SIGNAL

    control_dataframe.dropna(inplace=True)

    lin_reg_chan_mean_reversion = LinearRegressionChannelMeanReversion(
        dataframe=dataframe,
        window_size=window_size,
        channel_sd_spread=channel_sd_spread,
    )

    lin_reg_chan_mean_reversion.model_trading_signals()

    assert "signal" in lin_reg_chan_mean_reversion.dataframe.columns

    assert "l_bound" in lin_reg_chan_mean_reversion.dataframe.columns
    assert "u_bound" in lin_reg_chan_mean_reversion.dataframe.columns

    assert "slope" in lin_reg_chan_mean_reversion.dataframe.columns
    assert "prev_slope" in lin_reg_chan_mean_reversion.dataframe.columns

    pd.testing.assert_series_equal(dataframe["signal"], control_dataframe["signal"])
