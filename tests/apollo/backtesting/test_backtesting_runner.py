from pathlib import Path
from unittest.mock import patch

import pytest
from pandas import DataFrame

from apollo.backtesting.backtesting_runner import BacktestingRunner
from apollo.settings import STRATEGY
from tests.fixtures.api_response import DATA_DIR

LOT_SIZE_CASH = 1000
STOP_LOSS_LEVEL = 0.01
TAKE_PROFIT_LEVEL = 0.01


@pytest.mark.usefixtures("dataframe")
def test__backtesting_runner__for_uppercasing_columns(
    dataframe: DataFrame,
) -> None:
    """
    Test Backtesting Runner construction for casting columns to uppercase.

    Backtesting runner must cast OHLCV columns to first letter uppercase.
    """

    BacktestingRunner(
        dataframe=dataframe,
        strategy_name=str(STRATEGY),
        lot_size_cash=LOT_SIZE_CASH,
        stop_loss_level=STOP_LOSS_LEVEL,
        take_profit_level=TAKE_PROFIT_LEVEL,
    )

    assert all(
        col in dataframe.columns for col in ["Open", "High", "Low", "Close", "Volume"]
    )


@pytest.mark.usefixtures("dataframe")
@patch("apollo.backtesting.backtesting_runner.PLOT_DIR", DATA_DIR)
def test__backtesting_runner__for_running_the_process(
    dataframe: DataFrame,
) -> None:
    """
    Test Backtesting Runner for running the backtesting process.

    Backtesting runner must run the backtesting process and return statistics.
    Statistics must have strategy name from environment variables.
    """

    dataframe["signal"] = 0
    strategy_name = str(STRATEGY)

    backtesting_runner = BacktestingRunner(
        dataframe=dataframe,
        strategy_name=strategy_name,
        lot_size_cash=LOT_SIZE_CASH,
        stop_loss_level=STOP_LOSS_LEVEL,
        take_profit_level=TAKE_PROFIT_LEVEL,
    )

    stats = backtesting_runner.run()

    assert stats is not None
    assert stats["_strategy"] == strategy_name


@pytest.mark.usefixtures("dataframe")
@patch("apollo.backtesting.backtesting_runner.PLOT_DIR", Path("tests/temp/plots"))
def test__backtesting_runner__for_creating_plots_directory(
    dataframe: DataFrame,
) -> None:
    """
    Test Backtesting Runner for creating plots directory.

    Backtesting runner must create plots directory if it doesn't exist.
    """

    dataframe["signal"] = 0
    strategy_name = str(STRATEGY)

    backtesting_runner = BacktestingRunner(
        dataframe=dataframe,
        strategy_name=strategy_name,
        lot_size_cash=LOT_SIZE_CASH,
        stop_loss_level=STOP_LOSS_LEVEL,
        take_profit_level=TAKE_PROFIT_LEVEL,
        write_result_plot=True,
    )

    backtesting_runner.run()

    assert Path.exists(Path("tests/temp/plots"))


@pytest.mark.usefixtures("dataframe")
@patch("apollo.backtesting.backtesting_runner.PLOT_DIR", DATA_DIR)
def test__backtesting_runner__for_writing_result_plot(
    dataframe: DataFrame,
) -> None:
    """
    Test Backtesting Runner for writing the result plot.

    Backtesting runner must write the result plot if requested.
    """

    dataframe["signal"] = 0
    strategy_name = str(STRATEGY)

    backtesting_runner = BacktestingRunner(
        dataframe=dataframe,
        strategy_name=strategy_name,
        lot_size_cash=LOT_SIZE_CASH,
        stop_loss_level=STOP_LOSS_LEVEL,
        take_profit_level=TAKE_PROFIT_LEVEL,
        write_result_plot=True,
    )

    backtesting_runner.run()

    assert Path.exists(Path(f"{DATA_DIR}/{strategy_name}.html"))
