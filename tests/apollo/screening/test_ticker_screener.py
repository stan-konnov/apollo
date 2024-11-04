from unittest import mock
from unittest.mock import Mock

import pandas as pd
import pytest

from apollo.screening.ticker_screener import TickerScreener
from apollo.settings import END_DATE, FREQUENCY, MAX_PERIOD, START_DATE


@pytest.mark.usefixtures("dataframe", "window_size")
def test__calculate_measures__for_correctly_calculating_screening_measures(
    dataframe: pd.DataFrame,
    window_size: int,  # noqa: ARG001
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

    control_dataframe = ticker_screener._calculate_measures(tickers)  # noqa: SLF001

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

    assert len(control_dataframe) == len(tickers)

    assert "earnings_date" in control_dataframe.columns
    assert "dollar_volume" in control_dataframe.columns
    assert "adj close" in control_dataframe.columns
    assert "ticker" in control_dataframe.columns
    assert "atr" in control_dataframe.columns
    assert "ker" in control_dataframe.columns
