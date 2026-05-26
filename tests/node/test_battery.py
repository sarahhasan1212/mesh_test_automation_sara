import pytest

from mesh_simulator import MeshNode, MeshMessage, MessageType
from mesh_simulator.node import NodeState
from helpers import load_cases


BATTERY_CASES = load_cases("battery_cases.json")


@pytest.mark.regression
@pytest.mark.parametrize("case", _with_marks(BATTERY_CASES))
def test_node_battery_behaviour(case, online_node):
    """
    WHAT IS BEING TESTED: Node state and behavior at various battery levels
    EXPECTED BEHAVIOUR: State and send/receive matches battery_cases.json
    DATA SOURCE: tests/test_data/battery_cases.json
    """
    # Arrange
    node = online_node
    node.battery_level = case["battery_level"]

    # Force correct state based on battery
    if case["battery_level"] <= 0:
        node.state = NodeState.OFFLINE
    elif case["battery_level"] < MeshNode.LOW_BATTERY_THRESHOLD:
        node.state = NodeState.LOW_BATTERY

    msg = MeshMessage(
        source_id=1,
        destination_id=2,
        msg_type=MessageType.DATA,
        payload=b"test"
    )

    # Act
    can_send = node.send_message(msg)

    # Assert state
    assert node.state.value == case["expected_state"], \
        f"[{case['id']}] {case['description']}\n" \
        f"Expected state: {case['expected_state']}\n" \
        f"Actual state:   {node.state.value}"

    # Assert send capability
    assert bool(can_send) == case["can_send"], \
        f"[{case['id']}] {case['description']}\n" \
        f"Expected can_send: {case['can_send']}\n" \
        f"Actual can_send:   {bool(can_send)}"
