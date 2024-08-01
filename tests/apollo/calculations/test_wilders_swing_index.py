import pandas as pd
import pytest

from apollo.calculations.wilders_swing_index import WildersSwingIndexCalculator


@pytest.mark.usefixtures("dataframe", "window_size")
def test__calculate_swing_index__for_correct_columns(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test calculate_swing_index method for correct columns.

    Resulting dataframe must have "sp" column.
    Resulting dataframe must not have "si", "asi", "prev_open", "prev_close" columns.
    """

    wsi_calculator = WildersSwingIndexCalculator(
        dataframe=dataframe,
        window_size=window_size,
    )

    wsi_calculator.calculate_swing_index()

    assert "sp" in dataframe.columns
    assert "si" not in dataframe.columns
    assert "asi" not in dataframe.columns
    assert "prev_open" not in dataframe.columns
    assert "prev_close" not in dataframe.columns


@pytest.mark.usefixtures("dataframe", "window_size")
def test__calculate_swing_index__for_correct_rolling_window(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test calculate_swing_index method for correct rolling window.

    Where N = WINDOW_SIZE.

    Resulting dataframe must skip WINDOW_SIZE rows for SP column
    Since SP calculation relies on 3 consecutive ASI values,
    and, in such, only available after first N rows.
    """

    wsi_calculator = WildersSwingIndexCalculator(
        dataframe=dataframe,
        window_size=window_size,
    )

    wsi_calculator.calculate_swing_index()

    assert dataframe["sp"].isna().sum() == window_size


@pytest.mark.usefixtures("dataframe", "window_size")
def test__calc_wtr__with_invalid_base_calculation(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test calc_wtr method with invalid base calculation.

    The provided value for calculation of Weighted True Range is invalid.

    WildersSwingIndexCalculator must raise ValueError if base calculation is invalid.
    """

    wsi_calculator = WildersSwingIndexCalculator(
        dataframe=dataframe,
        window_size=window_size,
    )

    exception_message = "Provided diff_index is invalid. Base calculation is faulty."

    with pytest.raises(
        ValueError,
        match=exception_message,
    ) as exception:
        wsi_calculator._calc_wtr(999, 1, 1, 1, 1)  # noqa: SLF001

    assert str(exception.value) == exception_message
