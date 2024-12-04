import logging
from typing import cast
from unittest import mock
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from apollo.backtesters.backtesting_runner import BacktestingRunner
from apollo.calculators.average_true_range import AverageTrueRangeCalculator
from apollo.connectors.database.postgres_connector import PostgresConnector
from apollo.errors.system_invariants import OptimizedPositionAlreadyExistsError
from apollo.models.position import Position, PositionStatus
from apollo.processors.parameter_optimizer import ParameterOptimizer
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
    ParameterOptimizerMode,
)
from apollo.utils.types import ParameterKeysAndCombinations, ParameterSet
from tests.fixtures.window_size_and_dataframe import SameDataframe, SameSeries
from tests.utils.precalculate_shared_values import precalculate_shared_values

RANGE_MIN = 1.0
RANGE_MAX = 2.0
RANGE_STEP = 1.0


def test__get_combination_ranges__for_correct_combination_ranges() -> None:
    """
    Test get_combination_ranges method for correct combination ranges.

    Method must return Series with correct combination ranges.
    """

    parameter_optimizer = ParameterOptimizer(
        ParameterOptimizerMode.SINGLE_STRATEGY,
    )

    control_combination_ranges = pd.Series([RANGE_MIN, RANGE_MAX])

    combination_ranges = parameter_optimizer._get_combination_ranges(  # noqa: SLF001
        RANGE_MIN,
        RANGE_MAX,
        RANGE_STEP,
    )

    pd.testing.assert_series_equal(control_combination_ranges, combination_ranges)


def test__construct_parameter_combinations__for_correct_parameter_combinations() -> (
    None
):
    """
    Test construct_parameter_combinations method for correct combination ranges.

    Method must return tuple of parameter keys and product of ranges.
    """

    parameter_optimizer = ParameterOptimizer(
        ParameterOptimizerMode.SINGLE_STRATEGY,
    )

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


