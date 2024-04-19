import pytest
from pandas import DataFrame

from apollo.backtesting.strategy_simulation_agent import StrategySimulationAgent

LOT_SIZE_CASH = 1000
STOP_LOSS_LEVEL = 0.01
TAKE_PROFIT_LEVEL = 0.01


@pytest.mark.usefixtures("dataframe")
def test__strategy_simulation_agent__for_correct_sl_tp_calculation(
    dataframe: DataFrame,
) -> None:
    """
    Test Strategy Simulation Agent for correct SL and TP calculation.

    Strategy Simulation Agent must calculate correct stop loss and take profit levels.
    """

    close = dataframe.iloc[0]["close"]
    stop_loss_level = 0.01
    take_profit_level = 0.02

    StrategySimulationAgent.stop_loss_level = stop_loss_level
    StrategySimulationAgent.take_profit_level = take_profit_level

    agent_instance = StrategySimulationAgent(
        broker={},
        data=dataframe,
        params={},
    )

    long_sl, long_tp = agent_instance._calculate_long_sl_and_tp(close)  # noqa: SLF001

    control_long_sl = close * (1 - stop_loss_level)
    control_long_tp = close * (1 + take_profit_level)

    short_sl, short_tp = agent_instance._calculate_short_sl_and_tp(close)  # noqa: SLF001

    control_short_sl = close * (1 + stop_loss_level)
    control_short_tp = close * (1 - take_profit_level)

    assert long_sl == control_long_sl
    assert long_tp == control_long_tp

    assert short_sl == control_short_sl
    assert short_tp == control_short_tp
