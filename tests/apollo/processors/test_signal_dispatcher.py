from unittest import mock
from unittest.mock import Mock

import pytest

from apollo.errors.system_invariants import (
    DispatchedPositionAlreadyExistsError,
    NeitherOpenNorOptimizedPositionExistsError,
)
from apollo.models.position import Position, PositionStatus
from apollo.processors.signal_dispatcher import SignalDispatcher
from apollo.settings import TICKER


def mock_get_existing_position_by_status(
    position_status: PositionStatus,
) -> Position | None:
    """
    Conditional mock for get_existing_position_by_status.

    :param position_status: Position status to mock.
    :returns: Position if status is OPEN or OPTIMIZED, None otherwise.
    """

    if position_status in [PositionStatus.OPEN, PositionStatus.OPTIMIZED]:
        return Position(
            id="test",
            ticker=str(TICKER),
            status=position_status,
        )

    return None


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


def test__dispatch_signals__for_raising_error_if_open_and_optimized_positions_do_not_exist() -> (  # noqa: E501
    None
):
    """Test dispatch_signals for raising error if open and optimized positions do not exist."""  # noqa: E501

    signal_dispatcher = SignalDispatcher()

    signal_dispatcher._configuration = Mock()  # noqa: SLF001
    signal_dispatcher._database_connector = Mock()  # noqa: SLF001
    signal_dispatcher._price_data_provider = Mock()  # noqa: SLF001
    signal_dispatcher._price_data_enhancer = Mock()  # noqa: SLF001

    signal_dispatcher._database_connector.get_existing_position_by_status.return_value = None  # noqa: E501, SLF001

    exception_message = (
        "Neither open nor optimized position exists. "
        "System invariant violated, position was not opened or optimized."
    )

    with pytest.raises(
        NeitherOpenNorOptimizedPositionExistsError,
        match=exception_message,
    ) as exception:
        signal_dispatcher.dispatch_signals()

    assert str(exception.value) == exception_message


def test__dispatch_signals__for_calling_signal_generation_method() -> None:
    """Test dispatch_signals for calling signal generation method."""

    signal_dispatcher = SignalDispatcher()

    signal_dispatcher._configuration = Mock()  # noqa: SLF001
    signal_dispatcher._database_connector = Mock()  # noqa: SLF001
    signal_dispatcher._price_data_provider = Mock()  # noqa: SLF001
    signal_dispatcher._price_data_enhancer = Mock()  # noqa: SLF001

    signal_dispatcher._database_connector.get_existing_position_by_status.side_effect = mock_get_existing_position_by_status  # noqa: E501, SLF001

    signal_dispatcher._generate_signal_and_brackets = Mock()  # noqa: SLF001

    signal_dispatcher.dispatch_signals()

    signal_dispatcher._generate_signal_and_brackets.assert_has_calls(  # noqa: SLF001
        [
            mock.call(
                Position(
                    id="test",
                    ticker=str(TICKER),
                    status=PositionStatus.OPEN,
                ),
            ),
            mock.call(
                Position(
                    id="test",
                    ticker=str(TICKER),
                    status=PositionStatus.OPTIMIZED,
                ),
            ),
        ],
    )
