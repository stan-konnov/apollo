import pandas as pd
import pytest

from apollo.calculations.average_true_range import AverageTrueRangeCalculator
from apollo.calculations.bollinger_bands import BollingerBandsCalculator
from apollo.calculations.chaikin_accumulation_distribution import (
    ChaikinAccumulationDistributionCalculator,
)
from apollo.calculations.keltner_channel import KeltnerChannelCalculator
from apollo.calculations.mcnicholl_moving_average import (
    McNichollMovingAverageCalculator,
)
from apollo.settings import LONG_SIGNAL, SHORT_SIGNAL
from apollo.strategies.bollinger_keltner_chaikin_mean_reversion import (
    BollingerKeltnerChaikinMeanReversion,
)
from tests.fixtures.env_and_constants import CHANNEL_SD_SPREAD


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

    mnma_calculator = McNichollMovingAverageCalculator(
        dataframe=control_dataframe,
        window_size=window_size,
    )
    mnma_calculator.calculate_mcnicholl_moving_average()

    bb_calculator = BollingerBandsCalculator(
        dataframe=control_dataframe,
        window_size=window_size,
        channel_sd_spread=CHANNEL_SD_SPREAD,
    )
    bb_calculator.calculate_bollinger_bands()

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
        (
            (control_dataframe["adj close"] < control_dataframe["lb_band"])
            & (control_dataframe["lb_band"] > control_dataframe["lkc_bound"])
            & (control_dataframe["ub_band"] < control_dataframe["ukc_bound"])
        )
        | (control_dataframe["adl"] < control_dataframe["prev_adl"]),
        "signal",
    ] = LONG_SIGNAL

    control_dataframe.loc[
        (
            (control_dataframe["adj close"] > control_dataframe["ub_band"])
            & (control_dataframe["lb_band"] > control_dataframe["lkc_bound"])
            & (control_dataframe["ub_band"] < control_dataframe["ukc_bound"])
        )
        | (control_dataframe["adl"] > control_dataframe["prev_adl"]),
        "signal",
    ] = SHORT_SIGNAL

    control_dataframe.dropna(inplace=True)

    bollinger_keltner_chaikin_mean_reversion = BollingerKeltnerChaikinMeanReversion(
        dataframe=dataframe,
        window_size=window_size,
        volatility_multiplier=volatility_multiplier,
        channel_sd_spread=CHANNEL_SD_SPREAD,
    )

    bollinger_keltner_chaikin_mean_reversion.model_trading_signals()

    pd.testing.assert_series_equal(dataframe["signal"], control_dataframe["signal"])
