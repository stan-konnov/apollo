from typing import ClassVar

from backtesting import Strategy

from apollo.settings import LONG_SIGNAL, SHORT_SIGNAL, PositionType


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

        # We should come precalculated
        multiplier = 2
        lowest_price = 50
        highest_price = 100
        average_true_range = 10

        # Loop through open positions and calculate trailing stop loss
        for trade in self.trades:
            if trade.is_long:
                trade.sl = self._calculate_trailing_stop_loss(
                    position_type=PositionType.LONG,
                    limit_price=highest_price,
                    average_true_range=average_true_range,
                    volatility_multiplier=multiplier,
                )
            else:
                trade.sl = self._calculate_trailing_stop_loss(
                    position_type=PositionType.SHORT,
                    limit_price=lowest_price,
                    average_true_range=average_true_range,
                    volatility_multiplier=multiplier,
                )

        # Get currently iterated signal
        signal_identified = self.data["signal"][-1] != 0

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

                # Calculate stop loss and take profit levels
                sl, tp = self._calculate_long_sl_and_tp(close)

                # And open new long position
                self.buy(tp=tp)

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
                self.sell(tp=tp)

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

    def _calculate_trailing_stop_loss(
        self,
        position_type: PositionType,
        limit_price: float,
        average_true_range: float,
        volatility_multiplier: float,
    ) -> float:
        """
        Calculate trailing stop loss.

        Using Average True Range (ATR), multiplier and
        highest high (for long) or lowest low (for short).

        Kaufman, Trading Systems and Methods, 2020, 6th ed.

        :param position_type: Position type
        :param limit_price: Highest or lowest price
        :param average_true_range: Average True Range
        :param volatility_multiplier: Multiplier for ATR
        :returns: Trailing Stop Loss
        """

        if position_type == PositionType.LONG:
            return limit_price - volatility_multiplier * average_true_range

        return limit_price + volatility_multiplier * average_true_range
