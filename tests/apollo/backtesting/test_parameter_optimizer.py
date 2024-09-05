from typing import cast
from unittest.mock import Mock

import pandas as pd
import pytest

from apollo.backtesting.backtesting_runner import BacktestingRunner
from apollo.backtesting.parameter_optimizer import ParameterOptimizer
from apollo.calculations.average_true_range import AverageTrueRangeCalculator
from apollo.connectors.database.postgres_connector import PostgresConnector
from apollo.settings import (
    BACKTESTING_CASH_SIZE,
    END_DATE,
    FREQUENCY,
    LONG_SIGNAL,
    MAX_PERIOD,
    SHORT_SIGNAL,
    START_DATE,
    STRATEGY,
    TICKER,
)
from apollo.utils.types import ParameterSet
from tests.fixtures.window_size_and_dataframe import SameSeries

RANGE_MIN = 1.0
RANGE_MAX = 2.0
RANGE_STEP = 1.0


def test__parameter_optimizer__for_correct_combination_ranges() -> None:
    """
    Test Parameter Optimizer for correct combination ranges.

    _get_combination_ranges() must return Series with correct combination ranges.
    """

    parameter_optimizer = ParameterOptimizer()

    control_combination_ranges = pd.Series([RANGE_MIN, RANGE_MAX])

    combination_ranges = parameter_optimizer._get_combination_ranges(  # noqa: SLF001
        RANGE_MIN,
        RANGE_MAX,
        RANGE_STEP,
    )

    pd.testing.assert_series_equal(control_combination_ranges, combination_ranges)


def test__parameter_optimizer__for_correct_parameter_combinations() -> None:
    """
    Test Parameter Optimizer for correct combination ranges.

    _construct_parameter_combinations() must
    return tuple of parameter keys and product of ranges.
    """

    parameter_optimizer = ParameterOptimizer()

    parameters = {
        "sl_volatility_multiplier": {
            "range": [RANGE_MIN, RANGE_MAX],
            "step": RANGE_STEP,
        },
        "tp_volatility_multiplier": {
            "range": [RANGE_MIN, RANGE_MAX],
            "step": RANGE_STEP,
        },
    }

    control_combinations = [
        (RANGE_MIN, RANGE_MIN),
        (RANGE_MIN, RANGE_MAX),
        (RANGE_MAX, RANGE_MIN),
        (RANGE_MAX, RANGE_MAX),
    ]

    keys, combinations = parameter_optimizer._construct_parameter_combinations(  # noqa: SLF001
        cast(ParameterSet, parameters),
    )

    assert keys == (list(parameters.keys()))
    assert control_combinations == list(combinations)


def test__parameter_optimizer__for_correct_combinations_batching() -> None:
    """
    Test Parameter Optimizer for correct combinations batching.

    _batch_combinations() must return list of batches of combinations.
    """

    parameter_optimizer = ParameterOptimizer()

    combinations = [
        (RANGE_MIN, RANGE_MIN),
        (RANGE_MIN, RANGE_MAX),
        (RANGE_MAX, RANGE_MIN),
        (RANGE_MAX, RANGE_MAX),
    ]

    control_batches = [
        [(RANGE_MIN, RANGE_MIN), (RANGE_MIN, RANGE_MAX)],
        [(RANGE_MAX, RANGE_MIN), (RANGE_MAX, RANGE_MAX)],
    ]

    batches = parameter_optimizer._batch_combinations(  # noqa: SLF001
        len(control_batches),
        combinations,
    )

    assert control_batches == batches


