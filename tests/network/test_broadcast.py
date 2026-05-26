import pytest

from mesh_simulator import MeshNode, MeshNetwork, MessageType


@pytest.mark.smoke
@pytest.mark.regression
@pytest.mark.positive
def test_broadcast_delivers_to_all_other_nodes():
    """
    WHAT IS BEING TESTED: Broadcast from one node to all others
    EXPECTED BEHAVIOUR: Message delivered to all nodes except
        the sender — returns count of successful deliveries (2)
    """
    # Arrange
    network = MeshNetwork(network_id="test")
    network.add_node(MeshNode(node_id=1))
    network.add_node(MeshNode(node_id=2))
    network.add_node(MeshNode(node_id=3))
    network.create_link(1, 2)
    network.create_link(1, 3)
    network.boot_all()

    # Act
    delivered = network.broadcast(
        source_id=1,
        msg_type=MessageType.DATA,
        payload=b"hello everyone"
    )

    # Assert
    assert delivered == 2, \
        f"Expected 2 deliveries but got {delivered}"


@pytest.mark.regression
@pytest.mark.negative
def test_broadcast_skips_offline_nodes():
    """
    WHAT IS BEING TESTED: Broadcast when some nodes are offline
    EXPECTED BEHAVIOUR: Only online nodes receive broadcast
        offline nodes skipped — returns 1 not 2
    """
    # Arrange
    network = MeshNetwork(network_id="test")
    network.add_node(MeshNode(node_id=1))
    network.add_node(MeshNode(node_id=2))
    network.add_node(MeshNode(node_id=3))
    network.create_link(1, 2)
    network.create_link(1, 3)
    network.boot_all()
    network.nodes[3].shutdown()  # node 3 goes offline

    # Act
    delivered = network.broadcast(
        source_id=1,
        msg_type=MessageType.DATA,
        payload=b"hello everyone"
    )

    # Assert
    assert delivered == 1, \
        f"Expected 1 delivery (node 3 offline) but got {delivered}"