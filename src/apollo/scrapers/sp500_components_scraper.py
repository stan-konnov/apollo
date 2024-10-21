from bs4 import BeautifulSoup
from requests import get

from apollo.settings import SP500_COMPONENTS_URL


class SP500ComponentsScraper:
    """
    S&P 500 Components Scraper.

    Scraps the list of S&P 500 components from Wikipedia.
    """

    def __init__(self) -> None:
        """
        Construct S&P 500 Components Scraper.

        Visit the URL with S&P 500 components and load it into beautiful soup.
        """

        self._sp500_components_page = BeautifulSoup(
            get(url=str(SP500_COMPONENTS_URL), timeout=10).text,
            "html.parser",
        )
