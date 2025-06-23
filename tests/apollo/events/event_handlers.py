from unittest.mock import Mock, patch

from apollo.events.event_handlers import handle_signal_generated_event
from apollo.models.signal_notification import SignalNotification


# NOTE: this a single event test for which we
# do not need to create a full fixture of order manager
@patch("apollo.events.event_handlers.OrderManager")
def test__handle_signal_generated_event__for_handling_dispatched_position(
    mock_order_manager: Mock,
) -> None:
    """Test handling of dispatched position in signal generated event."""

    mock_order_manager = mock_order_manager.return_value

    # Call the event handler
    # with a Signal Notification
    handle_signal_generated_event(
        SignalNotification(
            open_position=False,
            dispatched_position=True,
        ),
    )

    # Assert that the dispatched position is handled
    mock_order_manager.handle_dispatched_position.assert_called_once()


@patch("apollo.events.event_handlers.OrderManager")
def test__handle_signal_generated_event__for_handling_open_position(
    mock_order_manager: Mock,
) -> None:
    """Test handling of open position in signal generated event."""

    mock_order_manager = mock_order_manager.return_value

    # Call the event handler
    # with a Signal Notification
    handle_signal_generated_event(
        SignalNotification(
            open_position=True,
            dispatched_position=False,
        ),
    )

    mock_order_manager.return_value.handle_dispatched_position.assert_not_called()


@patch("apollo.events.event_handlers.OrderManager")
def test__handle_signal_generated_event__for_handling_open_and_dispatched_positions(
    mock_order_manager: Mock,
) -> None:
    """Test handling of open and dispatched positions in signal generated event."""

    mock_order_manager = mock_order_manager.return_value

    # Call the event handler
    # with a Signal Notification
    handle_signal_generated_event(
        SignalNotification(
            open_position=True,
            dispatched_position=True,
        ),
    )

    mock_order_manager.return_value.handle_dispatched_position.assert_not_called()
