from unittest.mock import Mock

import pytest

from apollo.errors.system_invariants import DispatchedPositionAlreadyExistsError
from apollo.models.position import Position, PositionStatus
from apollo.processors.signal_dispatcher import SignalDispatcher
from apollo.settings import TICKER


def test__dispatch_signals__for_raising_error_if_dispatched_position_exists() -> None:
    """Test dispatch_signals for raising error if dispatched position already exists."""

    signal_dispatcher = SignalDispatcher()

    signal_dispatcher._configuration = Mock()  # noqa: SLF001
    signal_dispatcher._database_connector = Mock()  # noqa: SLF001
    signal_dispatcher._price_data_provider = Mock()  # noqa: SLF001
    signal_dispatcher._price_data_enhancer = Mock()  # noqa: SLF001

    signal_dispatcher._database_connector.get_existing_position_by_status.return_value = Position(  # noqa: SLF001, E501
        id="test",
        ticker=str(TICKER),
        status=PositionStatus.DISPATCHED,
    )

    exception_message = (
        "Dispatched position for "
        f"{TICKER} already exists. "
        "System invariant violated, position was not opened or cancelled."
    )

    with pytest.raises(
        DispatchedPositionAlreadyExistsError,
        match=exception_message,
    ) as exception:
        signal_dispatcher.dispatch_signals()

    assert str(exception.value) == exception_message