@pytest.mark.usefixtures("dataframe")
def test__parameter_optimizer__for_correct_error_handling(
    dataframe: pd.DataFrame,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """
    Test Parameter Optimizer for correct error handling.

    Parameter Optimizer must catch error from strategy, log and exit with code 1.
    """

    parameter_optimizer = ParameterOptimizer()

    parameter_set = cast(
        ParameterSet,
        {
            "window_size": {
                "step": 5,
                "range": [5, 10],
            },
            "kurtosis_thresh": {
                "step": 0.1,
                "range": [1.0, 2.0],
            },
            "volatility_multiplier": {
                "step": 0.1,
                "range": [1.0, 2.0],
            },
            "strategy_specific_parameters": [
                "kurtosis_thresh",
                "volatility_multiplier",
            ],
        },
    )

    keys, combinations = parameter_optimizer._construct_parameter_combinations(  # noqa: SLF001
        parameter_set,
    )

    with pytest.raises(SystemExit) as exception:
        parameter_optimizer._process(  # noqa: SLF001
            combinations=combinations,
            price_dataframe=dataframe,
            parameter_set=parameter_set,
            keys=keys,
        )

    assert "Parameters misconfigured, see traceback" in caplog.text
    assert exception.value.code == 1


@pytest.mark.usefixtures("enhanced_dataframe")
def test__parameter_optimizer__for_correct_processing(
    enhanced_dataframe: pd.DataFrame,
) -> None:
    """
    Test Parameter Optimizer for correct processing.

    Result must be dataframe.
    Result must have "parameters" column.
    """

    parameter_optimizer = ParameterOptimizer()

    parameters = {
        "window_size": {
            "range": [5, 10],
            "step": 5,
        },
        "sl_volatility_multiplier": {
            "range": [RANGE_MIN, RANGE_MAX],
            "step": RANGE_STEP,
        },
        "tp_volatility_multiplier": {
            "range": [RANGE_MIN, RANGE_MAX],
            "step": RANGE_STEP,
        },
        "kurtosis_threshold": {
            "range": [RANGE_MIN, RANGE_MAX],
            "step": RANGE_STEP,
        },
        "volatility_multiplier": {
            "range": [RANGE_MIN, RANGE_MAX],
            "step": RANGE_STEP,
        },
        "strategy_specific_parameters": [
            "kurtosis_threshold",
            "volatility_multiplier",
        ],
    }

    keys, combinations = parameter_optimizer._construct_parameter_combinations(  # noqa: SLF001
        cast(ParameterSet, parameters),
    )

    backtested_dataframe = parameter_optimizer._process(  # noqa: SLF001
        combinations=combinations,
        price_dataframe=enhanced_dataframe,
        parameter_set=cast(ParameterSet, parameters),
        keys=keys,
    )

    assert isinstance(backtested_dataframe, pd.DataFrame)
    assert "parameters" in backtested_dataframe.columns


@pytest.mark.usefixtures("dataframe", "window_size")
def test__parameter_optimizer__for_correct_result_output(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test Parameter Optimizer for correct result output.

    Results dataframe must have clean indices.
    Results dataframe must omit unnecessary columns.
    Results dataframe must be sorted by "Return [%]", "Sharpe Ratio", "# Trades".

    Optimized parameters JSON must match the best results.

    Parameter Optimizer must call database connector with correct values.
    """

    # Precalculate shared values
    dataframe["prev_close"] = dataframe["adj close"].shift(1)

    # Precalculate volatility
    at_calculator = AverageTrueRangeCalculator(dataframe, window_size)
    at_calculator.calculate_average_true_range()

    # Drop NaNs after rolling calculations
    dataframe.dropna(inplace=True)

    # Initialize ParameterOptimizer with strategy directory
    # NOTE: this is a flaky test that will be removed with moving away from files
    parameter_optimizer = ParameterOptimizer()
    parameter_optimizer._database_connector = Mock(PostgresConnector)  # noqa: SLF001

    # Insert signal column
    dataframe["signal"] = 0

    # Reset the indices so we can insert random signals
    dataframe.reset_index(inplace=True)

    # Create two optimization runs with different signals and parameters
    optimization_run_1_dataframe = dataframe.copy()
    optimization_run_2_dataframe = dataframe.copy()

    # NOTE: we explicitly setting signal at index 1,
    # since otherwise, given our test data, we would have no trades,
    # resulting in empty run, which would not be useful for testing purposes
    optimization_run_1_dataframe.loc[1, "signal"] = LONG_SIGNAL
    optimization_run_2_dataframe.loc[1, "signal"] = SHORT_SIGNAL

    # Set indices back to date
    optimization_run_1_dataframe.set_index("date", inplace=True)
    optimization_run_2_dataframe.set_index("date", inplace=True)

    # Backtest the first run
    backtesting_runner = BacktestingRunner(
        dataframe=optimization_run_1_dataframe,
        strategy_name=str(STRATEGY),
        lot_size_cash=BACKTESTING_CASH_SIZE,
        sl_volatility_multiplier=0.01,
        tp_volatility_multiplier=0.01,
    )
    optimization_run_1_stats = backtesting_runner.run()

    # Backtest the second run
    backtesting_runner = BacktestingRunner(
        dataframe=optimization_run_2_dataframe,
        strategy_name=str(STRATEGY),
        lot_size_cash=BACKTESTING_CASH_SIZE,
        sl_volatility_multiplier=0.02,
        tp_volatility_multiplier=0.02,
    )
    optimization_run_2_stats = backtesting_runner.run()

    # Transpose the results and add parameters
    optimized_results_1 = pd.DataFrame(optimization_run_1_stats).transpose()
    optimized_results_1["parameters"] = str(
        {
            "sl_volatility_multiplier": 0.01,
            "tp_volatility_multiplier": 0.01,
        },
    )

    optimized_results_2 = pd.DataFrame(optimization_run_2_stats).transpose()
    optimized_results_2["parameters"] = str(
        {
            "sl_volatility_multiplier": 0.02,
            "tp_volatility_multiplier": 0.02,
        },
    )

    # Merge the results
    optimized_results = pd.concat([optimized_results_1, optimized_results_2])

    # Use the results as control dataframe
    control_dataframe = optimized_results.copy()

    # Sort the control dataframe
    control_dataframe.sort_values(
        ["Sharpe Ratio", "Return [%]", "# Trades"],
        ascending=False,
        inplace=True,
    )

    # Reset the indices of the control
    # dataframe to cleanup after concatenation
    control_dataframe.reset_index(drop=True, inplace=True)

    # Parse the optimized parameters
    control_parameters = control_dataframe.iloc[0]["parameters"]
    control_parameters = str(control_parameters).replace("'", '"')

    # Extract single backtesting results series to write
    control_backtesting_results = control_dataframe.iloc[0]

    # Now, run the _output_results method
    parameter_optimizer._output_results(optimized_results)  # noqa: SLF001

    parameter_optimizer._database_connector.write_backtesting_results.assert_called_once_with(  # noqa: SLF001
        ticker=str(TICKER),
        strategy=str(STRATEGY),
        frequency=str(FREQUENCY),
        max_period=bool(MAX_PERIOD),
        parameters=control_parameters,
        # Please see tests/fixtures/window_size_and_dataframe.py
        # for explanation on SameSeries class
        backtesting_results=SameSeries(control_backtesting_results),
        backtesting_end_date=str(END_DATE),
        backtesting_start_date=str(START_DATE),
    )
