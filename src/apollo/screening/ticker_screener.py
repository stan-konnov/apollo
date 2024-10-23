from multiprocessing import cpu_count

from apollo.scrapers.sp500_components_scraper import SP500ComponentsScraper


class TickerScreener:
    """
    Ticker Screener class.

    Responsible for screening various ticker symbols
    based on the measures of volatility and noise with the
    purpose of identifying the most suitable ticker to trade.

    Is multiprocessing capable and runs in parallel.
    """

    def __init__(self) -> None:
        """
        Construct Ticker Screener.

        Initializes S&P500 Components Scraper.
        """

        self._sp500_components_scraper = SP500ComponentsScraper()

    def screen_in_parallel(self) -> None:
        """Run the screening process in parallel."""

        # Scrape S&P500 components tickers
        sp500_components_tickers = (
            self._sp500_components_scraper.scrape_sp500_components()
        )

        # Get the number of available CPU cores
        available_cores = cpu_count()

        # Split tickers into batches
        _ticker_batches = self._batch_tickers(
            batch_count=available_cores,
            tickers_to_batch=sp500_components_tickers,
        )

    def _batch_tickers(
        self,
        batch_count: int,
        tickers_to_batch: list[str],
    ) -> list[str]:
        """
        Split scraper tickers into equal batches.

        :param batch_count: Number of batches to split tickers into.
        :param tickers_to_batch: List of tickers to split into batches.
        :returns: List of batches with tickers.
        """

        # Calculate the total number of tickers
        tickers_count = len(tickers_to_batch)

        # Calculate the base size of each batch
        base_batch_size = tickers_count // batch_count

        # Calculate the size of the remainder batch
        remainder_batch_size = tickers_count % batch_count

        start_index = 0
        batches_to_return = []

        # Iterate over the number of batches
        for i in range(batch_count):
            # Calculate the current batch size
            current_batch_size = base_batch_size + (
                1 if i < remainder_batch_size else 0
            )

            # Slice and append the current batch
            batches_to_return.append(
                tickers_to_batch[start_index : start_index + current_batch_size],
            )

            # Update the start index for the next batch
            start_index += current_batch_size

        return batches_to_return
