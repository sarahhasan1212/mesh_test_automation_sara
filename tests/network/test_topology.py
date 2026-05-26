import pytest

from mesh_simulator import MeshNode, MeshNetwork


@pytest.mark.smoke
@pytest.mark.regression
@pytest.mark.positive
def test_add_node_returns_true():
    """
    WHAT IS BEING TESTED: Adding a node to the network
    EXPECTED BEHAVIOUR: add_node() returns True and node
        is registered in the network
    """
    # Arrange
    network = MeshNetwork(network_id="test")
    node = MeshNode(node_id=1)

    # Act
    result = network.add_node(node)

    # Assert
    assert result is True, \
        f"Expected True when adding node but got {result}"
    assert 1 in network.nodes, \
        f"Expected node 1 in network but not found"


@pytest.mark.regression
@pytest.mark.negative
def test_add_duplicate_node_returns_false():
    """
    WHAT IS BEING TESTED: Adding the same node twice
    EXPECTED BEHAVIOUR: Second add_node() returns False
        — duplicate nodes not allowed in network
    """
    # Arrange
    network = MeshNetwork(network_id="test")
    node = MeshNode(node_id=1)
    network.add_node(node)

    # Act
    result = network.add_node(node)

    # Assert
    assert result is False, \
        f"Expected False for duplicate node but got {result}"


@pytest.mark.regression
@pytest.mark.positive
def test_create_link_is_bidirectional():
    """
    WHAT IS BEING TESTED: Bidirectional link between two nodes
    EXPECTED BEHAVIOUR: When link created between Node 1 and Node 2
        BOTH nodes see each other as neighbors automatically
    """
    # Arrange
    network = MeshNetwork(network_id="test")
    network.add_node(MeshNode(node_id=1))
    network.add_node(MeshNode(node_id=2))

    # Act
    network.create_link(1, 2)

    # Assert
    assert 2 in network.nodes[1].neighbors, \
        f"Expected node 2 in node 1 neighbors but got {network.nodes[1].neighbors}"
    assert 1 in network.nodes[2].neighbors, \
        f"Expected node 1 in node 2 neighbors but got {network.nodes[2].neighbors}"


@pytest.mark.bug
@pytest.mark.negative
def test_remove_node_cleans_up_neighbors():
    """
    WHAT IS BEING TESTED: Neighbor cleanup after node removal
    EXPECTED BEHAVIOUR: When Node 2 is removed Node 1 should
        no longer have Node 2 in its neighbors list
    ACTUAL BEHAVIOUR (bug): Node 2 stays in Node 1 neighbor
        list even after removal — ghost node in the network!
    BUG: Bug #8 - network.py remove_node()
    """
    # Arrange
    network = MeshNetwork(network_id="test")
    network.add_node(MeshNode(node_id=1))
    network.add_node(MeshNode(node_id=2))
    network.create_link(1, 2)

    # Act
    network.remove_node(2)

    # Assert
    assert 2 not in network.nodes[1].neighbors, \
        f"Expected node 2 removed from neighbors " \
        f"but still found in {network.nodes[1].neighbors}"
    assert 2 not in network._routing_table, \
        f"Expected node 2 removed from routing table but still found!"