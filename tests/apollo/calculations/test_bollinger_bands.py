import pandas as pd
import pytest

from apollo.calculations.bollinger_bands import BollingerBandsCalculator
from apollo.calculations.mcnicholl_moving_average import (
    McNichollMovingAverageCalculator,
)
from tests.fixtures.env_and_constants import CHANNEL_SD_SPREAD


@pytest.mark.usefixtures("dataframe", "window_size")
def test__calculate_bollinger_bands__for_correct_columns(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test calculate_bollinger_bands method for correct columns.

    Resulting dataframe must have columns "lb_band" and "ub_band".
    """

    mnma_calculator = McNichollMovingAverageCalculator(
        dataframe=dataframe,
        window_size=window_size,
    )

    mnma_calculator.calculate_mcnicholl_moving_average()

    bb_calculator = BollingerBandsCalculator(
        dataframe=dataframe,
        window_size=window_size,
        channel_sd_spread=CHANNEL_SD_SPREAD,
    )

    bb_calculator.calculate_bollinger_bands()

    assert "lb_band" in bb_calculator.dataframe.columns
    assert "ub_band" in bb_calculator.dataframe.columns


@pytest.mark.usefixtures("dataframe", "window_size")
def test__calculate_bollinger_bands__for_correct_rolling_window(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test calculate_bollinger_bands method for correct rolling window.

    Where N = WINDOW_SIZE.

    Resulting dataframe must skip WINDOW_SIZE - 1 rows for lb_band and ub_band columns
    Since Bollinger Bands calculation must have at least N rows to be calculated.
    """

    mnma_calculator = McNichollMovingAverageCalculator(
        dataframe=dataframe,
        window_size=window_size,
    )

    mnma_calculator.calculate_mcnicholl_moving_average()

    bb_calculator = BollingerBandsCalculator(
        dataframe=dataframe,
        window_size=window_size,
        channel_sd_spread=CHANNEL_SD_SPREAD,
    )

    bb_calculator.calculate_bollinger_bands()

    assert dataframe["lb_band"].isna().sum() == window_size - 1
    assert dataframe["ub_band"].isna().sum() == window_size - 1
