import numpy as np
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


@pytest.mark.usefixtures("dataframe", "window_size")
def test__calculate_bollinger_bands__for_correct_bb_calculation(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test calculate_bollinger_bands method for correct Bollinger Bands calculation.

    Resulting "lb_band" and "ub_band" columns must have correct values for each row.
    """

    lb_band = np.full((1, window_size - 1), np.nan).flatten().tolist()
    ub_band = np.full((1, window_size - 1), np.nan).flatten().tolist()

    control_dataframe = dataframe.copy()

    mnma_calculator = McNichollMovingAverageCalculator(
        dataframe=control_dataframe,
        window_size=window_size,
    )
    mnma_calculator.calculate_mcnicholl_moving_average()

    control_dataframe["adj close"].rolling(window_size).apply(
        mimic_calc_bands,
        args=(
            control_dataframe,
            lb_band,
            ub_band,
            CHANNEL_SD_SPREAD,
        ),
    )

    control_dataframe["lb_band"] = lb_band
    control_dataframe["ub_band"] = ub_band

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

    pd.testing.assert_series_equal(dataframe["lb_band"], control_dataframe["lb_band"])
    pd.testing.assert_series_equal(dataframe["ub_band"], control_dataframe["ub_band"])


def mimic_calc_bands(
    series: pd.Series,
    dataframe: pd.DataFrame,
    lb_band: list[float],
    ub_band: list[float],
    channel_sd_spread: float,
) -> float:
    """
    Mimicry of Bollinger Bands calculation for testing purposes.

    Please see BollingerBandsCalculator for
    detailed explanation of Bollinger Bands calculation.
    """

    rolling_df = dataframe.loc[series.index]

    mnma = rolling_df["mnma"][-1]
    std = series.std()

    l_band = mnma - std * channel_sd_spread
    u_band = mnma + std * channel_sd_spread

    lb_band.append(l_band)
    ub_band.append(u_band)

    return 0.0
