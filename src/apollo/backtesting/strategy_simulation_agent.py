from typing import ClassVar

from backtesting import Strategy

from apollo.settings import LONG_SIGNAL, SHORT_SIGNAL

"""
https://docs.alpaca.markets/docs/orders-at-alpaca

!1. After hours, we are allowed only limit orders.

!2. There is not execution guarantee, so we assume we fill on next open.

!3. TIF is day, therefore, any non-filled position older than a day is cancelled.

!4. Brackets are not allowed. We manually compute SL/TP and send as separate orders.
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

    def next(self) -> None:  # noqa: C901
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

        # If by now we have outstanding
        # orders it means they were not filled.
        # We cancel them to adhere to the execution
        if len(self.orders) > 0:
            self.orders[0].cancel()

        # Enter the trade if signal identified
        if signal_identified:
            # Identify if signal is long or short
            long_signal = self.data["signal"][-1] == LONG_SIGNAL
            short_signal = self.data["signal"][-1] == SHORT_SIGNAL

            # Calculate limit entry price for long and short signals
            long_limit, short_limit = self._calculate_limit_entry_price(
                close,
                average_true_range,
            )

            if long_signal:
                # Skip if we already have long position
                if self.position.is_long:
                    return

                # Otherwise, close short position (if any)
                if self.position.is_short:
                    self.position.close()

                # And open new long position, where:
                # stop loss and take profit are our trailing levels
                # and entry is a limit order -- price below or equal our limit
                self.buy(limit=long_limit)

            if short_signal:
                # Skip if we already have short position
                if self.position.is_short:
                    return

                # Otherwise, close long position (if any)
                if self.position.is_long:
                    self.position.close()

                # And open new short position, where:
                # stop loss and take profit are our trailing levels
                # and entry is a limit order -- price above or equal our limit
                self.sell(limit=short_limit)

        # Loop through open positions
        # And assign SL and TP to open position(s)
        #
        # Given the internals of the library, this will
        # effectively close the position if SL or TP is hit
        # on the next open, adhering to broker-imposed limitations
        #
        # NOTE: in reality this would translate into two separate
        # buy or sell limit orders executed at market price given
        # price meets conditions and, thus, are not true SL/TP orders
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
