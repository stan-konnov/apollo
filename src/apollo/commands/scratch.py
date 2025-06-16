import logging

from alpaca.trading.client import TradingClient

from apollo.settings import (
    ALPACA_API_KEY,
    ALPACA_SECRET_KEY,
)
from apollo.utils.common import (
    ensure_environment_is_configured,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s %(asctime)s:\n\n%(message)s\n",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Run isolated logic for development purposes."""

    ensure_environment_is_configured()

    trading_client = TradingClient(
        api_key=ALPACA_API_KEY,
        secret_key=ALPACA_SECRET_KEY,
    )

    position = trading_client.get_open_position("CRWD")
    logger.info(position.model_dump_json(indent=4))  # type: ignore  # noqa: PGH003


if __name__ == "__main__":
    main()
