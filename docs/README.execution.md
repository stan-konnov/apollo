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