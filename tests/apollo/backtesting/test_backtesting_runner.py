import pytest
from pandas import DataFrame

from apollo.backtesting.backtesting_runner import BacktestingRunner
from apollo.settings import STRATEGY

LOT_SIZE_CASH = 1000
STOP_LOSS_LEVEL = 0.01
TAKE_PROFIT_LEVEL = 0.01


@pytest.mark.usefixtures("dataframe")
def test__backtesting_runner__for_uppercasing_columns(
    dataframe: DataFrame,
) -> None:
    """
    Test BacktestingRunner construction for casting columns to uppercase.

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
