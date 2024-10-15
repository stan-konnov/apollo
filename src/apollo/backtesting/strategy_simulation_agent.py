from typing import ClassVar

from backtesting import Strategy

from apollo.settings import LONG_SIGNAL, SHORT_SIGNAL

"""
As with any other backtesting approaches, this one takes on several assumptions:

* We are allowed to trade on close (during extended hours)
* We will get filled on our limit orders
* There are no commissions

These assumptions are partially validated by our broker documentation (Alpaca).

Alpaca indeed allows trading during extended hours (pre-market and after-hours).
Alpaca also allows limit orders, yet there is no guarantee that they will be filled.
Alpaca does not charge trading commissions for US equities, but does for other assets.

There are a few considerations to the library we are using:

First, when submitting a limit order with accompanying stop loss,
and in case security considerably gaps up or down (above/below the stop loss),
the library only triggers the limit order, naturally, leading to dubious results.

Example:

Security closes at $97.51. We submit a short
limit order at $96.60 with a stop loss at $97.96.

The next day, security gaps up to $99.66.
The library triggers the limit order, opening a trade $99.66.
but the stop loss is not triggered, as the security never reached $97.96.

In real trading, the stop loss would trigger at the market price,
leading to a vague result of entering and exiting the trade simultaneously.

Moreover, the library will carry the short
position to the open of the next after next day
and close it at the open price, which is not realistic.

And, as you already figured out the library does not actually triggers
limit order on close (clearly, it does not support extended hours trading).

We mitigate all this by placing market orders instead of limit orders,
and, during execution, place our limit orders with the same price as the market order.

RELY ON ALGORITHM INSTEAD OF SL/TP ORDERS.
"""


class StrategySimulationAgent(Strategy):
    """
    Strategy Simulation Agent is backtesting library wrapper class.

    Simulates trade execution according to signals identified by the strategy.
    Used as one of the components in backtesting process facilitated by runner class.
    """

    # Volatility multiplier applied to
    # ATR for calculating trailing stop loss
    sl_volatility_multiplier: ClassVar[float]

    # Volatility multiplier applied to
    # ATR for calculating trailing take profit and limit entry
    tp_volatility_multiplier: ClassVar[float]

    def init(self) -> None:
        """
        Initialize the agent.

        NOTE: Backtesting.py requires this method to be implemented.
        """
        super().init()

    def next(self) -> None:
        """
        Process each row in the supplied dataframe.

        Decide whether to enter trade based on identified signal.
        Calculate stop loss and take profit levels.
        Depending on whether the signal is long or short,
        close existing position (if any) and open new one.

        NOTE: Backtesting.py requires this method to be implemented.
        """
        super().init()

        # Grab close of the current row
        close = self.data["Close"][-1]

        # Grab average true range of the current row
        average_true_range = self.data["atr"][-1]

        # Get currently iterated signal
        signal_identified = self.data["signal"][-1] != 0

        # Calculate trailing stop loss and take profit
        long_sl, long_tp, short_sl, short_tp = (
            self._calculate_trailing_stop_loss_and_take_profit(
                close_price=close,
                average_true_range=average_true_range,
            )
        )

        # Enter the trade if signal identified
        if signal_identified:
            # Identify if signal is long or short
            long_signal = self.data["signal"][-1] == LONG_SIGNAL
            short_signal = self.data["signal"][-1] == SHORT_SIGNAL

            if long_signal:
                # Skip if we already have long position
                if self.position.is_long:
                    return

                # And open new long position, where:
                # stop loss and take profit are our trailing levels
                # and entry is a market order -- price at the close
                self.buy(sl=long_sl, tp=long_tp)

            if short_signal:
                # Skip if we already have short position
                if self.position.is_short:
                    return

                # And open new short position, where:
                # stop loss and take profit are our trailing levels
                # and entry is a market order -- price at the close
                self.sell(sl=short_sl, tp=short_tp)

        # Loop through open positions
        # And assign SL and TP to open position(s)
        for trade in self.trades:
            if trade.is_long:
                trade.sl = long_sl
                trade.tp = long_tp
            else:
                trade.sl = short_sl
                trade.tp = short_tp

    def _calculate_trailing_stop_loss_and_take_profit(
        self,
        close_price: float,
        average_true_range: float,
    ) -> tuple[float, float, float, float]:
        """
        Calculate trailing stop loss and take profit.

        Using close, Average True Range, and volatility multipliers.

        Kaufman, Trading Systems and Methods, 2020, 6th ed.

        :param position_type: Position type.
        :param average_true_range: Average True Range.
        :returns: Trailing stop loss and take profit levels.
        """

        long_sl = close_price - average_true_range * self.sl_volatility_multiplier
        long_tp = close_price + average_true_range * self.tp_volatility_multiplier

        short_sl = close_price + average_true_range * self.sl_volatility_multiplier
        short_tp = close_price - average_true_range * self.tp_volatility_multiplier

        return long_sl, long_tp, short_sl, short_tp

    def _calculate_limit_entry_price(
        self,
        close_price: float,
        average_true_range: float,
    ) -> tuple[float, float]:
        """
        Calculate limit entry price for long and short signals.

        We treat our limit entry as a point between close and take profit.

        :param close_price: Close price.
        :param average_true_range: Average True Range.
        :returns: Limit entry price for long and short signals.
        """

        l_limit = close_price + average_true_range * self.tp_volatility_multiplier / 2
        s_limit = close_price - average_true_range * self.tp_volatility_multiplier / 2

        return l_limit, s_limit
