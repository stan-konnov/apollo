from datetime import datetime
from logging import getLogger
from multiprocessing import Pool

import pandas as pd
from zoneinfo import ZoneInfo

from apollo.calculators.average_true_range import AverageTrueRangeCalculator
from apollo.calculators.kaufman_efficiency_ratio import (
    KaufmanEfficiencyRatioCalculator,
)
from apollo.connectors.api.yahoo_api_connector import YahooApiConnector
from apollo.connectors.database.postgres_connector import PostgresConnector
from apollo.errors.api import EmptyApiResponseError
from apollo.errors.system_invariants import ScreenedPositionAlreadyExistsError
from apollo.providers.price_data_provider import PriceDataProvider
from apollo.scrapers.sp500_components_scraper import SP500ComponentsScraper
from apollo.settings import (
    END_DATE,
    EXCHANGE,
    EXCHANGE_TIME_ZONE_AND_HOURS,
    FREQUENCY,
    MAX_PERIOD,
    SCREENING_LIQUIDITY_THRESHOLD,
    SCREENING_WINDOW_SIZE,
    START_DATE,
)
from apollo.utils.multiprocessing_capable import MultiprocessingCapable

logger = getLogger(__name__)

"""
Our screening process revolves around three points:

1. Available liquidity at the time of screening.
2. Absence of upcoming earnings within the screening window.
3. Healthy measures of volatility and noise expressed as a combined score.

These measures were chosen based on the following rationale:

At all times we want to be able to enter and exit the
position with minimal slippage and at the desired price.
Additionally, we want to mitigate the risk of partial fills.

We want to avoid any potential surprises
that are associated with earnings announcements.

We are aiming to avoid extremes: too high
volatility/noise can lead to excessive risk,
too low volatility/noise can lead to suboptimal returns.

We ensure that the instrument we are trading
exhibits healthy balance between volatility and noise.

It is important to note, that due to the lack of any kind
of numerical feedback after the process is complete,
we are boxed into two arbitrary decisions:

* We choose the window size for both volatility and noise measures.
* We choose the liquidity threshold after which we consider the ticker.

Please see SCREENING_WINDOW_SIZE and SCREENING_LIQUIDITY_THRESHOLD in the settings.

Additionally, at this point in time (2024-10-30), we are only trading S&P500 components.
"""


