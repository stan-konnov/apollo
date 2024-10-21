from typing import Generator
from unittest.mock import Mock, patch

import pytest


@pytest.fixture(name="requests_get_call")
def requests_get_call_fixture() -> Generator[Mock, None, None]:
    """Simulate call to requests.get."""

    with patch("apollo.scrapers.sp500_components_scraper.get") as mock_requests_get:
        yield mock_requests_get
