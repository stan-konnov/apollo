import pandas as pd
import pytest

from apollo.calculations.distribution_moments import DistributionMomentsCalculator


@pytest.mark.usefixtures("dataframe")
@pytest.mark.usefixtures("window_size")
def test__calculate_distribution_moments__for_correct_columns(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test calculate_distribution_moments method for correct columns.

    Resulting dataframe must have "avg", "std", "skew", "kurt", and "z_score" columns.
    """

    dm_calculator = DistributionMomentsCalculator(
        dataframe=dataframe,
        window_size=window_size,
    )

    dm_calculator.calculate_distribution_moments()

    assert "avg" in dataframe.columns
    assert "std" in dataframe.columns
    assert "skew" in dataframe.columns
    assert "kurt" in dataframe.columns
    assert "z_score" in dataframe.columns


@pytest.mark.usefixtures("dataframe")
@pytest.mark.usefixtures("window_size")
def test__calculate_distribution_moments__for_correct_rolling_window(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test calculate_distribution_moments method for correct rolling window.

    Where N = WINDOW_SIZE.

    Resulting dataframe must skip WINDOW_SIZE - 1 rows for each column
    Since each moment calculation has to have at least N rows to be calculated.
    """

    ignored_rows_count = window_size - 1

    dm_calculator = DistributionMomentsCalculator(
        dataframe=dataframe,
        window_size=window_size,
    )

    dm_calculator.calculate_distribution_moments()

    assert dataframe["avg"].isna().sum() == ignored_rows_count
    assert dataframe["std"].isna().sum() == ignored_rows_count
    assert dataframe["skew"].isna().sum() == ignored_rows_count
    assert dataframe["kurt"].isna().sum() == ignored_rows_count
    assert dataframe["z_score"].isna().sum() == ignored_rows_count

