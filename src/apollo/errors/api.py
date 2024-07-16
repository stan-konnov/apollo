class ApiResponseEmptyDataframeError(Exception):
    """Raised when the API returns an empty response."""

    def __init__(self) -> None:
        """Construct Api Response Empty Dataframe Error."""

        super().__init__("API response returned empty dataframe.")


class ApiResponseDatetimeIndexError(Exception):
    """Raised when dataframe returned by API is not indexed by datetime."""

    def __init__(self) -> None:
        """Construct Api Response Datetime Index Error."""

        super().__init__("Dataframe received from API is not indexed by datetime.")
