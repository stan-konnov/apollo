from pathlib import Path
from unittest.mock import patch

import pytest
from pandas import DataFrame

from apollo.backtesting.backtesting_runner import BacktestingRunner
from tests.fixtures.env_and_constants import (
    LOT_SIZE_CASH,
    SL_VOL_MULT,
    STRATEGY,
    TP_VOL_MULT,
)
from tests.fixtures.files_and_directories import PLOT_DIR


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
        strategy_name=STRATEGY,
        lot_size_cash=LOT_SIZE_CASH,
        sl_volatility_multiplier=SL_VOL_MULT,
        tp_volatility_multiplier=TP_VOL_MULT,
    )

    assert all(
        col in dataframe.columns for col in ["Open", "High", "Low", "Close", "Volume"]
    )


@pytest.mark.usefixtures("dataframe")
@patch("apollo.backtesting.backtesting_runner.PLOT_DIR", PLOT_DIR)
def test__backtesting_runner__for_running_the_process(
    dataframe: DataFrame,
) -> None:
    """
    Test Backtesting Runner for running the backtesting process.

    Backtesting runner must run the backtesting process and return statistics.
    Statistics must have strategy name from environment variables.
    """

    dataframe["atr"] = 0
    dataframe["signal"] = 0

    backtesting_runner = BacktestingRunner(
        dataframe=dataframe,
        strategy_name=STRATEGY,
        lot_size_cash=LOT_SIZE_CASH,
        sl_volatility_multiplier=SL_VOL_MULT,
        tp_volatility_multiplier=TP_VOL_MULT,
    )

    stats = backtesting_runner.run()

    assert stats is not None
    assert stats["_strategy"] == STRATEGY


@pytest.mark.usefixtures("dataframe")
@patch("apollo.backtesting.backtesting_runner.PLOT_DIR", PLOT_DIR)
def test__backtesting_runner__for_creating_plots_directory(
    dataframe: DataFrame,
) -> None:
    """
    Test Backtesting Runner for creating plots directory.

    Backtesting runner must create plots directory if it doesn't exist.
    """

    dataframe["atr"] = 0
    dataframe["signal"] = 0

    backtesting_runner = BacktestingRunner(
        dataframe=dataframe,
        strategy_name=STRATEGY,
        lot_size_cash=LOT_SIZE_CASH,
        sl_volatility_multiplier=SL_VOL_MULT,
        tp_volatility_multiplier=TP_VOL_MULT,
        write_result_plot=True,
    )

    backtesting_runner.run()

    assert Path.exists(PLOT_DIR)


@pytest.mark.usefixtures("dataframe")
@patch("apollo.backtesting.backtesting_runner.PLOT_DIR", PLOT_DIR)
def test__backtesting_runner__for_writing_result_plot(
    dataframe: DataFrame,
) -> None:
    """
    Test Backtesting Runner for writing the result plot.

    Backtesting runner must write the result plot if requested.
    """

    dataframe["atr"] = 0
    dataframe["signal"] = 0

    backtesting_runner = BacktestingRunner(
        dataframe=dataframe,
        strategy_name=STRATEGY,
        lot_size_cash=LOT_SIZE_CASH,
        sl_volatility_multiplier=SL_VOL_MULT,
        tp_volatility_multiplier=TP_VOL_MULT,
        write_result_plot=True,
    )

    backtesting_runner.run()

    assert Path.exists(Path(f"{PLOT_DIR}/{STRATEGY}.html"))
