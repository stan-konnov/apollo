import pandas as pd

from apollo.settings import ValidYahooApiFrequencies


def empty_yahoo_api_response(
        tickers: str | list[str],  # noqa: ARG001
        start: str,  # noqa: ARG001
        end: str,  # noqa: ARG001
        interval: str = ValidYahooApiFrequencies.ONE_DAY.value,  # noqa: ARG001
    ) -> pd.DataFrame:
    """
    Simulate empty Yahoo API OHLCV response.

    :param tickers: Ticker to request prices for.
    :param start: Start point to request prices from (inclusive).
    :param end: End point until which to request prices (exclusive).
    :param interval: Frequency of requested prices.
    :returns: Empty dataframe.
    """

    return pd.DataFrame()


def yahoo_api_response(
        tickers: str | list[str],  # noqa: ARG001
        start: str,
        end: str,
        interval: str = ValidYahooApiFrequencies.ONE_DAY.value,  # noqa: ARG001
    ) -> pd.DataFrame:
    """
    Simulate raw Yahoo API OHLCV response.

    :param tickers: Ticker to request prices for.
    :param start: Start point to request prices from (inclusive).
    :param end: End point until which to request prices (exclusive).
    :param interval: Frequency of requested prices.
    :returns: Dataframe with OHLCV data.
    """

    raw_yahoo_api_response = pd.DataFrame(
        {
            "Date": [start, end], "Open": [100.0, 101.0], "High": [105.0, 106.0],
            "Low":  [95.0, 96.0], "Close": [99.0, 100.0], "Volume": [1000, 2000],
        },
    )
    raw_yahoo_api_response.set_index("Date", inplace=True)

    return raw_yahoo_api_response
