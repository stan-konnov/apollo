from unittest.mock import Mock

import pytest

from apollo.errors.system_invariants import OpenPositionAlreadyExistsError
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
