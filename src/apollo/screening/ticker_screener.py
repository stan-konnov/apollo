from apollo.scrapers.sp500_components_scraper import SP500ComponentsScraper


class TickerScreener:
    """
    Ticker Screener class.

    Is responsible for screening various ticker symbols
    based on the measures of volatility and noise with the
    purpose of identifying the most suitable instrument to trade.

    Is multiprocessing capable and runs in parallel.
    """

    def __init__(self) -> None:
        """
        Construct Ticker Screener.

        Initializes S&P500 Components Scraper.
        """

        self._sp500_components_scraper = SP500ComponentsScraper()

    def identify_suitable_ticker(self) -> None:
        """
        Identify suitable ticker for trading.

        Screens tickers based on volatility expressed
        via Average True Range and noise via Kaufman Efficiency Ratio.
        """

        self._sp500_components_scraper.scrape_sp500_components()
