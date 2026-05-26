import pytest

from mesh_simulator import MeshMessage, MessageType


@pytest.mark.regression
@pytest.mark.positive
def test_diagnostics_shows_correct_firmware_version(online_node):
    """
    WHAT IS BEING TESTED: firmware_version field in diagnostics
    EXPECTED BEHAVIOUR: Should show the exact firmware version
        the node was created with — 1.0.0
    """
    # Arrange — online_node fixture provides booted node with fw 1.0.0

    # Act
    diag = online_node.get_diagnostics()

    # Assert
    assert diag["firmware_version"] == "1.0.0", \
        f"Expected firmware 1.0.0 but got {diag['firmware_version']}"


@pytest.mark.regression
@pytest.mark.positive
def test_diagnostics_shows_correct_tx_rx_counts(online_node):
    """
    WHAT IS BEING TESTED: transmitted and received counts in diagnostics
    EXPECTED BEHAVIOUR: transmitted shows messages sent (3)
        received shows messages received (2) — independently tracked
    """
    # Arrange — send 3 messages
    for _ in range(3):
        msg = MeshMessage(
            source_id=1,
            destination_id=2,
            msg_type=MessageType.DATA,
            payload=b"hello"
        )
        online_node.send_message(msg)

    # Arrange — receive 2 messages
    for _ in range(2):
        msg = MeshMessage(
            source_id=2,
            destination_id=1,
            msg_type=MessageType.DATA,
            payload=b"hello"
        )
        online_node.receive_message(msg)

    # Act
    diag = online_node.get_diagnostics()

    # Assert
    assert diag["transmitted"] == 3, \
        f"Expected TX 3 but got {diag['transmitted']}"
    assert diag["received"] == 2, \
        f"Expected RX 2 but got {diag['received']}"


@pytest.mark.bug
@pytest.mark.negative
def test_diagnostics_queue_depth_shows_message_queue_not_received(online_node):
    """
    WHAT IS BEING TESTED: queue_depth field in diagnostics
    EXPECTED BEHAVIOUR: queue_depth should show number of messages
        waiting in message_queue to be sent — NOT received_messages count
    ACTUAL BEHAVIOUR (bug): queue_depth returns len(received_messages)
        instead of len(message_queue) — completely wrong metric!
    BUG: Bug #4 - node.py get_diagnostics()
    """
    # Arrange — send 2 messages → adds to message_queue
    for _ in range(2):
        msg = MeshMessage(
            source_id=1,
            destination_id=2,
            msg_type=MessageType.DATA,
            payload=b"hello"
        )
        online_node.send_message(msg)

    # Arrange — receive 5 messages → adds to received_messages
    for _ in range(5):
        msg = MeshMessage(
            source_id=2,
            destination_id=1,
            msg_type=MessageType.DATA,
            payload=b"hello"
        )
        online_node.receive_message(msg)

    # Act
    diag = online_node.get_diagnostics()

    # Assert
    assert diag["queue_depth"] == 2, \
        f"Expected queue_depth 2 (message_queue) " \
        f"but got {diag['queue_depth']} (received_messages!)"