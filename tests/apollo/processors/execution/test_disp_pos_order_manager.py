import contextlib
from datetime import datetime
from json import dumps
from unittest.mock import Mock
from uuid import uuid4
from zoneinfo import ZoneInfo

import pytest
import timeout_decorator
from alpaca.common.exceptions import APIError
from alpaca.trading.enums import (
    AccountStatus,
    AssetClass,
    AssetExchange,
    OrderSide,
    PositionSide,
    TimeInForce,
)
from alpaca.trading.models import Position as AlpacaPosition
from alpaca.trading.models import TradeAccount
from alpaca.trading.requests import LimitOrderRequest
from freezegun import freeze_time

from apollo.errors.api import AlpacaAPIErrorCodes, RequestToAlpacaAPIFailedError
from apollo.errors.system_invariants import (
    DispatchedPositionDoesNotExistError,
    OpenPositionAlreadyExistsError,
)
from apollo.models.position import Position, PositionStatus
from apollo.processors.execution.disp_pos_order_manager import (
    DispatchedPositionOrderManager,
)
from apollo.settings import LONG_SIGNAL, TICKER


def mock_get_position_by_status(
    position_status: PositionStatus,
) -> Position | None:
    """
    Conditional mock for get_position_by_status.

    :param position_status: Position status to mock.
    :returns: Position if status is DISPATCHED, None otherwise.
    """

    if position_status == PositionStatus.DISPATCHED:
        return Position(
            id="test",
            ticker=str(TICKER),
            status=position_status,
            direction=LONG_SIGNAL,
            stop_loss=100.0,
            take_profit=150.0,
            target_entry_price=125.0,
        )

    return None


@pytest.mark.parametrize(
    "trading_client",
    ["apollo.processors.execution.base_order_manager.TradingClient"],
    indirect=True,
)
@pytest.mark.usefixtures("trading_client")
def test__handle_dispatched_position__for_raising_error_if_open_position_exists() -> (
    None
):
    """
    Test handle_dispatched_position method for raising error.

    Method must raise OpenPositionAlreadyExistsError.
    """

    disp_pos_order_manager = DispatchedPositionOrderManager()

    disp_pos_order_manager._database_connector = Mock()  # noqa: SLF001
    disp_pos_order_manager._database_connector.get_position_by_status.return_value = (  # noqa: SLF001
        Position(
            id="test",
            ticker=str(TICKER),
            status=PositionStatus.OPEN,
        )
    )

    exception_message = (
        "Open position exists while handling dispatched signal. "
        "System invariant violated, position was not closed or cancelled."
    )

    with pytest.raises(
        OpenPositionAlreadyExistsError,
        match=exception_message,
    ) as exception:
        disp_pos_order_manager.handle_dispatched_position()

    assert str(exception.value) == exception_message


@pytest.mark.parametrize(
    "trading_client",
    ["apollo.processors.execution.base_order_manager.TradingClient"],
    indirect=True,
)
@pytest.mark.usefixtures("trading_client")
def test__handle_dispatched_position__for_raising_error_if_disp_position_does_not_exist() -> (  # noqa: E501
    None
):
    """
    Test handle_dispatched_position method for raising error.

    Method must raise DispatchedPositionDoesNotExistError.
    """

    disp_pos_order_manager = DispatchedPositionOrderManager()

    disp_pos_order_manager._database_connector = Mock()  # noqa: SLF001
    disp_pos_order_manager._database_connector.get_position_by_status.return_value = (  # noqa: SLF001
        None
    )

    exception_message = (
        "Dispatched position does not exist while handling dispatched signal. "
        "System invariant violated, position was not dispatched."
    )

    with pytest.raises(
        DispatchedPositionDoesNotExistError,
        match=exception_message,
    ) as exception:
        disp_pos_order_manager.handle_dispatched_position()

    assert str(exception.value) == exception_message


