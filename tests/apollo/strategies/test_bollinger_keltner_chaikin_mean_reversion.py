import pandas as pd
import pytest

from apollo.calculations.average_true_range import AverageTrueRangeCalculator
from apollo.calculations.chaikin_accumulation_distribution import (
    ChaikinAccumulationDistributionCalculator,
)
from apollo.calculations.hull_moving_average import HullMovingAverageCalculator
from apollo.calculations.keltner_channel import KeltnerChannelCalculator
from apollo.settings import LONG_SIGNAL, SHORT_SIGNAL
from apollo.strategies.keltner_chaikin_trend_following import (
    KeltnerChaikinTrendFollowing,
)


@pytest.mark.usefixtures("dataframe", "window_size")
def test__bollinger_keltner_chaikin_mean_reversion__with_valid_parameters(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test Bollinger Keltner Chaikin Mean Reversion with valid parameters.

    Strategy should properly calculate trading signals.
    """

    volatility_multiplier = 0.5

    control_dataframe = dataframe.copy()
    control_dataframe["signal"] = 0

    atr_calculator = AverageTrueRangeCalculator(
        dataframe=control_dataframe,
        window_size=window_size,
    )
    atr_calculator.calculate_average_true_range()

    hma_calculator = HullMovingAverageCalculator(
        dataframe=control_dataframe,
        window_size=window_size,
    )
    hma_calculator.calculate_hull_moving_average()

    kc_calculator = KeltnerChannelCalculator(
        dataframe=control_dataframe,
        window_size=window_size,
        volatility_multiplier=volatility_multiplier,
    )
    kc_calculator.calculate_keltner_channel()

    cad_calculator = ChaikinAccumulationDistributionCalculator(
        dataframe=control_dataframe,
        window_size=window_size,
    )
    cad_calculator.calculate_chaikin_accumulation_distribution_line()

    control_dataframe.loc[
        (control_dataframe["adj close"] > control_dataframe["lkc_bound"])
        & (control_dataframe["adl"] > control_dataframe["prev_adl"]),
        "signal",
    ] = LONG_SIGNAL

    control_dataframe.loc[
        (control_dataframe["adj close"] < control_dataframe["ukc_bound"])
        & (control_dataframe["adl"] < control_dataframe["prev_adl"]),
        "signal",
    ] = SHORT_SIGNAL

    control_dataframe.dropna(inplace=True)

    bollinger_keltner_chaikin_mean_reversion = KeltnerChaikinTrendFollowing(
        dataframe=dataframe,
        window_size=window_size,
        volatility_multiplier=volatility_multiplier,
    )

    bollinger_keltner_chaikin_mean_reversion.model_trading_signals()

    pd.testing.assert_series_equal(dataframe["signal"], control_dataframe["signal"])
