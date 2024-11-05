import numpy as np
import pandas as pd
import pytest

from apollo.core.calculators.chaikin_accumulation_distribution import (
    ChaikinAccumulationDistributionCalculator,
)


@pytest.mark.usefixtures("dataframe", "window_size")
def test__calculate_chaikin_accumulation_distribution_line__for_correct_columns(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test calculate_chaikin_accumulation_distribution_line method for correct columns.

    Resulting dataframe must have columns "adl" and "prev_adl".
    """

    cad_calculator = ChaikinAccumulationDistributionCalculator(
        dataframe=dataframe,
        window_size=window_size,
    )
    cad_calculator.calculate_chaikin_accumulation_distribution_line()

    assert "adl" in dataframe.columns
    assert "prev_adl" in dataframe.columns


@pytest.mark.usefixtures("dataframe", "window_size")
def test__calculate_chaikin_accumulation_distribution_line__for_correct_rolling_window(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test calculate_chaikin_accumulation_distribution_line for correct rolling window.

    Where N = WINDOW_SIZE.

    Resulting dataframe must skip WINDOW_SIZE - 1 rows for adl column
    Since Chaikin Accumulation Distribution must have at least N rows to be calculated.

    Resulting dataframe must skip WINDOW_SIZE rows for prev_adl column
    Since previous AD line skips N + 1 rows due to shifting original AD line.
    """

    cad_calculator = ChaikinAccumulationDistributionCalculator(
        dataframe=dataframe,
        window_size=window_size,
    )
    cad_calculator.calculate_chaikin_accumulation_distribution_line()

    assert dataframe["adl"].isna().sum() == window_size - 1
    assert dataframe["prev_adl"].isna().sum() == window_size


@pytest.mark.usefixtures("dataframe", "window_size")
def test__calculate_chaikin_accumulation_distribution_line__for_correct_adl_calculation(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test calculate_chaikin_accumulation_distribution_line method for ADL calculation.

    Resulting "adl" and "prev_adl" columns must have correct values for each row.
    """

    accumulation_distribution_line = (
        np.full((1, window_size - 1), np.nan).flatten().tolist()
    )

    control_dataframe = dataframe.copy()

    control_dataframe["adj close"].rolling(window_size).apply(
        mimic_calc_adl,
        args=(
            control_dataframe,
            accumulation_distribution_line,
        ),
    )

    control_dataframe["adl"] = accumulation_distribution_line
    control_dataframe["prev_adl"] = control_dataframe["adl"].shift(1)

    cad_calculator = ChaikinAccumulationDistributionCalculator(
        dataframe=dataframe,
        window_size=window_size,
    )
    cad_calculator.calculate_chaikin_accumulation_distribution_line()

    pd.testing.assert_series_equal(dataframe["adl"], control_dataframe["adl"])
    pd.testing.assert_series_equal(dataframe["prev_adl"], control_dataframe["prev_adl"])


def mimic_calc_adl(
    series: pd.Series,
    dataframe: pd.DataFrame,
    accumulation_distribution_line: list[float],
) -> float:
    """
    Mimicry of Chaikin Accumulation Distribution calculation for testing purposes.

    Please see ChaikinAccumulationDistributionCalculator for
    detailed explanation of Chaikin Accumulation Distribution calculation.
    """

    rolling_df = dataframe.loc[series.index]

    money_flow_multiplier = (
        (rolling_df["adj close"] - rolling_df["adj low"])
        - (rolling_df["adj high"] - rolling_df["adj close"])
    ) / (rolling_df["adj high"] - rolling_df["adj low"])

    money_flow_volume = money_flow_multiplier * rolling_df["adj volume"]

    accumulation_distribution = money_flow_volume.cumsum()

    accumulation_distribution_line.append(
        accumulation_distribution.iloc[-1],
    )

    return 0.0
