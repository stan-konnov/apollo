import logging
import re
from sys import exit

from bs4 import BeautifulSoup, Tag
from requests import RequestException, get

from apollo.errors.scraping import HTMLStructureChangedError
from apollo.settings import SP500_COMPONENTS_URL

logger = logging.getLogger(__name__)


class SP500ComponentsScraper:
    """
    S&P 500 Components Scraper.

    Scraps the list of S&P 500 components from Wikipedia.
    """

    def __init__(self) -> None:
        """
        Construct S&P 500 Components Scraper.

        Visit the URL with S&P 500 components and load it into beautiful soup.

        :raises RequestException: If the page cannot be loaded.
        """

        try:
            self._sp500_components_page = BeautifulSoup(
                get(url=str(SP500_COMPONENTS_URL), timeout=10).text,
                "html.parser",
            )

        except RequestException:
            logger.exception(
                "Failed to load S&P 500 components page. "
                "Please check the URL and network connection.",
            )

            # At this point, we should exit
            # as we cannot proceed without the page
            exit(1)

    def scrape_sp500_components(self) -> list[str]:
        """
        Scrape S&P 500 components.

        :returns: List of strings representing S&P 500 components.

        :raises HTMLStructureChangedError: If the page HTML structure has changed.
        """

        # Find the table with S&P 500 components
        sp500_components_table = self._sp500_components_page.find(
            "table",
            {"id": "constituents"},
        )

        # Raise if table is not found
        if sp500_components_table is None:
            raise HTMLStructureChangedError(
                "The HTML structure of the SP500 components page has changed.",
            )

        # Find all rows in the table
        if isinstance(sp500_components_table, Tag):
            sp500_components_rows = sp500_components_table.find_all("tr")

        # Raise if rows are not found
        else:
            raise HTMLStructureChangedError(
                "The HTML structure of the SP500 components page has changed.",
            )

        # Remove the header row
        sp500_components_rows = sp500_components_rows[1:]

        # Extract ticker symbols from the rows
        sp500_components_tickers = [
            row.find_all("td")[0].text for row in sp500_components_rows
        ]

        # Remove any non-alphanumeric
        # characters from the tickers and return
        return [
            re.sub("[^0-9a-zA-Z]+", "", ticker) for ticker in sp500_components_tickers
        ]
