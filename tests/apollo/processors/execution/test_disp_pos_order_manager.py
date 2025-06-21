import contextlib
from unittest.mock import Mock

import pytest
import timeout_decorator
from freezegun import freeze_time

from apollo.errors.system_invariants import (
    DispatchedPositionDoesNotExistError,
    OpenPositionAlreadyExistsError,
)
from apollo.models.position import Position, PositionStatus
from apollo.processors.execution.disp_pos_order_manager import (
    DispatchedPositionOrderManager,
)
from apollo.settings import TICKER


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
def test__handle_dispatched_position__for_placing_limit_order() -> None:
    """Test handle_dispatched_position method for placing limit order."""

    disp_pos_order_manager = DispatchedPositionOrderManager()
    disp_pos_order_manager._trading_client = Mock()  # noqa: SLF001

    control_stop_loss = 100.0
    control_take_profit = 150.0
    control_target_entry_price = 120.0

    disp_pos_order_manager._database_connector = Mock()  # noqa: SLF001
    disp_pos_order_manager._database_connector.get_position_by_status.return_value = (  # noqa: SLF001
        Position(
            id="test",
            ticker=str(TICKER),
            status=PositionStatus.DISPATCHED,
            stop_loss=control_stop_loss,
            take_profit=control_take_profit,
            target_entry_price=control_target_entry_price,
        )
    )

    with contextlib.suppress(timeout_decorator.TimeoutError):
        disp_pos_order_manager.handle_dispatched_position()

    # Need a fixture for get position by status reused
    # assert call with specific arguments
    disp_pos_order_manager._trading_client.submit_order.assert_any_call()  # noqa: SLF001
