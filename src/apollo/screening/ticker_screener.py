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
from apollo.utils.multiprocessing_capable import MultiprocessingCapable

logger = getLogger(__name__)

"""
TODO: Exclude by liquidity (avoid partial fills).
      Exclude by upcoming earnings (no surprises).
      Exclude by Hurst - avoid brownian motion (no random walk).

TODO: Look into avoiding selecting arbitrary window size.

TODO: modelling and writing the Position with ticker into the database.
"""


class TickerScreener(MultiprocessingCapable):
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

        super().__init__()

        self._sp500_components_scraper = SP500ComponentsScraper()

    def process_in_parallel(self) -> None:
        """Run the screening process in parallel."""

        # Scrape S&P500 components tickers
        sp500_components_tickers = (
            self._sp500_components_scraper.scrape_sp500_components()
        )

        # Break down tickers into equal batches
        batches = self._batch_inputs_collection(sp500_components_tickers)

        # Process each batch in parallel
        with Pool(processes=self._available_cores) as pool:
            # Request the prices
            # and calculate volatility and noise
            # for each ticker in provided batches
            results = pool.map(self._calculate_measures, batches)

            # Flatten the computed results
            flattened_results = [
                ticker_results
                for batch_results in results
                for ticker_results in batch_results
            ]

            # Combine results into single dataframe
            results_dataframe = pd.DataFrame(flattened_results)

            # Select the most suitable ticker
            selected_ticker = self._select_suitable_ticker(results_dataframe)

            logger.info(f"Selected ticker: {selected_ticker}")

    def _calculate_measures(self, tickers: list[str]) -> list[pd.Series]:
        """
        Calculate volatility and noise for each ticker.

        Request historical data for each ticker and calculate volatility
        expressed as Average True Range and noise as Kaufman Efficiency Ratio.

        NOTE: We choose an arbitrary window size for both measures.

        Clearly, there has to be a better,
        data-driven way to determine the optimal window
        size for each measure, but due to the absence of a more
        robust solution we (for now) settle for the last (rolling) trading week.

        Please see SCREENING_WINDOW_SIZE in the settings.

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
                relevant_result = price_dataframe.iloc[-1][
                    ["ticker", "atr", "ker", "adj close"]
                ]

                # Append the result to the list
                result_dataframes.append(relevant_result)

        except EmptyApiResponseError:
            logger.warning("API returned empty response, skipping ticker.")

        return result_dataframes

    def _select_suitable_ticker(self, results_dataframe: pd.DataFrame) -> str:
        """
        Select the most suitable ticker.

        Construct an equal-weighted score based
        on volatility and noise measures and select
        the ticker that falls in the middle of the set.

        We choose the ticker that is closest to the mean score
        since we are looking for the balance between calculated measures.

        Specifically, we are aiming to avoid extremes:
        too high volatility/noise can lead to excessive risk
        while too low volatility/noise can lead to suboptimal returns.

        In such we settle on the ticker that exhibits healthy balance.

        :param results_dataframe: Dataframe with measures.
        :returns: Ticker symbol of the most suitable ticker.
        """

        # First, we normalize ATR against adjusted close
        # to represent it as ratio and not absolute value
        results_dataframe["atr"] = (
            results_dataframe["atr"] / results_dataframe["adj close"]
        )

        # Then, deduce equal
        # weight for each measure:
        # we use a constant value for both
        # since we only have two measures to combine
        weight = 0.5

        # Calculate the combined score
        results_dataframe["atr_ker_score"] = (
            weight * results_dataframe["atr"] + weight * results_dataframe["ker"]
        )

        # Sort the results in descending order
        results_dataframe.sort_values(
            by="atr_ker_score",
            ascending=False,
            inplace=True,
        )

        # Reset the indices to use
        # integer indexing for selection
        results_dataframe.reset_index(inplace=True)

        # Calculate the mean score
        mean_score = results_dataframe["atr_ker_score"].mean()

        # Locate the index that
        # is closest to the mean score
        closest_row_index = int(
            (results_dataframe["atr_ker_score"] - mean_score).abs().idxmin(),
        )

        # And, finally, select the suitable ticker
        return results_dataframe.iloc[closest_row_index]["ticker"]
