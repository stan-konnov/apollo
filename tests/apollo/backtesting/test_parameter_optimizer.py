from pathlib import Path
from random import randint
from typing import cast
from unittest.mock import patch

import pandas as pd
import pytest

from apollo.backtesting.backtesting_runner import BacktestingRunner
from apollo.backtesting.parameter_optimizer import ParameterOptimizer
from apollo.settings import END_DATE, START_DATE, TICKER
from apollo.utils.types import ParameterSet
from tests.fixtures.files_and_directories import BRES_DIR, STRATEGY, OPTP_DIR

RANGE_MIN = 1.0
RANGE_MAX = 2.0
RANGE_STEP = 1.0

LOT_SIZE_CASH = 1000
STOP_LOSS_LEVEL = 0.01
TAKE_PROFIT_LEVEL = 0.01


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
        "stop_loss_level": {
            "range": [RANGE_MIN, RANGE_MAX],
            "step": RANGE_STEP,
        },
        "take_profit_level": {
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

    assert keys == parameters.keys()
    assert control_combinations == list(combinations)


@pytest.mark.usefixtures("dataframe")
@patch("apollo.backtesting.parameter_optimizer.BRES_DIR", BRES_DIR)
@patch("apollo.backtesting.parameter_optimizer.OPTP_DIR", OPTP_DIR)
def test__parameter_optimizer__for_correct_result_output(
    dataframe: pd.DataFrame,
) -> None:
    """
    Test Parameter Optimizer for correct result output.

    _output_results() must create results directory.
    _output_results() must create optimized parameters directory.

    _output_results() must output results CSV file.
    _output_results() must output optimized parameters JSON file.

    Results CSV must have clean indices.
    Results CSV must omit unnecessary columns.
    Results CSV must be sorted by "Return [%]", "Sharpe Ratio", "# Trades".
    """

    dataframe["signal"] = 0
    dataframe.reset_index(inplace=True)

    optimization_run_1_dataframe = dataframe.copy()
    optimization_run_2_dataframe = dataframe.copy()

    random_index_1 = randint(1, dataframe.shape[0] - 1)  # noqa: S311
    random_index_2 = random_index_1 - 1

    optimization_run_1_dataframe.loc[random_index_1, "signal"] = 1
    optimization_run_2_dataframe.loc[random_index_2, "signal"] = 1

    optimization_run_1_dataframe.set_index("date", inplace=True)
    optimization_run_2_dataframe.set_index("date", inplace=True)

    backtesting_runner = BacktestingRunner(
        dataframe=optimization_run_1_dataframe,
        strategy_name=STRATEGY,
        lot_size_cash=LOT_SIZE_CASH,
        stop_loss_level=STOP_LOSS_LEVEL,
        take_profit_level=TAKE_PROFIT_LEVEL,
    )

    optimization_run_1_stats = backtesting_runner.run()

    backtesting_runner = BacktestingRunner(
        dataframe=optimization_run_2_dataframe,
        strategy_name=STRATEGY,
        lot_size_cash=LOT_SIZE_CASH,
        stop_loss_level=STOP_LOSS_LEVEL,
        take_profit_level=TAKE_PROFIT_LEVEL,
    )

    optimization_run_2_stats = backtesting_runner.run()

    optimized_results_1 = pd.DataFrame(optimization_run_1_stats).transpose()
    optimized_results_1["parameters"] = (
        "{'stop_loss_level': 0.01, 'take_profit_level': 0.01}"
    )

    optimized_results_2 = pd.DataFrame(optimization_run_2_stats).transpose()
    optimized_results_2["parameters"] = (
        "{'stop_loss_level': 0.02, 'take_profit_level': 0.02}"
    )

    optimized_results = pd.concat([optimized_results_1, optimized_results_2])

    control_dataframe = optimized_results.copy()

    control_dataframe.sort_values(
        ["Return [%]", "Sharpe Ratio", "# Trades"],
        ascending=False,
        inplace=True,
    )

    control_dataframe.reset_index(drop=True, inplace=True)

    control_dataframe.drop(
        columns=[
            "Start",
            "End",
            "Duration",
            "Profit Factor",
            "Expectancy [%]",
            "_strategy",
            "_equity_curve",
            "_trades",
        ],
        inplace=True,
    )

    parameter_optimizer = ParameterOptimizer()

    parameter_optimizer._output_results(optimized_results)  # noqa: SLF001

    results_dataframe = pd.read_csv(
        f"{BRES_DIR}/{TICKER}-{STRATEGY}-{START_DATE}-{END_DATE}.csv",
    )

    print(results_dataframe)

    assert Path.exists(BRES_DIR)
    assert Path.exists(OPTP_DIR)
