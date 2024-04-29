from typing import ClassVar

from backtesting import Strategy

from apollo.settings import LONG_SIGNAL, SHORT_SIGNAL, PositionType

# Assumptions:
# * are we sure we always running exclusively, non-overlapping trades?
# * we assume that trade-on-close is available to us
# * we assume no commission are applied (!)
# * we assume no slippage happens (!)

# On trailing SL:
# * Sometimes applied above TP in case of long positions (!)
# This has to be investigated: if stop will be placed above TP, will it get executed
# at current price below stop?

# On backtesting API:
# * Play with limit and stop properties available on self.buy() and self.sell()
# * Capturing the spread with limit/stop, something-something?
# * Work with limit orders, as current backtesting still applies market orders


class StrategySimulationAgent(Strategy):
    """
    Strategy Simulation Agent is backtesting library wrapper class.

    Simulates trade execution according to signals identified by the strategy.
    Used as one of the components in backtesting process facilitated by runner class.
    """

    # Percentage representation of trailing
    # take profit level for all trades to aim at
    take_profit_level: ClassVar[float]

    # Volatility multiplier applied to
    # ATR for calculating trailing stop loss
    sl_volatility_multiplier: ClassVar[float]

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

        # Grab lowest low and highest high of the current row
        lowest_low = self.data["l_low"][-1]
        highest_high = self.data["h_high"][-1]

        # Grab average true range of the current row
        average_true_range = self.data["atr"][-1]

        # Get currently iterated signal
        signal_identified = self.data["signal"][-1] != 0

        # Calculate long trailing stop loss and take profit
        long_sl, long_tp = self._calculate_trailing_stop_loss_and_take_profit(
            position_type=PositionType.LONG,
            close_price=close,
            limit_price=highest_high,
            average_true_range=average_true_range,
            sl_volatility_multiplier=self.sl_volatility_multiplier,
        )

        # Calculate short trailing stop loss and take profit
        short_sl, short_tp = self._calculate_trailing_stop_loss_and_take_profit(
            position_type=PositionType.SHORT,
            close_price=close,
            limit_price=lowest_low,
            average_true_range=average_true_range,
            sl_volatility_multiplier=self.sl_volatility_multiplier,
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

                # And open new long position
                self.buy()

            if short_signal:
                # Skip if we already have short position
                if self.position.is_short:
                    return

                # Otherwise, close long position (if any)
                if self.position.is_long:
                    self.position.close()

                # And open new short position
                self.sell()

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
        limit_price: float,
        average_true_range: float,
        sl_volatility_multiplier: float,
    ) -> tuple[float, float]:
        """
        Calculate trailing stop loss and take profit.

        Using highest high, lowest low, close,
        Average True Range, and volatility multiplier.

        Kaufman, Trading Systems and Methods, 2020, 6th ed.

        :param position_type: Position type
        :param close_price: Closing price
        :param limit_price: Highest or lowest price
        :param average_true_range: Average True Range
        :param sl_volatility_multiplier: Multiplier for ATR
        :returns: Trailing stop loss and take profit levels
        """

        sl = 0.0
        tp = 0.0

        if position_type == PositionType.LONG:
            sl = limit_price - average_true_range * sl_volatility_multiplier
            tp = close_price * (1 + self.take_profit_level)

        else:
            sl = limit_price + average_true_range * sl_volatility_multiplier
            tp = close_price * (1 - self.take_profit_level)

        return sl, tp
