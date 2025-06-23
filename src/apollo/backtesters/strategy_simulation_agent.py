from typing import ClassVar

from backtesting import Strategy

from apollo.core.order_brackets_calculator import OrderBracketsCalculator
from apollo.settings import LONG_SIGNAL, SHORT_SIGNAL


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
            OrderBracketsCalculator.calculate_trailing_stop_loss_and_take_profit(
                close_price=close,
                average_true_range=average_true_range,
                sl_volatility_multiplier=self.sl_volatility_multiplier,
                tp_volatility_multiplier=self.tp_volatility_multiplier,
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
            long_limit, short_limit = (
                OrderBracketsCalculator.calculate_limit_entry_price(
                    close_price=close,
                    average_true_range=average_true_range,
                    tp_volatility_multiplier=self.tp_volatility_multiplier,
                )
            )

            if long_signal:
                # Skip if we already have long position
                if self.position.is_long:
                    return

                # And open new long position, where entry is a
                # limit order -- price below or equal our limit
                self.buy(limit=long_limit)

            if short_signal:
                # Skip if we already have short position
                if self.position.is_short:
                    return

                # And open new short position, where entry is a
                # limit order -- price above or equal our limit
                self.sell(limit=short_limit)

        # Loop through open positions
        # And assign SL and TP to open position(s)
        for trade in self.trades:
            if trade.is_long:
                trade.sl = long_sl
                trade.tp = long_tp
            else:
                trade.sl = short_sl
                trade.tp = short_tp
