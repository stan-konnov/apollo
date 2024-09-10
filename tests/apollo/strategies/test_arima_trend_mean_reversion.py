import pandas as pd
import pytest

from apollo.calculations.average_true_range import AverageTrueRangeCalculator
from apollo.calculations.models.arima_regression import ARIMARegressionModelCalculator
from apollo.settings import LONG_SIGNAL, SHORT_SIGNAL
from apollo.strategies.arima_trend_mean_reversion import ARIMATrendMeanReversion
from tests.utils.precalculate_shared_values import precalculate_shared_values


@pytest.mark.usefixtures("dataframe", "window_size")
def test__arima_trend_mean_reversion__with_valid_parameters(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test ARIMA Trend Mean Reversion with valid parameters.

    Strategy should properly calculate trading signals.
    """

    dataframe = precalculate_shared_values(dataframe)

    control_dataframe = dataframe.copy()
    control_dataframe["signal"] = 0

    atr_calculator = AverageTrueRangeCalculator(
        dataframe=control_dataframe,
        window_size=window_size,
    )
    atr_calculator.calculate_average_true_range()

    arm_calculator = ARIMARegressionModelCalculator(
        dataframe=control_dataframe,
        window_size=window_size,
    )
    arm_calculator.forecast_trend_periods()

    control_dataframe.loc[
        control_dataframe["adj close"] < control_dataframe["artf"],
        "signal",
    ] = LONG_SIGNAL
    control_dataframe.loc[
        control_dataframe["adj close"] > control_dataframe["artf"],
        "signal",
    ] = SHORT_SIGNAL

    control_dataframe.dropna(inplace=True)

    arima_trend_mean_reversion = ARIMATrendMeanReversion(
        dataframe=dataframe,
        window_size=window_size,
    )

    arima_trend_mean_reversion.model_trading_signals()

    pd.testing.assert_series_equal(dataframe["signal"], control_dataframe["signal"])
