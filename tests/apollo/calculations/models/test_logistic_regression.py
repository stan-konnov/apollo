from contextvars import ContextVar

import numpy as np
import pandas as pd
import pytest
from sklearn.linear_model import LogisticRegression

from apollo.calculations.models.logistic_regression import (
    LogisticRegressionModelCalculator,
)

EXPANDING_INDICES: ContextVar[list[int]] = ContextVar("expanding_indices", default=[])


@pytest.mark.usefixtures("dataframe", "window_size")
def test__forecast_periods__for_correct_columns(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test forecast_periods method for correct columns.

    Resulting dataframe must have "lrf" column.
    """

    lrm_calculator = LogisticRegressionModelCalculator(
        dataframe=dataframe,
        window_size=window_size,
    )

    lrm_calculator.forecast_periods()

    assert "lrf" in lrm_calculator.dataframe.columns


@pytest.mark.usefixtures("dataframe", "window_size")
def test__define_explanatory_variables__for_creating_correct_x_variable(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test define_explanatory_variables method for creating correct X variable.

    Resulting X variable must be a Dataframe containing differences between:
    OHLC aspects and Close and Adjusted Close.
    """

    control_dataframe = dataframe.copy()

    ohlc_aspects: dict[str, str] = {
        "o": "open",
        "h": "high",
        "l": "low",
        "c": "close",
        "a": "adj close",
    }

    ohlc_aspects_combinations: list[tuple[str, str]] = [
        ("o", "h"),
        ("o", "l"),
        ("o", "c"),
        ("h", "l"),
        ("h", "c"),
        ("l", "c"),
        ("c", "a"),
    ]

    variables_to_apply = []

    for aspect_a, aspect_b in ohlc_aspects_combinations:
        control_dataframe[f"{aspect_a}_{aspect_b}"] = (
            control_dataframe[ohlc_aspects[aspect_a]]
            - control_dataframe[ohlc_aspects[aspect_b]]
        )

        variables_to_apply.append(f"{aspect_a}_{aspect_b}")

    control_x = control_dataframe[variables_to_apply]

    lrm_calculator = LogisticRegressionModelCalculator(
        dataframe=dataframe,
        window_size=window_size,
    )

    x = lrm_calculator._define_explanatory_variables(dataframe)  # noqa: SLF001

    pd.testing.assert_frame_equal(x, control_x)


@pytest.mark.usefixtures("dataframe", "window_size")
def test__create_regression_trading_conditions__for_creating_correct_y_variable(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test create_regression_trading_conditions method for creating correct Y variable.

    Resulting Y variable must be a Series containing binary classifier
    that indicates whether the price will go up or down in the next period.
    """

    control_dataframe = dataframe.copy()

    control_y = pd.Series(
        np.where(
            control_dataframe["close"].shift(-1) > control_dataframe["close"],
            1,
            -1,
        ),
    )

    lrm_calculator = LogisticRegressionModelCalculator(
        dataframe=dataframe,
        window_size=window_size,
    )

    _, y = lrm_calculator._create_regression_trading_conditions(dataframe)  # noqa: SLF001

    pd.testing.assert_series_equal(y, control_y)


@pytest.mark.usefixtures("dataframe", "window_size")
def test__forecast_periods__for_correct_forecast(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test forecast_periods method for correct forecast.

    Resulting forecast must be a correct forecast of the model.
    """

    control_dataframe = dataframe.copy()
    control_dataframe.reset_index(inplace=True)

    control_model = LogisticRegression(
        penalty="elasticnet",
        solver="saga",
        l1_ratio=1.0,
    )
    control_lrm_calculator = LogisticRegressionModelCalculator(
        dataframe=control_dataframe,
        window_size=window_size,
    )

    control_dataframe["lrf"] = (
        control_dataframe["close"]
        .rolling(window=window_size)
        .apply(
            mimic_rolling_forecast,
            args=(
                control_dataframe,
                control_model,
                control_lrm_calculator,
            ),
        )
    )

    control_dataframe.set_index("date", inplace=True)

    lrm_calculator = LogisticRegressionModelCalculator(
        dataframe=dataframe,
        window_size=window_size,
    )
    lrm_calculator.forecast_periods()

    pd.testing.assert_series_equal(dataframe["lrf"], control_dataframe["lrf"])


def mimic_rolling_forecast(
    series: pd.Series,
    dataframe: pd.DataFrame,
    model: LogisticRegression,
    lrm_calculator: LogisticRegressionModelCalculator,
) -> None:
    """
    Mimicry of rolling Logistic Regression forecast for testing purposes.

    Please see LogisticRegressionModelCalculator for detailed explanation.
    """

    rolling_indices = series.index.to_list()

    if len(EXPANDING_INDICES.get()) == 0:
        EXPANDING_INDICES.set(rolling_indices)

    else:
        this_run_expanding_indices = EXPANDING_INDICES.get()
        this_run_expanding_indices.append(rolling_indices[-1])

        EXPANDING_INDICES.set(this_run_expanding_indices)

    rolling_df = dataframe.loc[EXPANDING_INDICES.get()]

    x, y = lrm_calculator._create_regression_trading_conditions(rolling_df)  # noqa: SLF001

    model.fit(x, y)

    return model.predict(x)[-1]
