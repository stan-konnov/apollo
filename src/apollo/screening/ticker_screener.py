class TickerScreener:
    """
    Ticker Screener class.

    Is responsible for screening various ticker symbols
    based on the measures of volatility and noise with the
    purpose of identifying the most suitable instrument to trade.

    Makes use of SP500ComponentsScraper to get the list of S&P500 tickers for screening.
    """