# Assume today date is Monday
# 2025-06-23 10:00 ET = 14:00 UTC (trading hours)
@freeze_time("2025-06-23 14:00:00")
@pytest.mark.parametrize(
    "trading_client",
    ["apollo.processors.execution.base_order_manager.TradingClient"],
    indirect=True,
)
@pytest.mark.usefixtures("trading_client")
def test__handle_dispatched_position__for_placing_limit_order(
    trading_client: Mock,
) -> None:
    """Test handle_dispatched_position method for placing limit order."""

    disp_pos_order_manager = DispatchedPositionOrderManager()

    disp_pos_order_manager._trading_client = trading_client  # noqa: SLF001

    # Mock the account client such that
    # we can properly test quantity calculation
    control_trade_account = TradeAccount(
        id=uuid4(),
        account_number="test_account",
        status=AccountStatus.ACTIVE,
        non_marginable_buying_power="10000",
    )
    disp_pos_order_manager._account_client = control_trade_account  # noqa: SLF001

    # Mock the trading client to return an open position
    # so that we can test the successful placement of the order
    disp_pos_order_manager._trading_client.get_open_position.return_value = (  # noqa: SLF001
        AlpacaPosition(
            qty="10",
            asset_id=uuid4(),
            cost_basis="1250",
            symbol=str(TICKER),
            avg_entry_price="125",
            side=PositionSide.LONG,
            exchange=AssetExchange.NYSE,
            asset_class=AssetClass.US_EQUITY,
        )
    )

    # Mock the database connector to return a dispatched position
    disp_pos_order_manager._database_connector = Mock()  # noqa: SLF001
    disp_pos_order_manager._database_connector.get_position_by_status.side_effect = (  # noqa: SLF001
        mock_get_position_by_status
    )

    disp_pos_order_manager.handle_dispatched_position()

    # Control values that must
    # result from computation between
    # position from the mock and the account client
    control_ticker = str(TICKER)

    control_limit_price = 125.0

    control_order_quantity = int(
        float(control_trade_account.non_marginable_buying_power)  # type: ignore  # noqa: PGH003
        / control_limit_price,
    )

    control_order_side = (
        OrderSide.BUY
        if disp_pos_order_manager._database_connector.get_position_by_status(  # noqa: SLF001
            PositionStatus.DISPATCHED,
        ).direction
        == LONG_SIGNAL
        else OrderSide.SELL
    )

    disp_pos_order_manager._trading_client.submit_order.assert_called_once_with(  # noqa: SLF001
        order_data=LimitOrderRequest(
            symbol=control_ticker,
            limit_price=control_limit_price,
            qty=control_order_quantity,
            side=control_order_side,
            time_in_force=TimeInForce.IOC,
        ),
    )


# Assume today date is Monday
# 2025-06-23 09:00 ET = 13:00 UTC (before trading hours)
@timeout_decorator.timeout(3)
@freeze_time("2025-06-23 13:00:00")
@pytest.mark.parametrize(
    "trading_client",
    ["apollo.processors.execution.base_order_manager.TradingClient"],
    indirect=True,
)
@pytest.mark.usefixtures("trading_client")
def test__handle_dispatched_position__for_not_placing_order_outside_of_market_hours(
    trading_client: Mock,
) -> None:
    """Test handle_dispatched_position method for not placing order."""

    disp_pos_order_manager = DispatchedPositionOrderManager()
    disp_pos_order_manager._trading_client = trading_client  # noqa: SLF001

    # Mock the database connector to return a dispatched position
    disp_pos_order_manager._database_connector = Mock()  # noqa: SLF001
    disp_pos_order_manager._database_connector.get_position_by_status.side_effect = (  # noqa: SLF001
        mock_get_position_by_status
    )

    with contextlib.suppress(timeout_decorator.TimeoutError):
        disp_pos_order_manager.handle_dispatched_position()

    disp_pos_order_manager._trading_client.submit_order.assert_not_called()  # noqa: SLF001


