import pytest
from pandas import DataFrame

from apollo.calculators.average_true_range import AverageTrueRangeCalculator
from apollo.core.order_brackets_calculator import OrderBracketsCalculator
from tests.utils.precalculate_shared_values import precalculate_shared_values

SL_VOL_MULT = 0.01
TP_VOL_MULT = 0.01


@pytest.mark.usefixtures("dataframe", "window_size")
def test__order_brackets_calculator__for_correct_sl_tp_calculation(
    dataframe: DataFrame,
    window_size: int,
) -> None:
    """
    Test Order Brackets Calculator for correct trailing SL and TP calculation.

    Order Brackets Calculator must calculate correct stop loss and take profit levels.
    """

    dataframe = precalculate_shared_values(dataframe)

    at_calculator = AverageTrueRangeCalculator(dataframe, window_size)
    at_calculator.calculate_average_true_range()

    close_price = dataframe.iloc[-1]["close"]
    average_true_range = dataframe.iloc[-1]["atr"]

    long_sl, long_tp, short_sl, short_tp = (
        OrderBracketsCalculator.calculate_trailing_stop_loss_and_take_profit(
            close_price=close_price,
            average_true_range=average_true_range,
            sl_volatility_multiplier=SL_VOL_MULT,
            tp_volatility_multiplier=TP_VOL_MULT,
        )
    )

    control_long_sl = close_price - average_true_range * SL_VOL_MULT
    control_long_tp = close_price + average_true_range * TP_VOL_MULT

    control_short_sl = close_price + average_true_range * SL_VOL_MULT
    control_short_tp = close_price - average_true_range * TP_VOL_MULT

    assert long_sl == control_long_sl
    assert long_tp == control_long_tp

    assert short_sl == control_short_sl
    assert short_tp == control_short_tp


@pytest.mark.usefixtures("dataframe", "window_size")
def test__order_brackets_calculator__for_correct_limit_entry_price_calculation(
    dataframe: DataFrame,
    window_size: int,
) -> None:
    """
    Test Order Brackets Calculator for correct limit entry price calculation.

    Order Brackets Calculator must calculate correct limit entry price.
    """

    dataframe = precalculate_shared_values(dataframe)

    at_calculator = AverageTrueRangeCalculator(dataframe, window_size)
    at_calculator.calculate_average_true_range()

    close_price = dataframe.iloc[-1]["close"]
    average_true_range = dataframe.iloc[-1]["atr"]

    long_limit, short_limit = OrderBracketsCalculator.calculate_limit_entry_price(
        close_price=close_price,
        average_true_range=average_true_range,
        tp_volatility_multiplier=TP_VOL_MULT,
    )

    control_long_limit = close_price + average_true_range * TP_VOL_MULT / 2
    control_short_limit = close_price - average_true_range * TP_VOL_MULT / 2

    assert long_limit == control_long_limit
    assert short_limit == control_short_limit
