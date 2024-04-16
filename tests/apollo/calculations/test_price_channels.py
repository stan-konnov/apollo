import pandas as pd
import pytest

from apollo.calculations.price_channels import PriceChannelsCalculator

CHANNEL_SD_SPREAD = 1.0


@pytest.mark.usefixtures("dataframe")
@pytest.mark.usefixtures("window_size")
def test__calculate_price_channels__for_correct_columns(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test calculate_price_channels method for correct columns.

    Resulting dataframe must have columns
    "slope", "prev_slope", "l_bound", "u_bound", "lbf".
    """

    pc_calculator = PriceChannelsCalculator(
        dataframe=dataframe,
        window_size=window_size,
        channel_sd_spread=CHANNEL_SD_SPREAD,
    )

    pc_calculator.calculate_price_channels()

    assert "slope" in dataframe.columns
    assert "prev_slope" in dataframe.columns

    assert "l_bound" in dataframe.columns
    assert "u_bound" in dataframe.columns

    assert "lbf" in dataframe.columns


@pytest.mark.usefixtures("dataframe")
@pytest.mark.usefixtures("window_size")
def test__calculate_price_channels__for_correct_rolling_window(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test calculate_price_channels method for correct rolling window.

    Where N = WINDOW_SIZE.

    Resulting dataframe must skip WINDOW_SIZE - 1 rows for each column except
    "prev_slope", since channel calculation must have at least N rows to be calculated.

    Prev slope must skip WINDOW_SIZE rows since it is calculated by shifting "slope".
    """

    ignored_rows_count = window_size - 1

    pc_calculator = PriceChannelsCalculator(
        dataframe=dataframe,
        window_size=window_size,
        channel_sd_spread=CHANNEL_SD_SPREAD,
    )

    pc_calculator.calculate_price_channels()

    assert dataframe["slope"].isna().sum() == ignored_rows_count
    assert dataframe["prev_slope"].isna().sum() == window_size

    assert dataframe["l_bound"].isna().sum() == ignored_rows_count
    assert dataframe["u_bound"].isna().sum() == ignored_rows_count

    assert dataframe["lbf"].isna().sum() == ignored_rows_count


@pytest.mark.usefixtures("dataframe")
@pytest.mark.usefixtures("window_size")
def test__calculate_price_channels__for_correct_indices(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test calculate_price_channels method for correct indices.

    Since price channel calculation relies on using numerical indices
    for linear regression, dataframe must be reset before calculation;
    and reset back to date after calculation.

    Resulting dataframe must have "date" as index.
    """

    pc_calculator = PriceChannelsCalculator(
        dataframe=dataframe,
        window_size=window_size,
        channel_sd_spread=CHANNEL_SD_SPREAD,
    )

    pc_calculator.calculate_price_channels()


    assert dataframe.index.name == "date"
    assert dataframe.index.dtype == "datetime64[ns]"
