import pandas as pd
import pytest

from apollo.calculations.average_directional_movement_index import (
    AverageDirectionalMovementIndexCalculator,
)
from apollo.calculations.average_true_range import AverageTrueRangeCalculator
from tests.utils.precalculate_shared_values import precalculate_shared_values


@pytest.mark.usefixtures("dataframe", "window_size")
def test__calculate_average_directional_movement_index__for_correct_columns(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test calculate_average_directional_movement_index method for correct columns.

    Resulting dataframe must have the following columns:
    "dx", "pdi", "mdi", "prev_pdi", "prev_mdi", "dx_adx_ampl", "prev_dx_adx_ampl".

    Resulting dataframe must not have the following columns:
    "prev_low", "prev_high", "pdm", "mdm", "adx".
    """

    dataframe = precalculate_shared_values(dataframe)

    atr_calculator = AverageTrueRangeCalculator(
        dataframe=dataframe,
        window_size=window_size,
    )
    atr_calculator.calculate_average_true_range()

    adx_calculator = AverageDirectionalMovementIndexCalculator(
        dataframe=dataframe,
        window_size=window_size,
    )
    adx_calculator.calculate_average_directional_movement_index()

    assert "dx" in dataframe.columns
    assert "pdi" in dataframe.columns
    assert "mdi" in dataframe.columns
    assert "prev_pdi" in dataframe.columns
    assert "prev_mdi" in dataframe.columns
    assert "dx_adx_ampl" in dataframe.columns
    assert "prev_dx_adx_ampl" in dataframe.columns

    assert "pdm" not in dataframe.columns
    assert "mdm" not in dataframe.columns
    assert "adx" not in dataframe.columns
    assert "prev_low" not in dataframe.columns
    assert "prev_high" not in dataframe.columns


@pytest.mark.usefixtures("dataframe", "window_size")
def test__calculate_average_directional_movement_index__for_correct_rolling_window(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test calculate_average_directional_movement_index method for correct rolling window.

    Where N = WINDOW_SIZE.

    Resulting dataframe must skip (WINDOW_SIZE - 1) * 3 rows
    for dx_adx_ampl and (WINDOW_SIZE - 1) * 2 rows for pdi, mdi.
    Since Average Directional Movement Index Amplitude is calculated
    based on ADX, and, therefore PDI and MDI that are calculated based on ATR,
    which calculation must have at least N rows of valid True Range calculation.
    """

    dataframe = precalculate_shared_values(dataframe)

    atr_calculator = AverageTrueRangeCalculator(
        dataframe=dataframe,
        window_size=window_size,
    )
    atr_calculator.calculate_average_true_range()

    adx_calculator = AverageDirectionalMovementIndexCalculator(
        dataframe=dataframe,
        window_size=window_size,
    )
    adx_calculator.calculate_average_directional_movement_index()

    assert dataframe["pdi"].isna().sum() == (window_size - 1) * 2
    assert dataframe["mdi"].isna().sum() == (window_size - 1) * 2
    assert dataframe["dx_adx_ampl"].isna().sum() == (window_size - 1) * 3
