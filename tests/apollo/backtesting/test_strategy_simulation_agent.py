import pytest
from pandas import DataFrame

from apollo.backtesting.strategy_simulation_agent import StrategySimulationAgent
from apollo.calculations.average_true_range import AverageTrueRangeCalculator
from tests.fixtures.env_and_constants import SL_VOL_MULT, TP_VOL_MULT


@pytest.mark.usefixtures("dataframe", "window_size")
def test__strategy_simulation_agent__for_correct_sl_tp_calculation(
    dataframe: DataFrame,
    window_size: int,
) -> None:
    """
    Test Strategy Simulation Agent for correct trailing SL and TP calculation.

    Strategy Simulation Agent must calculate correct stop loss and take profit levels.
    """

    at_calculator = AverageTrueRangeCalculator(dataframe, window_size)
    at_calculator.calculate_average_true_range()

    close = dataframe.iloc[-1]["close"]
    average_true_range = dataframe.iloc[-1]["atr"]

    StrategySimulationAgent.sl_volatility_multiplier = SL_VOL_MULT
    StrategySimulationAgent.tp_volatility_multiplier = TP_VOL_MULT

    agent_instance = StrategySimulationAgent(
        broker={},
        data=dataframe,
        params={},
    )

    long_sl, long_tp, short_sl, short_tp = (
        agent_instance._calculate_trailing_stop_loss_and_take_profit(  # noqa: SLF001
            close_price=close,
            average_true_range=average_true_range,
            sl_volatility_multiplier=SL_VOL_MULT,
            tp_volatility_multiplier=TP_VOL_MULT,
        )
    )

    control_long_sl = close - average_true_range * SL_VOL_MULT
    control_long_tp = close + average_true_range * TP_VOL_MULT

    control_short_sl = close + average_true_range * SL_VOL_MULT
    control_short_tp = close - average_true_range * TP_VOL_MULT

    assert long_sl == control_long_sl
    assert long_tp == control_long_tp

    assert short_sl == control_short_sl
    assert short_tp == control_short_tp
