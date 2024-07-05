import logging

from apollo.api.yahoo_api_connector import YahooApiConnector
from apollo.settings import TICKER

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s %(asctime)s:\n\n%(message)s\n",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Quickly iterate on new concepts."""

    yahoo_api_connector = YahooApiConnector(
        ticker=str(TICKER),
        max_period=True,
    )

    yahoo_api_connector.request_or_read_prices()


if __name__ == "__main__":
    main()
