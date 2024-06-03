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