# Assume today date is Monday
# 2025-06-23 10:00 ET = 14:00 UTC
@freeze_time("2025-06-23 14:00:00")
@pytest.mark.parametrize(
    "trading_client",
    ["apollo.processors.execution.base_order_manager.TradingClient"],
    indirect=True,
)
@pytest.mark.usefixtures("trading_client")
def test__handle_dispatched_position__for_synchronizing_position_after_placing_order(
    trading_client: Mock,
) -> None:
    """Test handle_dispatched_position method for synchronizing position."""

    disp_pos_order_manager = DispatchedPositionOrderManager()
    disp_pos_order_manager._trading_client = trading_client  # noqa: SLF001

    # Mock the database connector to return a dispatched position
    disp_pos_order_manager._database_connector = Mock()  # noqa: SLF001
    disp_pos_order_manager._database_connector.get_position_by_status.side_effect = (  # noqa: SLF001
        mock_get_position_by_status
    )

    # Mock the trading client to return an open position
    # so that we can test the successful placement of the order
    disp_pos_order_manager._trading_client.get_open_position.return_value = (  # noqa: SLF001
        AlpacaPosition(
            qty="10",
            asset_id=uuid4(),
            cost_basis="1250",
            symbol=str(TICKER),
            avg_entry_price="125",
            side=PositionSide.LONG,
            exchange=AssetExchange.NYSE,
            asset_class=AssetClass.US_EQUITY,
        )
    )

    disp_pos_order_manager.handle_dispatched_position()

    disp_pos_order_manager._database_connector.update_position_by_status.assert_called_once_with(  # noqa: SLF001
        "test",
        PositionStatus.OPEN,
    )

    disp_pos_order_manager._database_connector.update_position_on_signal_execution.assert_called_once_with(  # noqa: SLF001
        position_id="test",
        entry_price=125.0,
        entry_date=datetime.now(tz=ZoneInfo("UTC")),
        unit_size=10.0,
        cash_size=1250.0,
    )


# Assume today date is Monday
# 2025-06-23 15:50 ET = 19:50 UTC (market about to close)
@freeze_time("2025-06-23 19:50:00")
@pytest.mark.parametrize(
    "trading_client",
    ["apollo.processors.execution.base_order_manager.TradingClient"],
    indirect=True,
)
@pytest.mark.usefixtures("trading_client")
def test__handle_dispatched_position__for_synchronizing_position_if_position_not_opened(
    trading_client: Mock,
) -> None:
    """Test handle_dispatched_position method for synchronizing position."""

    disp_pos_order_manager = DispatchedPositionOrderManager()
    disp_pos_order_manager._trading_client = trading_client  # noqa: SLF001

    # Mock the database connector to return a dispatched position
    disp_pos_order_manager._database_connector = Mock()  # noqa: SLF001
    disp_pos_order_manager._database_connector.get_position_by_status.side_effect = (  # noqa: SLF001
        mock_get_position_by_status
    )

    # Mock the trading client to raise an error
    disp_pos_order_manager._trading_client.get_open_position.side_effect = APIError(  # noqa: SLF001
        error=dumps(
            {
                "code": AlpacaAPIErrorCodes.POSITION_DOES_NOT_EXIST.value,
            },
        ),
    )

    # NOTE: we suppress our
    # internal error here since
    # due to the nature of the execution
    # during tests, it would always be raised
    # even though we have conditions to handle it
    with contextlib.suppress(RequestToAlpacaAPIFailedError):
        disp_pos_order_manager.handle_dispatched_position()

    disp_pos_order_manager._database_connector.update_position_by_status.assert_called_once_with(  # noqa: SLF001
        "test",
        PositionStatus.CANCELLED,
    )


# Assume today date is Monday
# 2025-06-23 10:00 ET = 14:00 UTC
@freeze_time("2025-06-23 14:00:00")
@pytest.mark.parametrize(
    "trading_client",
    ["apollo.processors.execution.base_order_manager.TradingClient"],
    indirect=True,
)
@pytest.mark.usefixtures("trading_client")
def test__handle_dispatched_position__for_rasing_error_if_communication_with_api_failed(
    trading_client: Mock,
) -> None:
    """Test handle_dispatched_position method for synchronizing position."""

    disp_pos_order_manager = DispatchedPositionOrderManager()
    disp_pos_order_manager._trading_client = trading_client  # noqa: SLF001

    # Mock the database connector to return a dispatched position
    disp_pos_order_manager._database_connector = Mock()  # noqa: SLF001
    disp_pos_order_manager._database_connector.get_position_by_status.side_effect = (  # noqa: SLF001
        mock_get_position_by_status
    )

    # Mock the trading client to raise an error
    disp_pos_order_manager._trading_client.get_open_position.side_effect = APIError(  # noqa: SLF001
        error=dumps(
            {
                "code": 12345,
            },
        ),
    )

    exception_message = (
        "Failed to synchronize position with Alpaca API. "
        "Please check the logs for more details."
    )

    with pytest.raises(
        RequestToAlpacaAPIFailedError,
        match=exception_message,
    ) as exception:
        disp_pos_order_manager.handle_dispatched_position()

    assert str(exception.value) == exception_message
