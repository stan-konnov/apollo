class ApiResponseEmptyDataframeError(Exception):
    """Raised when the API returns an empty response."""


class ApiResponseDatetimeIndexError(Exception):
    """Raised when dataframe returned by API is not indexed by datetime."""
