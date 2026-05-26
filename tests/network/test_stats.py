import pytest

from mesh_simulator import MeshNode, MeshNetwork, MeshMessage, MessageType


@pytest.mark.bug
@pytest.mark.negative
def test_network_stats_no_crash_with_zero_messages():
    """
    WHAT IS BEING TESTED: get_network_stats() on idle network
    EXPECTED BEHAVIOUR: Should return delivery_rate of 0.0
        without crashing when no messages have been sent
    ACTUAL BEHAVIOUR (bug): Crashes with ZeroDivisionError
        because delivery_rate divides by 0 when no messages exist
    BUG: Bug #7 - network.py get_network_stats()
    """
    # Arrange
    network = MeshNetwork(network_id="test")
    network.add_node(MeshNode(node_id=1))
    network.add_node(MeshNode(node_id=2))
    network.boot_all()

    # Act & Assert — should not crash!
    try:
        stats = network.get_network_stats()
        assert stats["delivery_rate"] == 0.0, \
            f"Expected delivery_rate 0.0 but got {stats['delivery_rate']}"
    except ZeroDivisionError:
        pytest.fail(
            "Bug: get_network_stats() crashed with ZeroDivisionError "
            "when no messages sent — expected delivery_rate 0.0"
        )


@pytest.mark.regression
@pytest.mark.positive
def test_network_stats_shows_correct_node_counts(simple_network):
    """
    WHAT IS BEING TESTED: total_nodes and online_nodes in stats
    EXPECTED BEHAVIOUR: Should show correct count of total
        and online nodes in the network
    """
    # Arrange — simple_network fixture provides 3 booted nodes
    # Send one message so delivery_rate doesn't crash
    msg = MeshMessage(
        source_id=1,
        destination_id=2,
        msg_type=MessageType.DATA,
        payload=b"hello"
    )
    simple_network.route_message(msg)

    # Act
    stats = simple_network.get_network_stats()

    # Assert
    assert stats["total_nodes"] == 3, \
        f"Expected total_nodes 3 but got {stats['total_nodes']}"
    assert stats["online_nodes"] == 3, \
        f"Expected online_nodes 3 but got {stats['online_nodes']}"