import pandas as pd
import pytest

from apollo.strategies.lin_reg_chan_mean_reversion import (
    LinearRegressionChannelMeanReversion,
)


@pytest.mark.usefixtures("dataframe", "window_size")
def test__skew_kurt_vol_trend_following__with_missing_parameters(
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
