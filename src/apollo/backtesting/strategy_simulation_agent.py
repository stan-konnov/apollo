from typing import ClassVar

from backtesting import Strategy

from apollo.settings import LONG_SIGNAL, SHORT_SIGNAL, PositionType

"""
As with any other backtesting approach, this one takes on several assumptions:

* We are allowed to trade on close (during extended hours)
* We will get filled on our limit orders
* There are no commissions

These assumptions are partially validated by our broker documentation (Alpaca).

Alpaca indeed allows trading during extended hours (pre-market and after-hours).
Alpaca also allows limit orders, yet there are no guarantees that they will be filled.
Alpaca does not charge trading commissions for US equities, but does for other assets.
"""


class StrategySimulationAgent(Strategy):
    """
    Strategy Simulation Agent is backtesting library wrapper class.

    Simulates trade execution according to signals identified by the strategy.
    Used as one of the components in backtesting process facilitated by runner class.
    """

    # Volatility multiplier applied to
    # ATR for calculating trailing stop loss and take profit
    exit_volatility_multiplier: ClassVar[float]

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

        # Calculate long trailing stop loss and take profit
        long_sl, long_tp = self._calculate_trailing_stop_loss_and_take_profit(
            position_type=PositionType.LONG,
            close_price=close,
            average_true_range=average_true_range,
            exit_volatility_multiplier=self.exit_volatility_multiplier,
        )

        # Calculate short trailing stop loss and take profit
        short_sl, short_tp = self._calculate_trailing_stop_loss_and_take_profit(
            position_type=PositionType.SHORT,
            close_price=close,
            average_true_range=average_true_range,
            exit_volatility_multiplier=self.exit_volatility_multiplier,
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

                # Otherwise, close short position (if any)
                if self.position.is_short:
                    self.position.close()

                # And open new long position, where:
                # stop loss and take profit are our trailing levels
                # and entry is a limit order -- price below or equal close
                self.buy(sl=long_sl, tp=long_tp, limit=close)

            if short_signal:
                # Skip if we already have short position
                if self.position.is_short:
                    return

                # Otherwise, close long position (if any)
                if self.position.is_long:
                    self.position.close()

                # And open new short position, where:
                # stop loss and take profit are our trailing levels
                # and entry is a limit order -- price above or equal close
                self.sell(sl=short_sl, tp=short_tp, limit=close)

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
        position_type: PositionType,
        close_price: float,
        average_true_range: float,
        exit_volatility_multiplier: float,
    ) -> tuple[float, float]:
        """
        Calculate trailing stop loss and take profit.

        Using close, Average True Range, and volatility multiplier.

        Kaufman, Trading Systems and Methods, 2020, 6th ed.

        :param position_type: Position type
        :param close_price: Closing price
        :param average_true_range: Average True Range
        :param exit_volatility_multiplier: Multiplier for ATR
        :returns: Trailing stop loss and take profit levels
        """

        sl = 0.0
        tp = 0.0

        if position_type == PositionType.LONG:
            sl = close_price - average_true_range * exit_volatility_multiplier
            tp = close_price + average_true_range * exit_volatility_multiplier

        else:
            sl = close_price + average_true_range * exit_volatility_multiplier
            tp = close_price - average_true_range * exit_volatility_multiplier

        return sl, tp
