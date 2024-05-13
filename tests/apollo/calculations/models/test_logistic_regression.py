import numpy as np
import pandas as pd
import pytest
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

from apollo.calculations.models.logistic_regression import (
    LogisticRegressionModelCalculator,
)

TRAIN_SIZE = 0.4


@pytest.mark.usefixtures("dataframe")
def test__forecast_periods__for_correct_columns(
    dataframe: pd.DataFrame,
) -> None:
    """
    Test forecast_periods method for correct columns.

    Resulting dataframe must have "lrf" column.
    """

    lrm_calculator = LogisticRegressionModelCalculator(
        dataframe=dataframe,
        train_size=TRAIN_SIZE,
    )

    lrm_calculator.forecast_periods()

    assert "lrf" in lrm_calculator.dataframe.columns


@pytest.mark.usefixtures("dataframe")
def test__define_explanatory_variables__for_creating_correct_x_variable(
    dataframe: pd.DataFrame,
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
        train_size=TRAIN_SIZE,
    )

    x = lrm_calculator._define_explanatory_variables(dataframe)  # noqa: SLF001

    pd.testing.assert_frame_equal(x, control_x)


@pytest.mark.usefixtures("dataframe")
def test__create_regression_trading_conditions__for_creating_correct_y_variable(
    dataframe: pd.DataFrame,
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
        train_size=TRAIN_SIZE,
    )

    _, y = lrm_calculator._create_regression_trading_conditions(dataframe)  # noqa: SLF001

    pd.testing.assert_series_equal(y, control_y)


@pytest.mark.usefixtures("dataframe")
def test__create_train_split_group__for_correctly_splitting_inputs(
    dataframe: pd.DataFrame,
) -> None:
    """
    Test create_train_split_group method for correctly splitting inputs.

    Resulting train and split groups must be equal to the control groups.
    """

    control_dataframe = dataframe.copy()
    control_dataframe["o_h"] = control_dataframe["open"] - control_dataframe["high"]

    control_x = control_dataframe[["o_h"]]
    control_y = pd.Series(
        np.where(
            control_dataframe["close"].shift(-1) > control_dataframe["close"],
            1,
            -1,
        ),
    )

    control_x_train, _, control_y_train, _ = train_test_split(
        control_x,
        control_y,
        shuffle=False,
        train_size=TRAIN_SIZE,
    )

    dataframe["o_h"] = dataframe["open"] - dataframe["high"]

    x = dataframe[["o_h"]]
    y = pd.Series(
        np.where(
            dataframe["close"].shift(-1) > dataframe["close"],
            1,
            -1,
        ),
    )

    lrm_calculator = LogisticRegressionModelCalculator(
        dataframe=dataframe,
        train_size=TRAIN_SIZE,
    )

    x_train, y_train = lrm_calculator._create_train_split_group(  # noqa: SLF001
        x,
        y,
    )

    pd.testing.assert_frame_equal(x_train, control_x_train)
    pd.testing.assert_series_equal(y_train, control_y_train)


@pytest.mark.usefixtures("dataframe")
def test__forecast_periods__for_correct_forecast(
    dataframe: pd.DataFrame,
) -> None:
    """
    Test forecast_periods method for correct forecast.

    Resulting forecast must be a correct forecast of the model.
    """

    control_dataframe = dataframe.copy()

    lrm_calculator = LogisticRegressionModelCalculator(
        dataframe=dataframe,
        train_size=TRAIN_SIZE,
    )

    x, y = lrm_calculator._create_regression_trading_conditions(control_dataframe)  # noqa: SLF001
    x_train, y_train = lrm_calculator._create_train_split_group(  # noqa: SLF001
        x,
        y,
    )

    model = LogisticRegression()
    model.fit(x_train, y_train)
    control_dataframe["lrf"] = model.predict(x)

    lrm_calculator.forecast_periods()

    pd.testing.assert_series_equal(dataframe["lrf"], control_dataframe["lrf"])
