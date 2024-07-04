import pandas as pd
import pytest

from apollo.calculations.average_true_range import AverageTrueRangeCalculator


@pytest.mark.usefixtures("dataframe", "window_size")
def test__calculate_average_true_range__for_correct_columns(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test calculate_average_true_range method for correct columns.

    Resulting dataframe must have columns "tr" and "atr".
    Resulting dataframe must drop "prev_close" column.
    """

    atr_calculator = AverageTrueRangeCalculator(
        dataframe=dataframe,
        window_size=window_size,
    )

    atr_calculator.calculate_average_true_range()

    assert "tr" in atr_calculator.dataframe.columns
    assert "atr" in atr_calculator.dataframe.columns
    assert "prev_close" not in atr_calculator.dataframe.columns


@pytest.mark.usefixtures("dataframe", "window_size")
def test__calculate_average_true_range__for_correct_rolling_window(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test calculate_average_true_range method for correct rolling window.

    Where N = WINDOW_SIZE.

    Resulting dataframe must skip WINDOW_SIZE - 1 rows for TR column
    Since TR calculation must have at least N rows to calculate TR.

    Resulting dataframe must skip (WINDOW_SIZE - 1) * 2 rows for ATR column
    Since ATR calculation must have at least N rows of valid TR to calculate ATR.
    """

    atr_calculator = AverageTrueRangeCalculator(
        dataframe=dataframe,
        window_size=window_size,
    )

    atr_calculator.calculate_average_true_range()

    assert dataframe["tr"].isna().sum() == window_size - 1
    assert dataframe["atr"].isna().sum() == (window_size - 1) * 2


@pytest.mark.usefixtures("dataframe", "window_size")
def test__calculate_average_true_range__for_correct_tr_calculation(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test calculate_average_true_range method for correct TR calculation.

    Resulting TR column must have correct values for each row.
    """

    control_dataframe = dataframe.copy()
    control_dataframe["prev_close"] = control_dataframe["close"].shift()

    control_dataframe["tr"] = (
        control_dataframe["close"]
        .rolling(
            window_size,
        )
        .apply(
            mimic_calc_tr,
            args=(control_dataframe,),
        )
    )

    atr_calculator = AverageTrueRangeCalculator(
        dataframe=dataframe,
        window_size=window_size,
    )

    atr_calculator.calculate_average_true_range()

    pd.testing.assert_series_equal(dataframe["tr"], control_dataframe["tr"])


@pytest.mark.usefixtures("dataframe", "window_size")
def test__calculate_average_true_range__for_correct_atr_calculation(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test calculate_average_true_range method for correct ATR calculation.

    Resulting ATR column must have correct values for each row.
    """

    control_dataframe = dataframe.copy()
    control_dataframe["prev_close"] = control_dataframe["close"].shift()

    control_dataframe["tr"] = (
        control_dataframe["close"]
        .rolling(
            window_size,
        )
        .apply(
            mimic_calc_tr,
            args=(control_dataframe,),
        )
    )

    control_dataframe["atr"] = (
        control_dataframe["tr"]
        .ewm(
            alpha=1 / window_size,
            min_periods=window_size,
            adjust=False,
        )
        .mean()
    )

    atr_calculator = AverageTrueRangeCalculator(
        dataframe=dataframe,
        window_size=window_size,
    )

    atr_calculator.calculate_average_true_range()

    pd.testing.assert_series_equal(dataframe["atr"], control_dataframe["atr"])


def mimic_calc_tr(series: pd.Series, dataframe: pd.DataFrame) -> None:
    """
    Mimicry of TR calculation for testing purposes.

    Please see AverageTrueRangeCalculator for detailed explanation of TR calculation.
    """

    rolling_df = dataframe.loc[series.index]

    high = rolling_df.iloc[-1]["high"]
    low = rolling_df.iloc[-1]["low"]
    prev_close = rolling_df.iloc[-1]["prev_close"]

    true_range = [high - low, high - prev_close, prev_close - low]

    return max([abs(tr) for tr in true_range])
