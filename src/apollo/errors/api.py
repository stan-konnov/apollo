from enum import Enum


class EmptyYahooApiResponseError(Exception):
    """Raised when the Yahoo API returns an empty response."""


class RequestToAlpacaAPIFailedError(Exception):
    """Raised when a request to the Alpaca API fails."""


class AlpacaAPIErrorMessages(Enum, str):
    """Enum for Alpaca API error messages."""

    POSITION_DOES_NOT_EXIST = "Position does not exist."
