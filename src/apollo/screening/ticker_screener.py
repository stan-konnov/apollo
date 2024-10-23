from multiprocessing import cpu_count

import pandas as pd

from apollo.calculations.average_true_range import AverageTrueRangeCalculator
from apollo.calculations.kaufman_efficiency_ratio import (
    KaufmanEfficiencyRatioCalculator,
)
from apollo.providers.price_data_provider import PriceDataProvider
from apollo.scrapers.sp500_components_scraper import SP500ComponentsScraper
from apollo.settings import (
    END_DATE,
    FREQUENCY,
    MAX_PERIOD,
    SCREENING_WINDOW_SIZE,
    START_DATE,
)


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

    def _calculate_volatility_and_noise(self, tickers: list[str]) -> list[pd.DataFrame]:
        """
        Calculate volatility and noise for each ticker.

        Request historical data for each ticker and calculate volatility
        expressed as Average True Range and noise as Kaufman Efficiency Ratio.

        :param tickers: List of tickers to screen.
        :returns: List of DataFrames with volatility and noise measures.
        """

        # Instantiate price data provider
        price_data_provider = PriceDataProvider()

        # Initialize list to store the results
        result_dataframes: list[pd.DataFrame] = []

        for ticker in tickers:
            # Request price data for the current ticker
            price_dataframe = price_data_provider.get_price_data(
                ticker=ticker,
                frequency=str(FREQUENCY),
                start_date=str(START_DATE),
                end_date=str(END_DATE),
                max_period=bool(MAX_PERIOD),
            )

            # Instantiate Average True Range calculator
            atr_calculator = AverageTrueRangeCalculator(
                dataframe=price_dataframe,
                window_size=int(str(SCREENING_WINDOW_SIZE)),
            )

            # Calculate Average True Range
            atr_calculator.calculate_average_true_range()

            # Calculate Kaufman Efficiency Ratio
            ker_calculator = KaufmanEfficiencyRatioCalculator(
                dataframe=price_dataframe,
                window_size=int(str(SCREENING_WINDOW_SIZE)),
            )

            # Calculate Kaufman Efficiency Ratio
            ker_calculator.calculate_kaufman_efficiency_ratio()

        return result_dataframes
