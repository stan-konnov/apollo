### On Alpaca Extended Hours Trading

* To indicate an order is eligible for extended hours trading,
you need to supply a boolean parameter named `extended_hours` to your order request.
By setting this parameter to true, the order will be eligible to execute in the pre-market or after-hours.

* Only limit day orders will be accepted as extended hours eligible.
All other order types and TIFs will be rejected with an error.
You must adhere to these settings in order to participate in extended hours:

* The order type must be set to `limit` (with a limit price).
Any other type of orders will be rejected with an error.
Time-in-force must be set to be `day`. Any other time_in_force will be rejected with an error.

</br>

### On Alternatives

* IBKR does allow for `stop` orders execution during extended hours, which proved to severely outperform limit orders in backtesting.

* There are, though, a few issues

    1. Maintaining brokerage session involves weekly re-authentication
    2. IBKR charges commissions

* There are a few open source libraries built to ease the connection hiccup:
    https://github.com/erdewit/ib_insync

* There are workarounds to automate IBKR API (TWS/Gateway):

    1. Install TWS
    2. Login using credentials
    3. Download IB API source code
    4. Use Python to connect to TWS
    5. Follow: https://algotrading101.com/learn/interactive-brokers-python-api-native-guide/


### On Orders:

* Immediate or Cancel (IOC)
  An IOC order mandates that whatever amount of an order that can be executed in the market (or at a limit)
  in a very short time span, often just a few seconds or less, be filled and then the rest of the order canceled.
  If no shares are traded in that "immediate" interval, then the order is canceled completely.

* Fill or Kill (FOK)
  This type of order combines an AON order with an IOC specification; in other words,
  it mandates that the entire order size be traded and in a very short time period,
  often a few seconds or less. If neither condition is met, the order is canceled.