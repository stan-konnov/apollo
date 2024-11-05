import logging
from re import sub
from sys import exit

from bs4 import BeautifulSoup, Tag
from requests import RequestException, get

from apollo.core.errors.scraping import HTMLStructureChangedError
from apollo.settings import SP500_COMPONENTS_URL

logger = logging.getLogger(__name__)


class SP500ComponentsScraper:
    """
    S&P 500 Components Scraper.

    Scraps the list of S&P 500 component tickers from Wikipedia.
    """

    # Constant to represent
    # maximum ticker length
    MAX_TICKER_LENGTH = 5

    def __init__(self) -> None:
        """
        Construct S&P 500 Components Scraper.

        Visit the S&P 500 components page and load it into Beautiful Soup.
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
        Scrape S&P 500 tickers from the page.

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

        # Declare variable to store rows
        sp500_components_rows: list[Tag] = []

        # Find all the rows in the table
        if isinstance(sp500_components_table, Tag):
            sp500_components_rows = sp500_components_table.find_all("tr")

        # And raise if rows are not found
        if not sp500_components_rows:
            raise HTMLStructureChangedError(
                "The HTML structure of the SP500 components table has changed.",
            )

        # Remove the header row as
        # it corresponds to the column names
        sp500_components_rows = sp500_components_rows[1:]

        # Extract tickers from the rows given
        # that the first column contains the ticker
        sp500_components_tickers = [
            row.find_all("td")[0].text
            for row in sp500_components_rows
            if len(row.find_all("td")) > 0 and row.find_all("td")[0].text
        ]

        # And raise if no tickers are found
        if not sp500_components_tickers:
            raise HTMLStructureChangedError(
                "The HTML structure of the SP500 components table row has changed.",
            )

        # Remove any non-alphanumeric
        # characters from the list and return
        sp500_components_tickers = [
            sub("[^0-9a-zA-Z]+", "", ticker) for ticker in sp500_components_tickers
        ]

        # Finally, we assume if there are values
        # longer than five characters, the page structure
        # has changed, since maximum ticker length is five characters
        if any(
            len(ticker) > self.MAX_TICKER_LENGTH for ticker in sp500_components_tickers
        ):
            raise HTMLStructureChangedError(
                "The HTML structure of the SP500 components table row has changed.",
            )

        return sp500_components_tickers
