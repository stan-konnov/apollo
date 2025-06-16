import logging
from typing import TYPE_CHECKING, Any

from alpaca.trading.client import TradingClient

# NOTE: we require this unused import
# to be able to register event handlers
import apollo.events.event_handlers  # noqa: F401
from apollo.settings import (
    ALPACA_API_KEY,
    ALPACA_SECRET_KEY,
)
from apollo.utils.common import (
    ensure_environment_is_configured,
)

if TYPE_CHECKING:
    from alpaca.trading.models import TradeAccount

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

    _account_client: TradeAccount | dict[str, Any] = trading_client.get_account()

    position = trading_client.get_open_position("CRWD")
    logger.info(f"Positions: {position}")


if __name__ == "__main__":
    main()
