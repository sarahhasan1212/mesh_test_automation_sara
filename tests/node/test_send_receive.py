import pytest

from mesh_simulator import MeshNode, MeshMessage, MessageType
from mesh_simulator.node import NodeState
from helpers import load_cases


_ALL_CASES = load_cases("send_receive_cases.json")
_NORMAL_CASES = [c for c in _ALL_CASES if not c.get("is_bug")]
_BUG_CASES = [c for c in _ALL_CASES if c.get("is_bug")]


@pytest.mark.regression
@pytest.mark.parametrize(
    "case",
    _NORMAL_CASES,
    ids=[c["id"] for c in _NORMAL_CASES]
)
def test_node_send_receive_behaviour(case):
    """
    WHAT IS BEING TESTED: Node send/receive capability and counter tracking
    EXPECTED BEHAVIOUR: OFFLINE nodes reject all messages
        ONLINE nodes accept and track counters correctly
    DATA SOURCE: tests/test_data/send_receive_cases.json
    """
    # Arrange
    node = MeshNode(node_id=1)
    if case["node_booted"]:
        node.boot()

    if case["battery_level"] is not None:
        node.battery_level = case["battery_level"]
    if case["node_state"] == "low_battery":
        node.state = NodeState.LOW_BATTERY
    elif case["node_state"] == "offline":
        node.state = NodeState.OFFLINE

    if case["action"] == "send":
        msg = MeshMessage(
            source_id=1,
            destination_id=2,
            msg_type=MessageType.DATA,
            payload=b"hello"
        )
        result = node.send_message(msg)
    else:
        msg = MeshMessage(
            source_id=2,
            destination_id=1,
            msg_type=MessageType.DATA,
            payload=b"hello"
        )
        result = node.receive_message(msg)

    # Assert result
    assert bool(result) == case["expected_result"], \
        f"[{case['id']}] {case['description']}\n" \
        f"Expected result: {case['expected_result']}\n" \
        f"Actual result:   {bool(result)}"

    # Assert counters
    if case["expected_tx"] is not None:
        assert node.transmitted_count == case["expected_tx"], \
            f"[{case['id']}] {case['description']}\n" \
            f"Expected TX: {case['expected_tx']}\n" \
            f"Actual TX:   {node.transmitted_count}"

    if case["expected_rx"] is not None:
        assert node.received_count == case["expected_rx"], \
            f"[{case['id']}] {case['description']}\n" \
            f"Expected RX: {case['expected_rx']}\n" \
            f"Actual RX:   {node.received_count}"


@pytest.mark.bug
@pytest.mark.parametrize(
    "case",
    _BUG_CASES,
    ids=[c["id"] for c in _BUG_CASES]
)
def test_node_send_receive_behaviour_bug(case):
    """
    WHAT IS BEING TESTED: LOW_BATTERY node send capability
    EXPECTED BEHAVIOUR: LOW_BATTERY node SHOULD be able to send
        assignment spec says ONLINE and LOW_BATTERY can both send
    ACTUAL BEHAVIOUR (bug): send_message() rejects LOW_BATTERY nodes
        only checks for ONLINE state — LOW_BATTERY incorrectly blocked!
    BUG: Bug #10 - node.py send_message()
    DATA SOURCE: tests/test_data/send_receive_cases.json
    """
    # Arrange
    node = MeshNode(node_id=1)
    node.boot()
    node.battery_level = case["battery_level"]
    node.state = NodeState.LOW_BATTERY

    msg = MeshMessage(
        source_id=1,
        destination_id=2,
        msg_type=MessageType.DATA,
        payload=b"hello"
    )

    # Act
    result = node.send_message(msg)

    # Assert
    assert bool(result) == case["expected_result"], \
        f"[{case['id']}] {case['description']}\n" \
        f"Expected result: {case['expected_result']}\n" \
        f"Actual result:   {bool(result)}" \
        f" — LOW_BATTERY nodes should be able to send!"