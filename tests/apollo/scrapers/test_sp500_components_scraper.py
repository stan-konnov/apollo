import logging
from unittest.mock import Mock, patch

import pytest
from requests import RequestException

from apollo.errors.scraping import HTMLStructureChangedError
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


@pytest.mark.parametrize(
    "requests_get_call",
    ["apollo.scrapers.sp500_components_scraper.get"],
    indirect=True,
)
@pytest.mark.usefixtures("sp500_components_page")
def test__sp500_components_scraper__for_raising_and_exiting_if_table_cannot_be_found(
    requests_get_call: Mock,
    sp500_components_page: str,
) -> None:
    """
    Test SP500 Components Scraper for raising HTMLStructureChangedError.

    If the table with S&P 500 components cannot be located on the accessed page.
    """

    requests_get_call.return_value = Mock(text=sp500_components_page)
    sp500_components_scraper = SP500ComponentsScraper()

    # Remove table with S&P 500 components from the page
    sp500_components_scraper._sp500_components_page.find(  # noqa: SLF001
        "table",
        {"id": "constituents"},
    ).decompose()  # type: ignore  # noqa: PGH003

    exception_message = "The HTML structure of the SP500 components page has changed."

    with pytest.raises(
        HTMLStructureChangedError,
        match=exception_message,
    ) as exception:
        sp500_components_scraper.scrape_sp500_components()

    assert str(exception.value) == exception_message
