from datetime import datetime
from typing import Generator
from unittest.mock import patch

import pandas as pd
import pytest

from apollo.settings import (
    DEFAULT_DATE_FORMAT,
    END_DATE,
    START_DATE,
)

"""
TODO:

API_RESPONSE_DATAFRAME should be made into fixture

How can we mock response from patch of yahoo_api_response?

The mocking of patch should be resolved first, since
it relies on API_RESPONSE_DATAFRAME variable, which is not a fixture.

Or, perhaps, _yahoo_api_response can use api_response_dataframe fixture
and then return it, therefore, also patching the download() function from the library.
"""

API_RESPONSE_DATAFRAME = pd.DataFrame(
    {
        "Date": [
            datetime.strptime(str(START_DATE), DEFAULT_DATE_FORMAT),
            datetime.strptime(str(END_DATE), DEFAULT_DATE_FORMAT),
        ],
        "Open": [100.0, 101.0],
        "High": [105.0, 106.0],
        "Low": [95.0, 96.0],
        "Close": [99.0, 100.0],
        "Adj Close": [98.0, 99.0],
        "Volume": [1000, 2000],
    },
)
API_RESPONSE_DATAFRAME.set_index("Date", inplace=True)


@pytest.fixture(name="yahoo_api_call")
def yahoo_api_call() -> Generator[None, None, None]:
    """Simulate call to Yahoo API."""

    with patch("apollo.connectors.api.yahoo_api_connector.download") as mocked_call:
        yield mocked_call