@pytest.mark.usefixtures("dataframe")
def test__parameter_optimizer__for_correct_error_handling(
    dataframe: pd.DataFrame,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """
    Test Parameter Optimizer for correct error handling.

    Parameter Optimizer must catch error from strategy, log and exit with code 1.
    """

    parameter_optimizer = ParameterOptimizer(
        ParameterOptimizerMode.SINGLE_STRATEGY,
    )

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
        parameter_optimizer._optimize_parameters(  # noqa: SLF001
            strategy_name=str(STRATEGY),
            combinations=combinations,
            price_dataframe=dataframe,
            parameter_set=parameter_set,
            keys=keys,
        )

    assert "Parameters misconfigured, see traceback" in caplog.text
    assert exception.value.code == 1


@pytest.mark.usefixtures("enhanced_dataframe")
def test__optimize_parameters__for_correctly_optimizing_parameters(
    enhanced_dataframe: pd.DataFrame,
) -> None:
    """
    Test optimize_parameters method for correctly optimizing parameters.

    Method must return Dataframe with backtested results.
    Resulting Dataframe must contain "parameters" column.
    """

    parameter_optimizer = ParameterOptimizer(
        ParameterOptimizerMode.SINGLE_STRATEGY,
    )

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

    backtested_dataframe = parameter_optimizer._optimize_parameters(  # noqa: SLF001
        strategy_name=str(STRATEGY),
        combinations=combinations,
        price_dataframe=enhanced_dataframe,
        parameter_set=cast(ParameterSet, parameters),
        keys=keys,
    )

    assert isinstance(backtested_dataframe, pd.DataFrame)
    assert "parameters" in backtested_dataframe.columns


@pytest.mark.usefixtures("dataframe", "window_size")
def test__output_results__for_correct_result_output(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test output_results method for correct result output.

    Results dataframe must have clean indices.
    Results dataframe must omit unnecessary columns.
    Results dataframe must be sorted by "Return [%]", "Sharpe Ratio", "# Trades".

    Optimized parameters JSON must match the best results.
    Parameter Optimizer must call database connector with correct values.
    """

    dataframe = precalculate_shared_values(dataframe)

    # Precalculate volatility
    at_calculator = AverageTrueRangeCalculator(dataframe, window_size)
    at_calculator.calculate_average_true_range()

    # Drop NaNs after rolling calculations
    dataframe.dropna(inplace=True)

    # Initialize ParameterOptimizer with strategy directory
    parameter_optimizer = ParameterOptimizer(
        ParameterOptimizerMode.SINGLE_STRATEGY,
    )

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
    parameter_optimizer._output_results(  # noqa: SLF001
        ticker=str(TICKER),
        strategy=str(STRATEGY),
        results_dataframe=optimized_results,
    )

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


@pytest.mark.usefixtures("dataframe")
@pytest.mark.parametrize(
    "multiprocessing_pool",
    ["apollo.processors.parameter_optimizer.Pool"],
    indirect=True,
)
def test__optimize_parameters_in_parallel__for_correct_optimization_process(
    dataframe: pd.DataFrame,
    multiprocessing_pool: Mock,
) -> None:
    """
    Test process_in_parallel for correct optimization process.

    Method must call Price Data Provider to get price data.
    Method must call Price Data Enhancer to enhance price data.
    Method must construct parameter combinations and create batches.
    Method must call process method in parallel for each combination batch.
    Method must call output results with combined dataframes of backtesting processes.
    """

    parameter_optimizer = ParameterOptimizer(
        ParameterOptimizerMode.SINGLE_STRATEGY,
    )

    parameter_optimizer._configuration = Mock()  # noqa: SLF001
    parameter_optimizer._database_connector = Mock()  # noqa: SLF001
    parameter_optimizer._price_data_provider = Mock()  # noqa: SLF001
    parameter_optimizer._price_data_enhancer = Mock()  # noqa: SLF001

    # Mock return values of Price Data Provider and Enhancer
    parameter_optimizer._price_data_provider.get_price_data.return_value = dataframe  # noqa: SLF001
    parameter_optimizer._price_data_enhancer.enhance_price_data.return_value = dataframe  # noqa: SLF001

    # Mock configured parameter set
    parameter_set = {
        "sl_volatility_multiplier": {
            "range": [RANGE_MIN, RANGE_MAX],
            "step": RANGE_STEP,
        },
        "tp_volatility_multiplier": {
            "range": [RANGE_MIN, RANGE_MAX],
            "step": RANGE_STEP,
        },
        "additional_data_enhancers": ["VIX"],
    }
    parameter_optimizer._configuration.get_parameter_set.return_value = parameter_set  # noqa: SLF001

    # Mock Parameter Optimizer private methods
    # to assert they have been called after the process
    with patch.object(
        ParameterOptimizer,
        "_construct_parameter_combinations",
    ) as construct_parameter_combinations, patch.object(
        ParameterOptimizer,
        "_output_results",
    ) as output_results:
        # Mock the return value of the map method as
        # list of dataframes with backtesting results
        backtesting_results = [
            pd.DataFrame(
                {
                    "Return [%]": [0.0],
                    "Sharpe Ratio": [0.0],
                    "# Trades": [0],
                },
            ),
            pd.DataFrame(
                {
                    "Return [%]": [0.0],
                    "Sharpe Ratio": [0.0],
                    "# Trades": [0],
                },
            ),
        ]
        multiprocessing_pool.starmap.return_value = backtesting_results

        # Mock the return value of _construct_parameter_combinations
        keys, combinations = cast(
            ParameterKeysAndCombinations,
            (
                ["sl_volatility_multiplier", "tp_volatility_multiplier"],
                [
                    (RANGE_MIN, RANGE_MIN),
                    (RANGE_MIN, RANGE_MAX),
                    (RANGE_MAX, RANGE_MIN),
                    (RANGE_MAX, RANGE_MAX),
                ],
            ),
        )
        construct_parameter_combinations.return_value = (keys, combinations)

        # Create batches and arguments for each process
        batches = parameter_optimizer._create_batches(combinations)  # noqa: SLF001
        batch_arguments = [
            (str(STRATEGY), batch, dataframe, parameter_set, keys) for batch in batches
        ]

        parameter_optimizer.process_in_parallel()

        # Assert that we requested the price data
        parameter_optimizer._price_data_provider.get_price_data.assert_called_once_with(  # noqa: SLF001
            ticker=str(TICKER),
            frequency=str(FREQUENCY),
            start_date=str(START_DATE),
            end_date=str(END_DATE),
            max_period=bool(MAX_PERIOD),
        )

        # Assert that we enhanced the price data
        parameter_optimizer._price_data_enhancer.enhance_price_data.assert_called_once_with(  # noqa: SLF001
            dataframe,
            parameter_set["additional_data_enhancers"],
        )

        # Assert that we constructed parameter combinations
        construct_parameter_combinations.assert_called_once_with(
            parameter_set,
        )

        # Assert that we called our processing method in parallel
        multiprocessing_pool.starmap.assert_called_once_with(
            parameter_optimizer._optimize_parameters,  # noqa: SLF001
            batch_arguments,
        )

        # Assert that we called the output results
        # with combined dataframes of backtesting processes
        output_results.assert_called_once_with(
            ticker=str(TICKER),
            strategy=str(STRATEGY),
            # Please see tests/fixtures/window_size_and_dataframe.py
            # for explanation on SameDataframe class
            results_dataframe=SameDataframe(pd.concat(backtesting_results)),
        )


def test__optimize_parameters_in_parallel__for_raising_error_if_position_exists() -> (
    None
):
    """
    Test process_in_parallel for raising error if position exists.

    Method must raise error if existing optimized position is found.
    """

    parameter_optimizer = ParameterOptimizer(
        ParameterOptimizerMode.MULTIPLE_STRATEGIES,
    )

    parameter_optimizer._database_connector = Mock()  # noqa: SLF001
    parameter_optimizer._database_connector.get_existing_position_by_status.return_value = Position(  # noqa: E501, SLF001
        ticker=str(TICKER),
        status=PositionStatus.OPTIMIZED,
    )

    exception_message = (
        "Optimized position for "
        f"{TICKER} already exists. "
        "System invariant violated, previous position not dispatched."
    )

    with pytest.raises(
        OptimizedPositionAlreadyExistsError,
        match=exception_message,
    ) as exception:
        parameter_optimizer.process_in_parallel()

    assert str(exception.value) == exception_message


def test__optimize_parameters_in_parallel__for_skipping_process_if_no_screened_position(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """
    Test process_in_parallel for skipping process if no screened position.

    Method must log if no screened position is found.
    Method must not call perform any database write operations.
    """

    caplog.set_level(logging.INFO)

    parameter_optimizer = ParameterOptimizer(
        ParameterOptimizerMode.MULTIPLE_STRATEGIES,
    )

    parameter_optimizer._database_connector = Mock()  # noqa: SLF001
    parameter_optimizer._database_connector.get_existing_position_by_status.return_value = None  # noqa: E501, SLF001

    parameter_optimizer.process_in_parallel()

    assert (
        str(
            "Screened position does not exist. "
            "Skipping optimization process and proceeding further.",
        )
        in caplog.text
    )

    parameter_optimizer._database_connector.update_position_on_optimization.assert_not_called()  # noqa: SLF001


@patch(
    "apollo.processors.parameter_optimizer.STRATEGY_CATALOGUE_MAP",
    {
        "Strategy1": "Strategy1",
        "Strategy2": "Strategy2",
    },
)
def test__optimize_parameters_in_parallel__for_multiple_strategies() -> None:
    """
    Test process_in_parallel for multiple strategies.

    Method must call process method in parallel for each strategy.
    Method must call update_position_on_optimization after all strategies are processed.
    """

    parameter_optimizer = ParameterOptimizer(
        ParameterOptimizerMode.MULTIPLE_STRATEGIES,
    )

    parameter_optimizer._database_connector = Mock()  # noqa: SLF001
    parameter_optimizer._database_connector.get_existing_position_by_status.return_value = Position(  # noqa: E501, SLF001
        id="test",
        ticker=str(TICKER),
        status=PositionStatus.SCREENED,
    )

    parameter_optimizer._database_connector.get_existing_position_by_status.return_value = None  # noqa: E501, SLF001

    with patch.object(
        ParameterOptimizer,
        "_run_optimization_process",
    ) as _run_optimization_process:
        parameter_optimizer.process_in_parallel()

        _run_optimization_process.assert_has_calls(
            [
                mock.call(
                    ticker=str(TICKER),
                    strategy="Strategy1",
                ),
                mock.call(
                    ticker=str(TICKER),
                    strategy="Strategy2",
                ),
            ],
        )

        parameter_optimizer._database_connector.update_position_on_optimization.assert_called_once_with(  # noqa: SLF001
            "test",
        )


def test__optimize_parameters_in_parallel__for_single_strategies() -> None:
    """
    Test process_in_parallel for single strategies.

    Method must call process method in parallel with default parameters.
    Method must not call update_position_on_optimization after strategy is processed.
    """

    parameter_optimizer = ParameterOptimizer(
        ParameterOptimizerMode.SINGLE_STRATEGY,
    )

    parameter_optimizer._database_connector = Mock()  # noqa: SLF001

    with patch.object(
        ParameterOptimizer,
        "_run_optimization_process",
    ) as _run_optimization_process:
        parameter_optimizer.process_in_parallel()

        _run_optimization_process.assert_called_once_with()

        parameter_optimizer._database_connector.update_position_on_optimization.assert_not_called()  # noqa: SLF001