class TickerScreener(MultiprocessingCapable):
    """
    Ticker Screener class.

    Responsible for screening various ticker symbols based
    on the measures of liquidity, earnings, volatility and noise
    with the purpose of identifying the most suitable ticker to trade.

    Is multiprocessing capable and runs in parallel.
    """

    def __init__(self) -> None:
        """
        Construct Ticker Screener.

        Initialize API Connector.
        Initialize Database Connector.
        Initialize Price Data Provider.
        Initialize S&P500 Components Scraper.
        """

        super().__init__()

        self._api_connector = YahooApiConnector()
        self._database_connector = PostgresConnector()
        self._price_data_provider = PriceDataProvider()
        self._sp500_components_scraper = SP500ComponentsScraper()

    def process_in_parallel(self) -> None:
        """Run the screening process in parallel."""

        # Query the existing screened position
        existing_screened_position = (
            self._database_connector.get_existing_screened_position()
        )

        # Raise an error if the
        # screened position already exists
        if existing_screened_position:
            raise ScreenedPositionAlreadyExistsError(
                "Screened position for ",
                f"{existing_screened_position.ticker} already exists. "
                "System invariant violated, previous position not dispatched.",
            )

        logger.info("Screening process started.")

        # Scrape S&P500 components tickers
        sp500_components_tickers = (
            self._sp500_components_scraper.scrape_sp500_components()
        )

        # Break down tickers into equal batches
        batches = self._create_batches(sp500_components_tickers)

        # Process each batch in parallel
        with Pool(processes=self._available_cores) as pool:
            # Request prices and
            # earnings date and calculate
            # measure for each ticker in the batch
            results = pool.map(self._calculate_measures, batches)

            # Combine the computed results
            combined_results = pd.concat(results)

            # Select the most suitable ticker
            selected_ticker = self._select_suitable_ticker(combined_results)

            logger.info(
                f"Screening process complete. Selected ticker: {selected_ticker}.",
            )

            # Initialize position in the database
            self._initialize_position(selected_ticker)

    def _calculate_measures(self, tickers: list[str]) -> pd.DataFrame:
        """
        Calculate screening measures for each ticker.

        Request upcoming earnings date for each ticker.

        Request prices for each ticker and calculate liquidity as Dollar Volume,
        volatility as Average True Range, and noise as Kaufman Efficiency Ratio.

        :param tickers: List of tickers to screen.
        :returns: Dataframe with calculated measures.
        """

        # Initialize dataframe for results
        results_dataframe = pd.DataFrame()

        for ticker in tickers:
            try:
                # Request price data for the current ticker
                price_dataframe = self._price_data_provider.get_price_data(
                    ticker=ticker,
                    frequency=str(FREQUENCY),
                    start_date=str(START_DATE),
                    end_date=str(END_DATE),
                    max_period=bool(MAX_PERIOD),
                )

                # Due to hardware constraints,
                # we limit incoming prices to last 30 years
                price_dataframe = price_dataframe[
                    price_dataframe.index
                    >= pd.Timestamp.now() - pd.DateOffset(years=30)
                ]

                # Get upcoming earnings date
                price_dataframe["earnings_date"] = (
                    self._api_connector.request_upcoming_earnings_date(
                        ticker,
                    )
                )

                # Calculate Dollar Volume
                price_dataframe["dollar_volume"] = (
                    price_dataframe["close"] * price_dataframe["volume"]
                )

                # Precalculate previous close necessary for ATR calculation
                price_dataframe["prev_close"] = price_dataframe["adj close"].shift(1)

                # Calculate Average True Range
                atr_calculator = AverageTrueRangeCalculator(
                    dataframe=price_dataframe,
                    # We map to integer from string since
                    # environment variables are expressed as strings
                    window_size=int(str(SCREENING_WINDOW_SIZE)),
                )
                atr_calculator.calculate_average_true_range()

                # Calculate Kaufman Efficiency Ratio
                ker_calculator = KaufmanEfficiencyRatioCalculator(
                    dataframe=price_dataframe,
                    # We map to integer from string since
                    # environment variables are expressed as strings
                    window_size=int(str(SCREENING_WINDOW_SIZE)),
                )
                ker_calculator.calculate_kaufman_efficiency_ratio()

                # For the purposes of screening we are
                # only interested in the most recent values
                relevant_result = pd.DataFrame(
                    [
                        price_dataframe.iloc[-1][
                            [
                                "earnings_date",
                                "dollar_volume",
                                "adj close",
                                "ticker",
                                "atr",
                                "ker",
                            ]
                        ],
                    ],
                )

                # Append the result to the dataframe
                results_dataframe = pd.concat(
                    [results_dataframe, relevant_result],
                )

            except EmptyApiResponseError:  # noqa: PERF203
                logger.warning(
                    f"API returned empty response for {ticker}, skipping ticker.",
                )

                continue

        return results_dataframe

    def _select_suitable_ticker(self, results_dataframe: pd.DataFrame) -> str:
        """
        Select the most suitable ticker.

        Select tickers with Dollar Volume exceeding
        configured quantile (2024-10-30, 0.9 = top 10%).

        Select tickers with no earnings date within
        the configured window size (2024-10-30, 5 days).

        Construct an equal-weighted score based
        on volatility and noise measures and select
        the ticker that falls in the middle of the set.

        :param results_dataframe: Dataframe with measures.
        :returns: Ticker symbol of the most suitable ticker.
        """

        # Include only those tickers with
        # Dollar Volume in configured quantile
        results_dataframe = results_dataframe.loc[
            results_dataframe["dollar_volume"]
            > results_dataframe["dollar_volume"].quantile(
                # We map to float from string since
                # environment variables are expressed as strings
                float(str(SCREENING_LIQUIDITY_THRESHOLD)),
            )
        ]

        # Include only those tickers with no
        # earnings date within the next window
        configured_exchange_date = datetime.now(
            tz=ZoneInfo(EXCHANGE_TIME_ZONE_AND_HOURS[str(EXCHANGE)]["timezone"]),
        ).date()

        # NOTE: we allow tickers that
        # do not yet have earnings announced
        results_dataframe = results_dataframe.loc[
            (
                results_dataframe["earnings_date"].isna()
                | (
                    results_dataframe["earnings_date"]
                    > configured_exchange_date
                    + pd.Timedelta(
                        int(str(SCREENING_WINDOW_SIZE)),
                        unit="D",
                    )
                )
            )
        ]

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

        # Limit the score to two decimal
        # places to avoid floating point errors
        results_dataframe["atr_ker_score"] = results_dataframe["atr_ker_score"].round(2)

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

    def _initialize_position(self, selected_ticker: str) -> None:
        """
        Initialize position in the database.

        :param selected_ticker: Selected ticker to initialize position for.
        """

        # Check if we have an active position for the selected ticker
        existing_active_position = (
            self._database_connector.get_existing_active_position(
                selected_ticker,
            )
        )

        # If we have an active position,
        # log info message and skip the write
        if existing_active_position:
            logger.info(
                f"Active position for {selected_ticker} already exists. "
                f"Status: {existing_active_position.status.value}. "
                "Skipping position creation.",
            )
            return

        # Otherwise, initialize position in the database
        self._database_connector.create_position_on_screening(selected_ticker)
