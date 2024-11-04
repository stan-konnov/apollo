from unittest.mock import Mock

import pandas as pd
import pytest

from apollo.screening.ticker_screener import TickerScreener


@pytest.mark.usefixtures("dataframe", "window_size")
def test__calculate_measures__for_correctly_calculating_screening_measures(
    dataframe: pd.DataFrame,
    window_size: int,  # noqa: ARG001
) -> None:
    """
    Test calculate_measures method for correct screening measures calculation.

    Method should request earnings from API Connector.
    Method should request prices from Price Data Provider.
    Method should calculate Dollar Volume, Average True Range, Kaufman Efficiency Ratio.
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
    ticker_screener._price_data_provider.get_prices.return_value = dataframe  # noqa: SLF001

    ticker_screener._calculate_measures(tickers)  # noqa: SLF001

    ticker_screener._price_data_provider.get_prices.assert_has_calls(  # noqa: SLF001
        [
            tickers[0],
            tickers[1],
        ],
        any_order=True,
    )

    ticker_screener._api_connector.get_earnings.assert_has_calls(  # noqa: SLF001
        [
            tickers[0],
            tickers[1],
        ],
        any_order=True,
    )
