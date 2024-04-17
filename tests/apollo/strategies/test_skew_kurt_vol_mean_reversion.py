import pandas as pd
import pytest

from apollo.strategies.skew_kurt_vol_mean_reversion import (
    SkewnessKurtosisVolatilityMeanReversion,
)


@pytest.mark.usefixtures("dataframe", "window_size")
def test__skew_kurt_vol_mean_reversion__with_missing_parameters(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """Test Skewness Kurtosis Volatility Mean Reversion with missing parameters."""

    invalid_param_set = {
        "kurtosis_threshold": None,
    }

    with pytest.raises(
        ValueError,
        match="Parameter kurtosis_threshold is missing",
    ) as exception:

        SkewnessKurtosisVolatilityMeanReversion(
            dataframe=dataframe,
            window_size=window_size,
            kurtosis_threshold=invalid_param_set.get("kurtosis_threshold"),  # type: ignore[assignment]
            volatility_multiplier=1.0,
        )

    assert str(exception.value) == "Parameter kurtosis_threshold is missing"


@pytest.mark.usefixtures("dataframe", "window_size")
def test__skew_kurt_vol_mean_reversion__with_invalid_parameters(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """Test Skewness Kurtosis Volatility Mean Reversion with invalid parameters."""

    invalid_param_set = {
        "kurtosis_threshold": "invalid",
    }

    exception_message = str(
        "Parameter kurtosis_threshold is "
        f"not of expected type {float.__name__}",
    )

    with pytest.raises(
        TypeError,
        match=exception_message,
    ) as exception:

        SkewnessKurtosisVolatilityMeanReversion(
            dataframe=dataframe,
            window_size=window_size,
            kurtosis_threshold=invalid_param_set.get("kurtosis_threshold"),  # type: ignore[assignment]
            volatility_multiplier=1.0,
        )

    assert str(exception.value) == exception_message
