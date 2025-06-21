import contextlib
from unittest.mock import Mock
from uuid import uuid4

import pytest
import timeout_decorator
from alpaca.trading.enums import AssetClass, AssetExchange, PositionSide
from alpaca.trading.models import Position as AlpacaPosition
from freezegun import freeze_time

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
def test__handle_dispatched_position__for_raising_error_if_dispatched_position_does_not_exist() -> (  # noqa: E501
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
@timeout_decorator.timeout(3)
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

    disp_pos_order_manager._database_connector = Mock()  # noqa: SLF001
    disp_pos_order_manager._database_connector.get_position_by_status.side_effect = (  # noqa: SLF001
        mock_get_position_by_status
    )

    with contextlib.suppress(timeout_decorator.TimeoutError):
        disp_pos_order_manager.handle_dispatched_position()

    disp_pos_order_manager._trading_client.submit_order.assert_called_once()  # noqa: SLF001
