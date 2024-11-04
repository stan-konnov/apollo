from unittest import mock
from unittest.mock import Mock

import pandas as pd
import pytest

from apollo.calculations.average_true_range import AverageTrueRangeCalculator
from apollo.calculations.kaufman_efficiency_ratio import (
    KaufmanEfficiencyRatioCalculator,
)
from apollo.errors.api import EmptyApiResponseError
from apollo.screening.ticker_screener import TickerScreener
from apollo.settings import END_DATE, FREQUENCY, MAX_PERIOD, START_DATE
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
