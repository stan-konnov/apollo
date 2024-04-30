from json import load
from pathlib import Path
from random import randint
from typing import cast
from unittest.mock import patch

import pandas as pd
import pytest

from apollo.backtesting.backtesting_runner import BacktestingRunner
from apollo.backtesting.parameter_optimizer import ParameterOptimizer
from apollo.calculations.average_true_range import AverageTrueRangeCalculator
from apollo.settings import LONG_SIGNAL, SHORT_SIGNAL
from apollo.utils.configuration import Configuration
from apollo.utils.types import ParameterSet
from tests.fixtures.env_and_constants import (
    END_DATE,
    LOT_SIZE_CASH,
    SL_VOL_MULT,
    START_DATE,
    STRATEGY,
    TICKER,
    TP_VOL_MULT,
)
from tests.fixtures.files_and_directories import BRES_DIR, OPTP_DIR, PARM_DIR

RANGE_MIN = 1.0
RANGE_MAX = 2.0
RANGE_STEP = 1.0


@patch("apollo.utils.configuration.STRATEGY", STRATEGY)
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


@patch("apollo.utils.configuration.STRATEGY", STRATEGY)
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


@pytest.mark.usefixtures("yahoo_api_response")
@patch("apollo.utils.configuration.PARM_DIR", PARM_DIR)
@patch("apollo.utils.configuration.STRATEGY", STRATEGY)
def test__parameter_optimizer__for_correct_error_handling(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """
    Test Parameter Optimizer for correct error handling.

    Parameter Optimizer must catch error from strategy, log and exit with code 1.
    """

    parameter_optimizer = ParameterOptimizer()
    parameter_optimizer._configuration.parameter_set = {  # type: ignore  # noqa: PGH003, SLF001
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
    }

    with pytest.raises(SystemExit) as exception:
        parameter_optimizer.process()

    assert "Parameters misconfigured, see traceback" in caplog.text
    assert exception.value.code == 1


@pytest.mark.usefixtures("dataframe", "window_size")
@patch("apollo.utils.configuration.STRATEGY", STRATEGY)
@patch("apollo.backtesting.parameter_optimizer.BRES_DIR", BRES_DIR)
@patch("apollo.backtesting.parameter_optimizer.OPTP_DIR", OPTP_DIR)
def test__parameter_optimizer__for_correct_result_output(  # noqa: PLR0915
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test Parameter Optimizer for correct result output.

    Parameter Optimizer must create results directory.
    Parameter Optimizer must create individual strategy directory.
    Parameter Optimizer must create optimized parameters directory.

    Parameter Optimizer must output trades CSV file.
    Parameter Optimizer must output results CSV file.
    Parameter Optimizer must output optimized parameters JSON file.

    Results CSV must have clean indices.
    Results CSV must omit unnecessary columns.
    Results CSV must be sorted by "Return [%]", "Sharpe Ratio", "# Trades".

    Trades CSV must match the best results.
    Optimized parameters JSON must match the best results.
    """

    # Precalculate volatility
    at_calculator = AverageTrueRangeCalculator(dataframe, window_size)
    at_calculator.calculate_average_true_range()

    # Drop NaNs after rolling calculations
    dataframe.dropna(inplace=True)

    # Initialize ParameterOptimizer with Configuration
    parameter_optimizer = ParameterOptimizer()
    parameter_optimizer._configuration = Configuration()  # noqa: SLF001
    parameter_optimizer._configuration.ticker = TICKER  # noqa: SLF001
    parameter_optimizer._configuration.strategy = STRATEGY  # noqa: SLF001
    parameter_optimizer._configuration.start_date = START_DATE  # noqa: SLF001
    parameter_optimizer._configuration.end_date = END_DATE  # noqa: SLF001

    # Insert signal column
    dataframe["signal"] = 0

    # Reset the indices so we can insert random signals
    dataframe.reset_index(inplace=True)

    # Create two optimization runs with different signals and parameters
    optimization_run_1_dataframe = dataframe.copy()
    optimization_run_2_dataframe = dataframe.copy()

    random_index_1 = randint(1, dataframe.shape[0] - 1)  # noqa: S311
    random_index_2 = random_index_1 - 1

    optimization_run_1_dataframe.loc[random_index_1, "signal"] = LONG_SIGNAL
    optimization_run_2_dataframe.loc[random_index_2, "signal"] = SHORT_SIGNAL

    # Set indices back to date
    optimization_run_1_dataframe.set_index("date", inplace=True)
    optimization_run_2_dataframe.set_index("date", inplace=True)

    # Backtest the first run
    backtesting_runner = BacktestingRunner(
        dataframe=optimization_run_1_dataframe,
        strategy_name=STRATEGY,
        lot_size_cash=LOT_SIZE_CASH,
        sl_volatility_multiplier=SL_VOL_MULT,
        tp_volatility_multiplier=TP_VOL_MULT,
    )
    optimization_run_1_stats = backtesting_runner.run()

    # Backtest the second run
    backtesting_runner = BacktestingRunner(
        dataframe=optimization_run_2_dataframe,
        strategy_name=STRATEGY,
        lot_size_cash=LOT_SIZE_CASH,
        sl_volatility_multiplier=SL_VOL_MULT,
        tp_volatility_multiplier=TP_VOL_MULT,
    )
    optimization_run_2_stats = backtesting_runner.run()

    # Transpose the results and add parameters
    optimized_results_1 = pd.DataFrame(optimization_run_1_stats).transpose()
    optimized_results_1["parameters"] = (
        "{'sl_volatility_multiplier': 0.01, 'tp_volatility_multiplier': 0.01}"
    )

    optimized_results_2 = pd.DataFrame(optimization_run_2_stats).transpose()
    optimized_results_2["parameters"] = (
        "{'sl_volatility_multiplier': 0.02, 'tp_volatility_multiplier': 0.02}"
    )

    # Merge the results
    optimized_results = pd.concat([optimized_results_1, optimized_results_2])

    # Use the results as control dataframe
    control_dataframe = optimized_results.copy()

    # Sort the control dataframe
    control_dataframe.sort_values(
        ["Return [%]", "Sharpe Ratio", "# Trades"],
        ascending=False,
        inplace=True,
    )

    # Reset the indices of the control
    # dataframe to cleanup after concatenation
    control_dataframe.reset_index(drop=True, inplace=True)

    # Preserve the best performing trades
    trades_dataframe: pd.DataFrame = control_dataframe.iloc[0]["_trades"]

    # Humanize trades' returns
    trades_dataframe["ReturnPct"] = trades_dataframe["ReturnPct"] * 100

    # Drop unnecessary columns from the control dataframe
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

    # Now, run the _output_results method
    parameter_optimizer._output_results(optimized_results)  # noqa: SLF001

    # Define the individual strategy directory
    individual_strategy_directory = Path(
        f"{BRES_DIR}/{TICKER}-{STRATEGY}-{START_DATE}-{END_DATE}",
    )

    # Read back the results
    results_dataframe = pd.read_csv(
        f"{individual_strategy_directory}/RESULTS.csv",
        index_col=0,
    )

    # Read back the trades
    trades_dataframe_from_disk = pd.read_csv(
        f"{individual_strategy_directory}/TRADES.csv",
        index_col=0,
    )

    # Read back the optimized parameters
    with Path.open(Path(f"{OPTP_DIR}/{STRATEGY}.json")) as file:
        optimized_parameters = load(file)

    # Grab the return from the results and control dataframes
    results_return = round(results_dataframe.iloc[0]["Return [%]"], 2)
    control_return = round(control_dataframe.iloc[0]["Return [%]"], 2)

    # Directories must exist
    assert Path.exists(BRES_DIR)
    assert Path.exists(OPTP_DIR)
    assert Path.exists(individual_strategy_directory)

    # Results CSV must have clean indices
    assert results_dataframe.index.equals(control_dataframe.index)

    # Results CSV must omit unnecessary columns
    assert list(results_dataframe.columns) == list(control_dataframe.columns)

    # Results CSV must be sorted by "Return [%]", "Sharpe Ratio", "# Trades"
    assert results_return == control_return

    # Trades CSV must match the best performing trades
    # NOTE: to avoid hacks around different type of indices and columns
    # between dataframe in memory and one read from disk, we simply compare returns
    pd.testing.assert_series_equal(
        trades_dataframe["ReturnPct"].reset_index(drop=True),
        trades_dataframe_from_disk["ReturnPct"].reset_index(drop=True),
    )

    # Optimized parameters JSON must match the best results
    assert str(optimized_parameters) == control_dataframe.iloc[0]["parameters"]
