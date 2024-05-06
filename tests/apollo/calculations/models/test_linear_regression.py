import pandas as pd
import pytest
from sklearn.model_selection import train_test_split

from apollo.calculations.models.linear_regression import LinearRegressionModelCalculator

SPLIT_RATIO = 0.6
SMOOTHING_FACTOR = 0.1


@pytest.mark.usefixtures("dataframe")
def test__forecast_periods__for_correct_columns(
    dataframe: pd.DataFrame,
) -> None:
    """
    Test forecast_periods method for correct columns.

    Resulting dataframe must have "lrf" column.
    """

    lrm_calculator = LinearRegressionModelCalculator(
        dataframe=dataframe,
        split_ratio=SPLIT_RATIO,
        smoothing_factor=SMOOTHING_FACTOR,
    )

    lrm_calculator.forecast_periods()

    assert "lrf" in lrm_calculator.dataframe.columns


@pytest.mark.usefixtures("dataframe")
def test__forecast_periods__for_correctly_dropping_first_observation(
    dataframe: pd.DataFrame,
) -> None:
    """
    Test forecast_periods method for correctly dropping first observation.

    Resulting dataframe length must be equal to the original dataframe length - 1.
    """

    control_dataframe_length = len(dataframe.copy().index)

    lrm_calculator = LinearRegressionModelCalculator(
        dataframe=dataframe,
        split_ratio=SPLIT_RATIO,
        smoothing_factor=SMOOTHING_FACTOR,
    )

    lrm_calculator.forecast_periods()

    assert len(dataframe.index) == control_dataframe_length - 1


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

    lrm_calculator = LinearRegressionModelCalculator(
        dataframe=dataframe,
        split_ratio=SPLIT_RATIO,
        smoothing_factor=SMOOTHING_FACTOR,
    )

    x = lrm_calculator._define_explanatory_variables(dataframe)  # noqa: SLF001

    pd.testing.assert_frame_equal(x, control_x)


@pytest.mark.usefixtures("dataframe")
def test__create_regression_trading_conditions__for_creating_correct_y_variable(
    dataframe: pd.DataFrame,
) -> None:
    """
    Test create_regression_trading_conditions method for creating correct Y variable.

    Resulting Y variable must be a Series containing the difference between:
    Close at T and Close at T-1.
    """

    control_dataframe = dataframe.copy()

    control_y = control_dataframe["close"].shift(1) - control_dataframe["close"]
    control_y.dropna(inplace=True)

    lrm_calculator = LinearRegressionModelCalculator(
        dataframe=dataframe,
        split_ratio=SPLIT_RATIO,
        smoothing_factor=SMOOTHING_FACTOR,
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
    control_x = control_x.drop(control_x.index[0])

    control_y = control_dataframe["close"].shift(1) - control_dataframe["close"]
    control_y.dropna(inplace=True)

    control_x_train, control_x_test, control_y_train, control_y_test = train_test_split(
        control_x,
        control_y,
        shuffle=False,
        test_size=SPLIT_RATIO,
    )

    dataframe["o_h"] = dataframe["open"] - dataframe["high"]
    x = dataframe[["o_h"]]
    x = x.drop(x.index[0])

    y = dataframe["close"].shift(1) - dataframe["close"]
    y.dropna(inplace=True)

    lrm_calculator = LinearRegressionModelCalculator(
        dataframe=dataframe,
        split_ratio=SPLIT_RATIO,
        smoothing_factor=SMOOTHING_FACTOR,
    )

    x_train, x_test, y_train, y_test = lrm_calculator._create_train_split_group(  # noqa: SLF001
        x,
        y,
    )

    pd.testing.assert_frame_equal(x_train, control_x_train)
    pd.testing.assert_frame_equal(x_test, control_x_test)

    pd.testing.assert_series_equal(y_train, control_y_train)
    pd.testing.assert_series_equal(y_test, control_y_test)


def test__score_model__for_correctly_calculating_score() -> None:
    """
    Test score_model method for correctly calculating score.

    Resulting score must be a correct combination of R2 and MSE.
    """

    r_squared_train = 0.5
    mean_square_error_train = 2

    r_squared_test = 0.4
    mean_square_error_test = 3

    lrm_calculator = LinearRegressionModelCalculator(
        dataframe=pd.DataFrame(),
        split_ratio=SPLIT_RATIO,
        smoothing_factor=SMOOTHING_FACTOR,
    )

    control_score = (r_squared_train + r_squared_test) + (
        (mean_square_error_train + mean_square_error_test) * -1
    )

    score = lrm_calculator._score_model(  # noqa: SLF001
        r_squared_train,
        mean_square_error_train,
        r_squared_test,
        mean_square_error_test,
    )

    assert score == control_score
