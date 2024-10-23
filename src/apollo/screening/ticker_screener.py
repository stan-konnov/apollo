from apollo.scrapers.sp500_components_scraper import SP500ComponentsScraper


class TickerScreener:
    """
    Ticker Screener class.

    Is responsible for screening various ticker symbols
    based on the measures of volatility and noise with the
    purpose of identifying the most suitable instrument to trade.

    Makes use of S&P 500 Components Scraper to get the list of S&P500 tickers.

    Is multiprocessing capable and runs in parallel.
    """

    def __init__(self) -> None:
        """
        Construct Ticker Screener.

        Initializes S&P500 Components Scraper.
        """

        self._sp500_components_scraper = SP500ComponentsScraper()
