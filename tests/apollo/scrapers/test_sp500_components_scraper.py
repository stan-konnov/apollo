import logging
from unittest.mock import Mock, patch

import pytest
from bs4 import Tag
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
def test__sp500_components_scraper__for_raising_if_table_cannot_be_found(
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


@pytest.mark.parametrize(
    "requests_get_call",
    ["apollo.scrapers.sp500_components_scraper.get"],
    indirect=True,
)
@pytest.mark.usefixtures("sp500_components_page")
def test__sp500_components_scraper__for_raising_if_rows_cannot_be_found(
    requests_get_call: Mock,
    sp500_components_page: str,
) -> None:
    """
    Test SP500 Components Scraper for raising HTMLStructureChangedError.

    If the rows with S&P 500 components cannot be located on the accessed page.
    """

    requests_get_call.return_value = Mock(text=sp500_components_page)
    sp500_components_scraper = SP500ComponentsScraper()

    sp500_components_table = sp500_components_scraper._sp500_components_page.find(  # noqa: SLF001
        "table",
        {"id": "constituents"},
    )

    # Remove rows with S&P 500 components from the page
    if isinstance(sp500_components_table, Tag):
        for row in sp500_components_table.find_all("tr"):
            row.decompose()

    exception_message = "The HTML structure of the SP500 components table has changed."

    with pytest.raises(
        HTMLStructureChangedError,
        match=exception_message,
    ) as exception:
        sp500_components_scraper.scrape_sp500_components()

    assert str(exception.value) == exception_message


@pytest.mark.parametrize(
    "requests_get_call",
    ["apollo.scrapers.sp500_components_scraper.get"],
    indirect=True,
)
@pytest.mark.usefixtures("sp500_components_page")
def test__sp500_components_scraper__for_raising_if_tickers_cannot_be_found(
    requests_get_call: Mock,
    sp500_components_page: str,
) -> None:
    """
    Test SP500 Components Scraper for raising HTMLStructureChangedError.

    If the tickers of S&P 500 components cannot be located on the accessed page.
    """

    requests_get_call.return_value = Mock(text=sp500_components_page)
    sp500_components_scraper = SP500ComponentsScraper()

    sp500_components_table = sp500_components_scraper._sp500_components_page.find(  # noqa: SLF001
        "table",
        {"id": "constituents"},
    )

    if isinstance(sp500_components_table, Tag):
        sp500_components_rows = sp500_components_table.find_all("tr")
        sp500_components_rows = sp500_components_rows[1:]

        # Mutate first cells of
        # each row into empty strings
        for row in sp500_components_rows:
            row.find_all("td")[0].string = ""

    exception_message = (
        "The HTML structure of the SP500 components table row has changed."
    )

    with pytest.raises(
        HTMLStructureChangedError,
        match=exception_message,
    ) as exception:
        sp500_components_scraper.scrape_sp500_components()

    assert str(exception.value) == exception_message


@pytest.mark.parametrize(
    "requests_get_call",
    ["apollo.scrapers.sp500_components_scraper.get"],
    indirect=True,
)
@pytest.mark.usefixtures("sp500_components_page")
def test__sp500_components_scraper__for_raising_if_tickers_are_malformed(
    requests_get_call: Mock,
    sp500_components_page: str,
) -> None:
    """
    Test SP500 Components Scraper for raising HTMLStructureChangedError.

    If the tickers of S&P 500 components cannot be located on the accessed page.
    """

    requests_get_call.return_value = Mock(text=sp500_components_page)
    sp500_components_scraper = SP500ComponentsScraper()

    sp500_components_table = sp500_components_scraper._sp500_components_page.find(  # noqa: SLF001
        "table",
        {"id": "constituents"},
    )

    if isinstance(sp500_components_table, Tag):
        sp500_components_rows = sp500_components_table.find_all("tr")
        sp500_components_rows = sp500_components_rows[1:]

        # Mutate the first ticker into an invalid string
        sp500_components_rows[0].find_all("td")[0].string = "INVALID"

    exception_message = (
        "The HTML structure of the SP500 components table row has changed."
    )

    with pytest.raises(
        HTMLStructureChangedError,
        match=exception_message,
    ) as exception:
        sp500_components_scraper.scrape_sp500_components()

    assert str(exception.value) == exception_message


@pytest.mark.parametrize(
    "requests_get_call",
    ["apollo.scrapers.sp500_components_scraper.get"],
    indirect=True,
)
@pytest.mark.usefixtures("sp500_components_page")
def test__sp500_components_scraper__for_scraping_list_of_sp500_tickers(
    requests_get_call: Mock,
    sp500_components_page: str,
) -> None:
    """
    Test SP500 Components Scraper for scraping list of S&P 500 tickers.

    Scraper must return a list of strings representing S&P 500 components.

    Returned list length must be equal to the number of S&P 500 components.
    Returned list element must not include any non-alphanumeric characters.
    """

    # 2024-10-22:
    # Index contains 503 stocks
    # because it includes two share classes
    # of stock from 4 of its component companies
    current_number_of_tickers = 503

    requests_get_call.return_value = Mock(text=sp500_components_page)
    sp500_components_scraper = SP500ComponentsScraper()

    sp500_components_tickers = sp500_components_scraper.scrape_sp500_components()

    assert len(sp500_components_tickers) == current_number_of_tickers
    assert all(ticker.isalnum() for ticker in sp500_components_tickers)
