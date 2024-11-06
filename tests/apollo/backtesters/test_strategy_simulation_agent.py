import pytest
from pandas import DataFrame

from apollo.backtesters.strategy_simulation_agent import StrategySimulationAgent
from apollo.calculators.average_true_range import AverageTrueRangeCalculator
from tests.utils.precalculate_shared_values import precalculate_shared_values

SL_VOL_MULT = 0.01
TP_VOL_MULT = 0.01


@pytest.mark.usefixtures("dataframe", "window_size")
def test__strategy_simulation_agent__for_correct_sl_tp_calculation(
    dataframe: DataFrame,
    window_size: int,
) -> None:
    """
    Test Strategy Simulation Agent for correct trailing SL and TP calculation.

    Strategy Simulation Agent must calculate correct stop loss and take profit levels.
    """

    dataframe = precalculate_shared_values(dataframe)

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


@pytest.mark.usefixtures("dataframe", "window_size")
def test__strategy_simulation_agent__for_correct_limit_entry_price_calculation(
    dataframe: DataFrame,
    window_size: int,
) -> None:
    """
    Test Strategy Simulation Agent for correct limit entry price calculation.

    Strategy Simulation Agent must calculate correct limit entry price.
    """

    dataframe = precalculate_shared_values(dataframe)

    at_calculator = AverageTrueRangeCalculator(dataframe, window_size)
    at_calculator.calculate_average_true_range()

    close = dataframe.iloc[-1]["close"]
    average_true_range = dataframe.iloc[-1]["atr"]

    StrategySimulationAgent.tp_volatility_multiplier = TP_VOL_MULT

    agent_instance = StrategySimulationAgent(
        broker={},
        data=dataframe,
        params={},
    )

    long_limit, short_limit = agent_instance._calculate_limit_entry_price(  # noqa: SLF001
        close_price=close,
        average_true_range=average_true_range,
    )

    control_long_limit = close + average_true_range * TP_VOL_MULT / 2
    control_short_limit = close - average_true_range * TP_VOL_MULT / 2

    assert long_limit == control_long_limit
    assert short_limit == control_short_limit
