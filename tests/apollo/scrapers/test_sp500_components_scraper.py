import logging
from unittest.mock import Mock, patch

import pytest
from requests import RequestException

from apollo.scrapers.sp500_components_scraper import SP500ComponentsScraper


@patch(
    "apollo.scrapers.sp500_components_scraper.SP500_COMPONENTS_URL",
    "http://doesnotexist.com/notfound",
)
def test__sp500_components_scraper__for_raising_and_exiting_if_page_is_not_found(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """
    Test SP500 Components Scraper for raising and exiting if page is not found.

    SP500 Components Scraper must log an exception and exit with code 1.
    """

    caplog.set_level(logging.ERROR)

    with pytest.raises(SystemExit) as exception:
        SP500ComponentsScraper()

    assert (
        str(
            "Failed to load S&P 500 components page. "
            "Please check the URL and network connection.",
        )
        in caplog.text
    )

    assert exception.value.code == 1


@pytest.mark.parametrize(
    "requests_get_call",
    ["apollo.scrapers.sp500_components_scraper.get"],
    indirect=True,
)
def test__sp500_components_scraper__for_raising_and_exiting_if_page_cannot_be_accessed(
    requests_get_call: Mock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """
    Test SP500 Components Scraper for raising and exiting if page cannot be accessed.

    SP500 Components Scraper must log an exception and exit with code 1.
    """

    caplog.set_level(logging.ERROR)
    requests_get_call.side_effect = RequestException

    with pytest.raises(SystemExit) as exception:
        SP500ComponentsScraper()

    assert (
        str(
            "Failed to load S&P 500 components page. "
            "Please check the URL and network connection.",
        )
        in caplog.text
    )

    assert exception.value.code == 1
