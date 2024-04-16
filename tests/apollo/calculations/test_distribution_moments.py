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


@pytest.mark.usefixtures("dataframe")
@pytest.mark.usefixtures("window_size")
def test__calculate_distribution_moments__for_correct_moments_calculation(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test calculate_distribution_moments method for correct moments calculation.

    Resulting dataframe must have correct values for each moment.
    """

    control_dataframe = dataframe.copy()

    rolling_window = control_dataframe["adj close"].rolling(window=window_size)

    control_dataframe["avg"] = rolling_window.mean()
    control_dataframe["std"] = rolling_window.std()

    control_dataframe["skew"] = rolling_window.skew()
    control_dataframe["kurt"] = rolling_window.kurt()

    control_dataframe["z_score"] = (
        (control_dataframe["adj close"] - control_dataframe["avg"]) /
        control_dataframe["std"]
    )

    dm_calculator = DistributionMomentsCalculator(
        dataframe=dataframe,
        window_size=window_size,
    )

    dm_calculator.calculate_distribution_moments()

    pd.testing.assert_series_equal(dataframe["avg"], control_dataframe["avg"])
    pd.testing.assert_series_equal(dataframe["std"], control_dataframe["std"])

    pd.testing.assert_series_equal(dataframe["skew"], control_dataframe["skew"])
    pd.testing.assert_series_equal(dataframe["kurt"], control_dataframe["kurt"])

    pd.testing.assert_series_equal(dataframe["z_score"], control_dataframe["z_score"])
