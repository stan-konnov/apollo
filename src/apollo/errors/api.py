from enum import Enum


class EmptyYahooApiResponseError(Exception):
    """Raised when the Yahoo API returns an empty response."""


class RequestToAlpacaAPIFailedError(Exception):
    """Raised when a request to the Alpaca API fails."""


class AlpacaAPIErrorCodes(int, Enum):
    """Enum for Alpaca API error codes."""

    POSITION_DOES_NOT_EXIST = 40410000
