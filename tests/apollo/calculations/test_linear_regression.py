import pandas as pd
import pytest

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
