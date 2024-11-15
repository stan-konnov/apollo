class OrderBracketsGenerator:
    """
    Order Brackets Generator class.

    Exists to calculate Limit Entry Price, Stop Loss, and
    Take Profit levels during backtesting and signal dispatching.
    """

    @staticmethod
    def calculate_limit_entry_price(
        close_price: float,
        average_true_range: float,
        tp_volatility_multiplier: float,
    ) -> tuple[float, float]:
        """
        Calculate limit entry price for long and short signals.

        We treat our limit entry as a point between close and take profit.

        :param close_price: Close price.
        :param average_true_range: Average True Range.
        :param tp_volatility_multiplier: Take Profit volatility multiplier.
        :returns: Limit entry price for long and short signals.
        """

        l_limit = close_price + average_true_range * tp_volatility_multiplier / 2
        s_limit = close_price - average_true_range * tp_volatility_multiplier / 2

        return l_limit, s_limit

    @staticmethod
    def calculate_trailing_stop_loss_and_take_profit(
        close_price: float,
        average_true_range: float,
        sl_volatility_multiplier: float,
        tp_volatility_multiplier: float,
    ) -> tuple[float, float, float, float]:
        """
        Calculate trailing stop loss and take profit.

        Using close, Average True Range, and volatility multipliers.

        Kaufman, Trading Systems and Methods, 2020, 6th ed.

        :param close_price: Close price.
        :param average_true_range: Average True Range.
        :param sl_volatility_multiplier: Stop Loss volatility multiplier.
        :param tp_volatility_multiplier: Take Profit volatility multiplier.
        :returns: Trailing stop loss and take profit levels for long and short signals.
        """

        long_sl = close_price - average_true_range * sl_volatility_multiplier
        long_tp = close_price + average_true_range * tp_volatility_multiplier

        short_sl = close_price + average_true_range * sl_volatility_multiplier
        short_tp = close_price - average_true_range * tp_volatility_multiplier

        return long_sl, long_tp, short_sl, short_tp
