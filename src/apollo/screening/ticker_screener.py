from logging import getLogger
from multiprocessing import Pool

import pandas as pd

from apollo.calculations.average_true_range import AverageTrueRangeCalculator
from apollo.calculations.kaufman_efficiency_ratio import (
    KaufmanEfficiencyRatioCalculator,
)
from apollo.errors.api import EmptyApiResponseError
from apollo.providers.price_data_provider import PriceDataProvider
from apollo.scrapers.sp500_components_scraper import SP500ComponentsScraper
from apollo.settings import (
    END_DATE,
    FREQUENCY,
    MAX_PERIOD,
    SCREENING_WINDOW_SIZE,
    START_DATE,
)

logger = getLogger(__name__)


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

        # Set the number of
        # batches to split tickers into
        # NOTE: due to API limitations we
        # are limited to 10 connections at a time
        batch_count = 10

        # Split tickers into batches
        ticker_batches = self._batch_tickers(
            batch_count=batch_count,
            tickers_to_batch=sp500_components_tickers,
        )

        # Process each batch in parallel
        with Pool(processes=batch_count) as pool:
            # Request the prices
            # and calculate volatility and noise
            # for each ticker in provided batches
            results = pool.map(
                self._calculate_volatility_and_noise,
                ticker_batches,
            )

            # Flatten the computed results
            flattened_results = [
                ticker_results
                for batch_results in results
                for ticker_results in batch_results
            ]

            # Combine results into single dataframe
            results_dataframe = pd.DataFrame(flattened_results).transpose()

            logger.info(results_dataframe)

    def _batch_tickers(
        self,
        batch_count: int,
        tickers_to_batch: list[str],
    ) -> list[list[str]]:
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

    def _calculate_volatility_and_noise(self, tickers: list[str]) -> list[pd.Series]:
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
        result_dataframes: list[pd.Series] = []

        try:
            for ticker in tickers:
                # Request price data for the current ticker
                price_dataframe = price_data_provider.get_price_data(
                    ticker=ticker,
                    frequency=str(FREQUENCY),
                    start_date=str(START_DATE),
                    end_date=str(END_DATE),
                    max_period=bool(MAX_PERIOD),
                )

                """
                TODO: Move shared values into separate calculator
                """

                # Precalculate previous close necessary for ATR calculation
                price_dataframe["prev_close"] = price_dataframe["adj close"].shift(1)

                # Instantiate Average True Range calculator
                atr_calculator = AverageTrueRangeCalculator(
                    dataframe=price_dataframe,
                    # We map to integer from string since
                    # environment variables are expressed as strings
                    window_size=int(str(SCREENING_WINDOW_SIZE)),
                )

                # Calculate Average True Range
                atr_calculator.calculate_average_true_range()

                # Calculate Kaufman Efficiency Ratio
                ker_calculator = KaufmanEfficiencyRatioCalculator(
                    dataframe=price_dataframe,
                    # We map to integer from string since
                    # environment variables are expressed as strings
                    window_size=int(str(SCREENING_WINDOW_SIZE)),
                )

                # Calculate Kaufman Efficiency Ratio
                ker_calculator.calculate_kaufman_efficiency_ratio()

                # For the purposes of screening we are
                # only interested in the most recent values
                # of Average True Range and Kaufman Efficiency Ratio
                relevant_result = price_dataframe.iloc[-1][["ticker", "atr", "ker"]]

                # Append the result to the list
                result_dataframes.append(relevant_result)

        except EmptyApiResponseError:
            """
            TODO: Manage empty responses better
            """
            logger.warning("API returned empty response, skipping ticker")

        return result_dataframes
