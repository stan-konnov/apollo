from typing import ClassVar

from backtesting import Strategy

from apollo.core.order_brackets_calculator import OrderBracketsCalculator
from apollo.settings import LONG_SIGNAL, SHORT_SIGNAL

"""
The step-by-step of matching the nature of
backtesting library with realities of execution is following:

----

Or entries backtested as limit orders traded on close.
In the context of the library, this would translate to filling
the limit order on the next open, given the price meets the conditions.

To mirror this approach during trade execution,
we resolve to placing limit orders on market open.

Since we also want to factor in the risk of partial fills,
we dispatch our orders as IOC (Immediate or Cancel) orders.

This ensures that we fill at least the portion of the
order at desired price, while the rest is cancelled.

Clearly, this does skew the results of the backtest,
yet this is the closest approximation we can make given the limitations.

More on IOC orders: https://docs.alpaca.markets/docs/orders-at-alpaca#time-in-force

NOTE: as of 2024-10-17, this is up to debate and has to be
tested against simple limit orders when the execution module is ready.

----

We backtest attaching dynamic Stop Loss and Take Profit levels.
In the context of the library, this would translate to filling
those orders on the next open, given the price meets the conditions.

To mirror this approach during trade execution, we resolve
to placing OCO (One Cancels Other) orders on next market open.

OCO orders are two-legged orders where one leg cancels the other
given it is filled. This ensures that we either hit our Stop Loss
or Take Profit level, while the other order is cancelled.

More on OCO orders: https://docs.alpaca.markets/docs/orders-at-alpaca#time-in-force

---

We backtest exclusive orders and closing positions on counter signals.
In the context of the library, this would translate to ignoring
any signal if we already have similar (long or short) position.

Additionally, we would close the position
on the next open if we receive a counter signal
and open a new position in the opposite direction.

To mirror this approach during trade execution, we resolve to closing the position
on the next open if we receive a counter signal via limit or market order
and opening a new position in the opposite direction via IOC order.

NOTE: as of 2024-10-17, this is up to debate and using either
limit or market order has to be tested when the execution module is ready.

---

Given the above, our Trade Lifecycle is following:

(T+0 AH): Generate a signal after market close.

(T+1 MH): Place a limit IOC order on market open.

(T+1 AH): Generate another signal after market close.

(T+1 AH): Generate Stop Loss and Take Profit levels after market close.

(T+2 MH): Ignore non-counter signal and Place OCO order on market open to close.

(T+2 MH): Use counter signal and place market/limit order on market open to close.

(T+2 MH): Given previous step, place IOC order on market open to open counter position.

In case we received a signal for another security and
we have an open position, we resolve to the following logic:

If we received counter signal for the same security,
we close the position on the next open and open a new for another security.

Otherwise, if we did not receive a counter for the same security, we ignore signal
for another security and place a OCO order on market open for currently open position.

---

Further considerations:

Our broker does not charge commissions, yet, if one
does not pay in commissions, one pays in slippage and spread.

At this point in time, we do not have enough data to
approximate the slippage and, thus, we do not yet factor it in.

More on orders: https://docs.alpaca.markets/docs/orders-at-alpaca
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
                    close,
                    average_true_range,
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
