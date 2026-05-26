import pytest

from mesh_simulator import MeshNode, MeshNetwork, MeshMessage, MessageType
from helpers import load_cases


_ALL_ROUTING_CASES = load_cases("routing_cases.json")
_NORMAL_CASES = [c for c in _ALL_ROUTING_CASES if not c.get("is_bug")]
_BUG_CASES = [c for c in _ALL_ROUTING_CASES if c.get("is_bug")]


@pytest.mark.regression
@pytest.mark.parametrize(
    "case",
    _NORMAL_CASES,
    ids=[c["id"] for c in _NORMAL_CASES]
)
def test_message_routing(case):
    """
    WHAT IS BEING TESTED: Message routing across network topologies
    EXPECTED BEHAVIOUR: Messages delivered when path exists
        dropped when destination unknown or no path exists
    DATA SOURCE: tests/test_data/routing_cases.json
    """
    # Arrange
    network = MeshNetwork(network_id="test")
    for node_id in case["nodes"]:
        network.add_node(MeshNode(node_id=node_id))
    for link in case["links"]:
        network.create_link(link[0], link[1])
    network.boot_all()

    msg = MeshMessage(
        source_id=case["source_id"],
        destination_id=case["destination_id"],
        msg_type=MessageType.DATA,
        payload=b"hello"
    )

    # Act
    result = network.route_message(msg)

    # Assert
    assert bool(result) == case["expected_result"], \
        f"[{case['id']}] {case['description']}\n" \
        f"Expected result: {case['expected_result']}\n" \
        f"Actual result:   {bool(result)}"


@pytest.mark.bug
@pytest.mark.parametrize(
    "case",
    _BUG_CASES,
    ids=[c["id"] for c in _BUG_CASES]
)
def test_message_routing_bug(case):
    """
    WHAT IS BEING TESTED: Source node receiving its own message
    EXPECTED BEHAVIOUR: Source node received_count should be 0
        after routing — it sent the message, not received it!
    ACTUAL BEHAVIOUR (bug): Source node receives its own message
        because route_message() iterates path[0:] instead of path[1:]
    BUG: Bug #7 - network.py route_message()
    DATA SOURCE: tests/test_data/routing_cases.json
    """
    # Arrange
    network = MeshNetwork(network_id="test")
    for node_id in case["nodes"]:
        network.add_node(MeshNode(node_id=node_id))
    for link in case["links"]:
        network.create_link(link[0], link[1])
    network.boot_all()

    msg = MeshMessage(
        source_id=case["source_id"],
        destination_id=case["destination_id"],
        msg_type=MessageType.DATA,
        payload=b"hello"
    )

    # Act
    network.route_message(msg)

    # Assert source did not receive its own message
    source_node = network.nodes[case["source_id"]]
    assert source_node.received_count == 0, \
        f"[{case['id']}] {case['description']}\n" \
        f"Expected source received_count: 0\n" \
        f"Actual source received_count:   {source_node.received_count}" \
        f" — source received its own message!"