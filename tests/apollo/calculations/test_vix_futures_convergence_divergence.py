import pandas as pd
import pytest

from apollo.calculations.vix_futures_convergence_divergence import (
    VixFuturesConvergenceDivergenceCalculator,
)
from apollo.settings import MISSING_DATA_PLACEHOLDER


@pytest.mark.usefixtures("enhanced_dataframe", "window_size")
def test__calculate_vix_futures_convergence_divergence__for_correct_columns(
    enhanced_dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test calculate_vix_futures_convergence_divergence method for correct columns.

    Resulting dataframe must have "vix_spf_pct_diff" and "prev_vix_spf_pct_diff".
    Resulting dataframe must drop "vix_pct_change" and "spf_pct_change" columns.
    """

    vfcd_calculator = VixFuturesConvergenceDivergenceCalculator(
        dataframe=enhanced_dataframe,
        window_size=window_size,
    )

    vfcd_calculator.calculate_vix_futures_convergence_divergence()

    assert "vix_spf_pct_diff" in enhanced_dataframe.columns
    assert "prev_vix_spf_pct_diff" in enhanced_dataframe.columns
    assert "vix_pct_change" not in enhanced_dataframe.columns
    assert "spf_pct_change" not in enhanced_dataframe.columns


@pytest.mark.usefixtures("enhanced_dataframe", "window_size")
def test__calculate_vix_futures_convergence_divergence__for_correct_vixep_calculation(
    enhanced_dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test calculate_vix_futures_convergence_divergence method for correct calculation.

    Resulting "vix_spf_pct_diff" column must have correct values for each row.
    """

    control_dataframe = enhanced_dataframe.copy()

    control_dataframe["vix_pct_change"] = 0.0
    control_dataframe["spf_pct_change"] = 0.0
    control_dataframe["vix_spf_pct_diff"] = 0.0

    control_dataframe.loc[
        control_dataframe["vix close"] != MISSING_DATA_PLACEHOLDER,
        "vix_pct_change",
    ] = control_dataframe["vix close"].pct_change()

    control_dataframe.loc[
        control_dataframe["spf close"] != MISSING_DATA_PLACEHOLDER,
        "spf_pct_change",
    ] = control_dataframe["spf close"].pct_change()

    control_dataframe["vix_spf_pct_diff"] = (
        control_dataframe["vix_pct_change"] - control_dataframe["spf_pct_change"]
    )

    control_dataframe["prev_vix_spf_pct_diff"] = control_dataframe[
        "vix_spf_pct_diff"
    ].shift(1)

    control_dataframe.drop(
        columns=["vix_pct_change", "spf_pct_change"],
        inplace=True,
    )

    vfcd_calculator = VixFuturesConvergenceDivergenceCalculator(
        dataframe=enhanced_dataframe,
        window_size=window_size,
    )

    vfcd_calculator.calculate_vix_futures_convergence_divergence()

    pd.testing.assert_series_equal(
        control_dataframe["vix_spf_pct_diff"],
        enhanced_dataframe["vix_spf_pct_diff"],
    )


@pytest.mark.usefixtures("enhanced_dataframe", "window_size")
def test__calculate_vix_futures_convergence_divergence__for_missing_data_calculation(
    enhanced_dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test calculate_vix_futures_convergence_divergence for missing data calculation.

    Resulting "vix_spf_pct_diff" column must have 0.0 for rows with missing data.
    Resulting "vix_spf_pct_diff" column must have correct values for rows with data.
    """

    enhanced_dataframe.reset_index(inplace=True)

    # Mimic missing data for "vix close" and "spf close" columns
    enhanced_dataframe.loc[0:5, "vix close"] = MISSING_DATA_PLACEHOLDER
    enhanced_dataframe.loc[0:5, "spf close"] = MISSING_DATA_PLACEHOLDER

    control_dataframe = enhanced_dataframe.copy()

    control_dataframe["vix_pct_change"] = 0.0
    control_dataframe["spf_pct_change"] = 0.0
    control_dataframe["vix_spf_pct_diff"] = 0.0

    control_dataframe.loc[
        control_dataframe["vix close"] != MISSING_DATA_PLACEHOLDER,
        "vix_pct_change",
    ] = control_dataframe["vix close"].pct_change()

    control_dataframe.loc[
        control_dataframe["spf close"] != MISSING_DATA_PLACEHOLDER,
        "spf_pct_change",
    ] = control_dataframe["spf close"].pct_change()

    control_dataframe["vix_spf_pct_diff"] = (
        control_dataframe["vix_pct_change"] - control_dataframe["spf_pct_change"]
    )

    control_dataframe["prev_vix_spf_pct_diff"] = control_dataframe[
        "vix_spf_pct_diff"
    ].shift(1)

    control_dataframe.drop(
        columns=["vix_pct_change", "spf_pct_change"],
        inplace=True,
    )

    vfcd_calculator = VixFuturesConvergenceDivergenceCalculator(
        dataframe=enhanced_dataframe,
        window_size=window_size,
    )

    vfcd_calculator.calculate_vix_futures_convergence_divergence()

    assert all(enhanced_dataframe["vix_spf_pct_diff"].iloc[0:5] == 0.0)

    assert (
        control_dataframe["vix_spf_pct_diff"]
        .iloc[0:5]
        .equals(enhanced_dataframe["vix_spf_pct_diff"].iloc[0:5])
    )
