import pandas as pd
import pytest

from apollo.core.calculations.average_directional_movement_index import (
    AverageDirectionalMovementIndexCalculator,
)
from apollo.core.calculations.average_true_range import AverageTrueRangeCalculator
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


@pytest.mark.usefixtures("dataframe", "window_size")
def test__calculate_average_directional_movement_index__for_correct_calculation(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test calculate_average_directional_movement_index method for correct calculation.

    Following columns must have correct values for each row:
    "dx", "pdi", "mdi", "prev_pdi", "prev_mdi", "dx_adx_ampl", "prev_dx_adx_ampl".
    """

    dataframe = precalculate_shared_values(dataframe)

    control_dataframe = dataframe.copy()

    atr_calculator = AverageTrueRangeCalculator(
        dataframe=control_dataframe,
        window_size=window_size,
    )
    atr_calculator.calculate_average_true_range()

    control_dataframe["prev_low"] = control_dataframe["adj low"].shift(1)
    control_dataframe["prev_high"] = control_dataframe["adj high"].shift(1)

    control_dataframe["mdm"] = (
        control_dataframe["adj low"] - control_dataframe["prev_low"]
    )
    control_dataframe["pdm"] = (
        control_dataframe["adj high"] - control_dataframe["prev_high"]
    )

    control_dataframe["pdm"] = (
        control_dataframe["pdm"]
        .ewm(
            alpha=1 / window_size,
            min_periods=window_size,
            adjust=False,
        )
        .mean()
    )
    control_dataframe["mdm"] = (
        control_dataframe["mdm"]
        .ewm(
            alpha=1 / window_size,
            min_periods=window_size,
            adjust=False,
        )
        .mean()
    )

    control_dataframe["pdi"] = control_dataframe["pdm"] / control_dataframe["atr"]
    control_dataframe["mdi"] = control_dataframe["mdm"] / control_dataframe["atr"]

    control_dataframe["dx"] = 100 * (
        abs(control_dataframe["pdi"] - control_dataframe["mdi"])
        / (control_dataframe["pdi"] + control_dataframe["mdi"])
    )

    control_dataframe["adx"] = (
        control_dataframe["dx"]
        .ewm(
            alpha=1 / window_size,
            min_periods=window_size,
            adjust=False,
        )
        .mean()
    )

    control_dataframe["dx_adx_ampl"] = abs(control_dataframe["dx"]) - abs(
        control_dataframe["adx"],
    )

    control_dataframe["prev_pdi"] = control_dataframe["pdi"].shift(1)
    control_dataframe["prev_mdi"] = control_dataframe["mdi"].shift(1)

    control_dataframe["prev_dx"] = control_dataframe["dx"].shift(1)
    control_dataframe["prev_dx_adx_ampl"] = control_dataframe["dx_adx_ampl"].shift(1)

    control_dataframe.drop(
        columns=["prev_low", "prev_high", "mdm", "pdm", "adx"],
        inplace=True,
    )

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

    pd.testing.assert_series_equal(dataframe["dx"], control_dataframe["dx"])

    pd.testing.assert_series_equal(dataframe["pdi"], control_dataframe["pdi"])
    pd.testing.assert_series_equal(dataframe["mdi"], control_dataframe["mdi"])

    pd.testing.assert_series_equal(dataframe["prev_pdi"], control_dataframe["prev_pdi"])
    pd.testing.assert_series_equal(dataframe["prev_mdi"], control_dataframe["prev_mdi"])

    pd.testing.assert_series_equal(
        dataframe["dx_adx_ampl"],
        control_dataframe["dx_adx_ampl"],
    )
    pd.testing.assert_series_equal(
        dataframe["prev_dx_adx_ampl"],
        control_dataframe["prev_dx_adx_ampl"],
    )
