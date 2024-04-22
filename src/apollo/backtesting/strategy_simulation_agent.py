from typing import ClassVar

from backtesting import Strategy

from apollo.settings import LONG_SIGNAL, SHORT_SIGNAL


class StrategySimulationAgent(Strategy):
    """
    Strategy Simulation Agent is backtesting library wrapper class.

    Simulates trade execution according to signals identified by the strategy.
    Used as one of the components in backtesting process facilitated by runner class.
    """

    # Stop loss level to use for exits
    stop_loss_level: ClassVar[float]

    # Take profit level to use for exits
    take_profit_level: ClassVar[float]


    def init(self) -> None:
        """
        Initialize the agent.

        NOTE: Backtesting.py requires this method to be implemented.
        """


    def next(self) -> None:
        """
        Process each row in the supplied dataframe.

        Decide whether to enter trade based on identified signal.
        Calculate stop loss and take profit levels.
        Depending on whether the signal is long or short,
        close existing position (if any) and open new one.

        NOTE: Backtesting.py requires this method to be implemented.
        """

        # Get currently iterated signal
        signal_identified = self.data["signal"][-1] != 0

        # Enter the trade if signal identified
        if signal_identified:

            # Identify if signal is long or short
            long_signal = self.data["signal"][-1] == LONG_SIGNAL
            short_signal = self.data["signal"][-1] == SHORT_SIGNAL

            # Grab close of the current row
            close = self.data["Close"][-1]

            if long_signal:

                # Skip if we already have long position
                if self.position.is_long:
                    return

                # Otherwise, close short position (if any)
                if self.position.is_short:
                    self.position.close()

                # Calculate stop loss and take profit levels
                sl, tp = self._calculate_long_sl_and_tp(close)

                # And open new long position
                self.buy(sl=sl, tp=tp)

            if short_signal:

                # Skip if we already have short position
                if self.position.is_short:
                    return

                # Otherwise, close long position (if any)
                if self.position.is_long:
                    self.position.close()

                # Calculate stop loss and take profit levels
                sl, tp = self._calculate_short_sl_and_tp(close)

                # And open new short position
                self.sell(sl=sl, tp=tp)


    def _calculate_long_sl_and_tp(self, close: float) -> tuple[float, float]:
        """
        Calculate long stop loss and take profit.

        Use provided close, stop loss and take profit levels.
        """

        return close * (1 - self.stop_loss_level), close * (1 + self.take_profit_level)


    def _calculate_short_sl_and_tp(self, close: float) -> tuple[float, float]:
        """
        Calculate short stop loss and take profit.

        Use provided close, stop loss and take profit levels.
        """

        return close * (1 + self.stop_loss_level), close * (1 - self.take_profit_level)
