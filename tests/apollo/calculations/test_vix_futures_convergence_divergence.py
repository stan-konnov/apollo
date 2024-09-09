import pandas as pd
import pytest

from apollo.calculations.vix_futures_convergence_divergence import (
    VixFuturesConvergenceDivergenceCalculator,
)


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
