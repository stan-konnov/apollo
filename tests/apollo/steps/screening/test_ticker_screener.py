import logging
from datetime import datetime
from unittest import mock
from unittest.mock import Mock, patch

import pandas as pd
import pytest
from zoneinfo import ZoneInfo

from apollo.core.calculators.average_true_range import AverageTrueRangeCalculator
from apollo.core.calculators.kaufman_efficiency_ratio import (
    KaufmanEfficiencyRatioCalculator,
)
from apollo.core.errors.api import EmptyApiResponseError
from apollo.core.models.position import Position, PositionStatus
from apollo.settings import (
    END_DATE,
    EXCHANGE,
    EXCHANGE_TIME_ZONE_AND_HOURS,
    FREQUENCY,
    MAX_PERIOD,
    SCREENING_LIQUIDITY_THRESHOLD,
    SCREENING_WINDOW_SIZE,
    START_DATE,
    TICKER,
)
from apollo.steps.screening.ticker_screener import TickerScreener
from tests.fixtures.window_size_and_dataframe import SameDataframe
from tests.utils.precalculate_shared_values import precalculate_shared_values


@pytest.mark.usefixtures("dataframe", "window_size")
def test__calculate_measures__for_correctly_calculating_screening_measures(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test calculate_measures method for correct screening measures calculation.

    Method should request earnings from API Connector.
    Method should request prices from Price Data Provider.
    Method should return dataframe where each row contains measures for each ticker.
    """

    tickers = ["AAPL", "MSFT"]

    ticker_screener = TickerScreener()

    # Mock dependencies on other services
    ticker_screener._api_connector = Mock()  # noqa: SLF001
    ticker_screener._database_connector = Mock()  # noqa: SLF001
    ticker_screener._price_data_provider = Mock()  # noqa: SLF001
    ticker_screener._sp500_components_scraper = Mock()  # noqa: SLF001

    # Mimic the return value of Price Data Provider
    ticker_screener._price_data_provider.get_price_data.return_value = dataframe  # noqa: SLF001

    # Precalculate shared values
    dataframe = precalculate_shared_values(dataframe)

    # Calculate control measures
    control_dataframe = dataframe.copy()
    control_dataframe["dollar_volume"] = dataframe["close"] * dataframe["volume"]

    atr_calculator = AverageTrueRangeCalculator(
        dataframe=control_dataframe,
        window_size=window_size,
    )
    atr_calculator.calculate_average_true_range()

    ker_calculator = KaufmanEfficiencyRatioCalculator(
        dataframe=control_dataframe,
        window_size=window_size,
    )
    ker_calculator.calculate_kaufman_efficiency_ratio()

    # Run tickers through the screening process
    screened_dataframe = ticker_screener._calculate_measures(tickers)  # noqa: SLF001

    # Check that we requested price data for each ticker
    ticker_screener._price_data_provider.get_price_data.assert_has_calls(  # noqa: SLF001
        [
            mock.call(
                ticker=tickers[0],
                frequency=str(FREQUENCY),
                start_date=str(START_DATE),
                end_date=str(END_DATE),
                max_period=bool(MAX_PERIOD),
            ),
            mock.call(
                ticker=tickers[1],
                frequency=str(FREQUENCY),
                start_date=str(START_DATE),
                end_date=str(END_DATE),
                max_period=bool(MAX_PERIOD),
            ),
        ],
    )

    # Check that we requested earnings date for each ticker
    ticker_screener._api_connector.request_upcoming_earnings_date.assert_has_calls(  # noqa: SLF001
        [
            mock.call(tickers[0]),
            mock.call(tickers[1]),
        ],
    )

    assert len(screened_dataframe) == len(tickers)

    # Since we are using identical
    # price inputs for both tickers
    # we can compare the results directly
    # without filtering by individual ticker
    # NOTE: we also care only about last entry
    assert (
        control_dataframe["dollar_volume"].iloc[-1]
        == screened_dataframe["dollar_volume"].iloc[-1]
    )
    assert control_dataframe["atr"].iloc[-1] == screened_dataframe["atr"].iloc[-1]
    assert control_dataframe["ker"].iloc[-1] == screened_dataframe["ker"].iloc[-1]

    assert "earnings_date" in screened_dataframe.columns
    assert "dollar_volume" in screened_dataframe.columns
    assert "adj close" in screened_dataframe.columns
    assert "ticker" in screened_dataframe.columns
    assert "atr" in screened_dataframe.columns
    assert "ker" in screened_dataframe.columns


def test__calculate_measures__for_skipping_ticker_if_api_returned_empty_response(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """
    Test calculate_measures method for skipping if API returned empty response.

    Resulting dataframe must not contain ticker with empty API response.
    Ticker Screener must log a warning message.
    """

    tickers = ["AAPL"]

    ticker_screener = TickerScreener()

    ticker_screener._api_connector = Mock()  # noqa: SLF001
    ticker_screener._database_connector = Mock()  # noqa: SLF001
    ticker_screener._price_data_provider = Mock()  # noqa: SLF001
    ticker_screener._sp500_components_scraper = Mock()  # noqa: SLF001

    # Mimic the exception raised by Price Data Provider
    ticker_screener._price_data_provider.get_price_data.side_effect = (  # noqa: SLF001
        EmptyApiResponseError
    )

    screened_dataframe = ticker_screener._calculate_measures(tickers)  # noqa: SLF001

    assert len(screened_dataframe) == 0
    assert (
        f"API returned empty response for {tickers[0]}, skipping ticker." in caplog.text
    )


@pytest.mark.usefixtures("screened_tickers_dataframe")
def test__select_suitable_ticker__for_correct_selection(
    screened_tickers_dataframe: pd.DataFrame,
) -> None:
    """
    Test select_suitable_ticker method for correct selection.

    Method should filter screened ticker based on liquidity threshold.
    Method should filter screened ticker based on upcoming earnings date.
    Method should filter screened ticker based on the combined ATR and KER score.
    """

    ticker_screener = TickerScreener()

    ticker_screener._api_connector = Mock()  # noqa: SLF001
    ticker_screener._database_connector = Mock()  # noqa: SLF001
    ticker_screener._price_data_provider = Mock()  # noqa: SLF001
    ticker_screener._sp500_components_scraper = Mock()  # noqa: SLF001

    control_screened_ticker_dataframe = screened_tickers_dataframe.copy()

    control_screened_ticker_dataframe = control_screened_ticker_dataframe.loc[
        control_screened_ticker_dataframe["dollar_volume"]
        > control_screened_ticker_dataframe["dollar_volume"].quantile(
            float(str(SCREENING_LIQUIDITY_THRESHOLD)),
        )
    ]

    configured_exchange_date = datetime.now(
        tz=ZoneInfo(EXCHANGE_TIME_ZONE_AND_HOURS[str(EXCHANGE)]["timezone"]),
    ).date()

    control_screened_ticker_dataframe = control_screened_ticker_dataframe.loc[
        (
            control_screened_ticker_dataframe["earnings_date"].isna()
            | (
                control_screened_ticker_dataframe["earnings_date"]
                > configured_exchange_date
                + pd.Timedelta(
                    int(str(SCREENING_WINDOW_SIZE)),
                    unit="D",
                )
            )
        )
    ]

    control_screened_ticker_dataframe["atr"] = (
        control_screened_ticker_dataframe["atr"]
        / control_screened_ticker_dataframe["adj close"]
    )

    weight = 0.5

    control_screened_ticker_dataframe["atr_ker_score"] = (
        weight * control_screened_ticker_dataframe["atr"]
        + weight * control_screened_ticker_dataframe["ker"]
    )

    control_screened_ticker_dataframe["atr_ker_score"] = (
        control_screened_ticker_dataframe["atr_ker_score"].round(2)
    )

    control_screened_ticker_dataframe.sort_values(
        by="atr_ker_score",
        ascending=False,
        inplace=True,
    )

    control_screened_ticker_dataframe.reset_index(inplace=True)

    mean_score = control_screened_ticker_dataframe["atr_ker_score"].mean()

    closest_row_index = int(
        (control_screened_ticker_dataframe["atr_ker_score"] - mean_score)
        .abs()
        .idxmin(),
    )

    control_selected_ticker = control_screened_ticker_dataframe.iloc[closest_row_index][
        "ticker"
    ]

    selected_ticker = ticker_screener._select_suitable_ticker(  # noqa: SLF001
        screened_tickers_dataframe,
    )

    assert control_selected_ticker == selected_ticker


@pytest.mark.usefixtures("screened_tickers_dataframe")
def test__select_suitable_ticker__for_avoiding_tickers_with_upcoming_earnings(
    screened_tickers_dataframe: pd.DataFrame,
) -> None:
    """
    Test select_suitable_ticker method for avoiding tickers with earnings.

    Method should not return any of the tickers with upcoming earnings.
    """

    ticker_screener = TickerScreener()

    ticker_screener._api_connector = Mock()  # noqa: SLF001
    ticker_screener._database_connector = Mock()  # noqa: SLF001
    ticker_screener._price_data_provider = Mock()  # noqa: SLF001
    ticker_screener._sp500_components_scraper = Mock()  # noqa: SLF001

    screened_tickers_dataframe.reset_index(inplace=True)

    ticker_with_upcoming_earnings = screened_tickers_dataframe.iloc[0:5][
        "ticker"
    ].to_numpy()

    # Set earnings date to tomorrow for first 5 tickers
    screened_tickers_dataframe.loc[
        screened_tickers_dataframe["ticker"].isin(ticker_with_upcoming_earnings),
        "earnings_date",
    ] = datetime.now(tz=ZoneInfo("UTC")).date() + pd.Timedelta(1, unit="D")

    # Set earnings date to None for the rest of the tickers
    screened_tickers_dataframe.loc[
        ~screened_tickers_dataframe["ticker"].isin(ticker_with_upcoming_earnings),
        "earnings_date",
    ] = None

    selected_ticker = ticker_screener._select_suitable_ticker(  # noqa: SLF001
        screened_tickers_dataframe,
    )

    assert selected_ticker not in ticker_with_upcoming_earnings


def test__initialize_position__for_creating_position_if_no_active_position_exists() -> (
    None
):
    """
    Test initialize_position method for creating position if no position exists.

    Method should call Database Connector to create position on screening.
    """

    ticker_screener = TickerScreener()

    ticker_screener._api_connector = Mock()  # noqa: SLF001
    ticker_screener._database_connector = Mock()  # noqa: SLF001
    ticker_screener._price_data_provider = Mock()  # noqa: SLF001
    ticker_screener._sp500_components_scraper = Mock()  # noqa: SLF001

    ticker_screener._database_connector.get_existing_active_position.return_value = None  # noqa: SLF001

    ticker_screener._initialize_position(str(TICKER))  # noqa: SLF001

    ticker_screener._database_connector.create_position_on_screening.assert_called_once_with(  # noqa: SLF001
        str(TICKER),
    )


def test__initialize_position__for_not_creating_position_if_position_exists(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """
    Test initialize_position method for not creating position if position exists.

    Method should log info message and return early.
    Method should not call Database Connector to create position on screening.
    """

    caplog.set_level(logging.INFO)

    ticker_screener = TickerScreener()

    ticker_screener._api_connector = Mock()  # noqa: SLF001
    ticker_screener._database_connector = Mock()  # noqa: SLF001
    ticker_screener._price_data_provider = Mock()  # noqa: SLF001
    ticker_screener._sp500_components_scraper = Mock()  # noqa: SLF001

    existing_active_position = Position(
        ticker=str(TICKER),
        status=PositionStatus.SCREENED,
    )

    ticker_screener._database_connector.get_existing_active_position.return_value = (  # noqa: SLF001
        existing_active_position
    )

    ticker_screener._initialize_position(str(TICKER))  # noqa: SLF001

    assert (
        str(
            f"Active position for {TICKER} already exists. "
            f"Status: {existing_active_position.status.value}. "
            "Skipping position creation.",
        )
        in caplog.text
    )

    ticker_screener._database_connector.create_position_on_screening.assert_not_called()  # noqa: SLF001


@pytest.mark.usefixtures("screened_tickers_dataframe")
@pytest.mark.parametrize(
    "multiprocessing_pool",
    ["apollo.steps.screening.ticker_screener.Pool"],
    indirect=True,
)
def test__process_in_parallel__for_correct_screening_process(
    screened_tickers_dataframe: pd.DataFrame,
    multiprocessing_pool: Mock,
) -> None:
    """
    Test process_in_parallel method for correct screening process.

    Method must call SP500 Components Scraper to scrape SP500 components.
    Method must call calculate_measures method in parallel for each batch.
    Method must call select_suitable_ticker method to select suitable ticker.
    Method must call initialize_position method to initialize position in the database.
    """

    ticker_screener = TickerScreener()

    ticker_screener._api_connector = Mock()  # noqa: SLF001
    ticker_screener._database_connector = Mock()  # noqa: SLF001
    ticker_screener._price_data_provider = Mock()  # noqa: SLF001
    ticker_screener._sp500_components_scraper = Mock()  # noqa: SLF001

    # Mock the results of the SP500 components scraping
    tickers_to_screen = screened_tickers_dataframe["ticker"].to_numpy()
    ticker_screener._sp500_components_scraper.scrape_sp500_components.return_value = (  # noqa: SLF001
        tickers_to_screen
    )

    # Mock Ticker Screener private methods
    # to assert they have been called after the process
    with patch.object(
        TickerScreener,
        "_select_suitable_ticker",
    ) as select_suitable_ticker, patch.object(
        TickerScreener,
        "_initialize_position",
    ) as initialize_position:
        # Mock the return value of the map method as
        # list of dataframes, each for each scraped ticker
        screened_results = [
            pd.DataFrame([row], columns=screened_tickers_dataframe.columns)
            for _, row in screened_tickers_dataframe.iterrows()
        ]
        multiprocessing_pool.map.return_value = screened_results

        # Mock the return value of
        # the select_suitable_ticker method
        select_suitable_ticker.return_value = str(TICKER)

        # Run the screening process
        ticker_screener.process_in_parallel()

        # Assert that we scraped the SP500 components
        ticker_screener._sp500_components_scraper.scrape_sp500_components.assert_called_once()  # noqa: SLF001

        # Assert that we called our calculation method in parallel
        multiprocessing_pool.map.assert_called_once_with(
            ticker_screener._calculate_measures,  # noqa: SLF001
            ticker_screener._create_batches(tickers_to_screen),  # noqa: SLF001
        )

        # Assert that we selected suitable ticker
        # from the results of the screening process
        select_suitable_ticker.assert_called_once_with(
            # Please see tests/fixtures/window_size_and_dataframe.py
            # for explanation on SameDataframe class
            SameDataframe(pd.concat(screened_results)),
        )

        # Assert that we initialized
        # position for the selected ticker
        initialize_position.assert_called_once_with(str(TICKER))
