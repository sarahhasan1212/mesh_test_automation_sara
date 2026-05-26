import pytest
from helpers import load_cases

from mesh_simulator.node import NodeState


_ALL_BOOT_CASES = load_cases("boot_cases.json")
_NORMAL_CASES = [c for c in _ALL_BOOT_CASES if not c.get("is_bug")]
_BUG_CASES = [c for c in _ALL_BOOT_CASES if c.get("is_bug")]


@pytest.mark.regression
@pytest.mark.parametrize(
    "case",
    _NORMAL_CASES,
    ids=[c["id"] for c in _NORMAL_CASES]
)
def test_node_boot_behaviour(case, offline_node):
    """
    WHAT IS BEING TESTED: Node boot, shutdown, and initial state behaviour
    EXPECTED BEHAVIOUR: State and boot() result match boot_cases.json
    DATA SOURCE: tests/test_data/boot_cases.json
    """
    # Arrange
    node = offline_node
    node.battery_level = case["battery_level"]

    if case["action"] == "create_only":
        assert node.state.value == case["expected_state"], \
            f"[{case['id']}] {case['description']}\n" \
            f"Expected state: {case['expected_state']}\n" \
            f"Actual state:   {node.state.value}"

    elif case["action"] == "boot":
        result = node.boot()
        assert bool(result) == case["expected_result"], \
            f"[{case['id']}] {case['description']}\n" \
            f"Expected boot() result: {case['expected_result']}\n" \
            f"Actual boot() result:   {bool(result)}"
        assert node.state.value == case["expected_state"], \
            f"[{case['id']}] {case['description']}\n" \
            f"Expected state: {case['expected_state']}\n" \
            f"Actual state:   {node.state.value}"

    elif case["action"] == "boot_twice":
        node.boot()
        result = node.boot()
        assert bool(result) == case["expected_result"], \
            f"[{case['id']}] {case['description']}\n" \
            f"Expected boot() result: {case['expected_result']}\n" \
            f"Actual boot() result:   {bool(result)}"
        assert node.state.value == case["expected_state"], \
            f"[{case['id']}] {case['description']}\n" \
            f"Expected state: {case['expected_state']}\n" \
            f"Actual state:   {node.state.value}"

    elif case["action"] == "shutdown":
        node.boot()
        node.shutdown()
        assert node.state.value == case["expected_state"], \
            f"[{case['id']}] {case['description']}\n" \
            f"Expected state: {case['expected_state']}\n" \
            f"Actual state:   {node.state.value}"


@pytest.mark.bug
@pytest.mark.parametrize(
    "case",
    _BUG_CASES,
    ids=[c["id"] for c in _BUG_CASES]
)
def test_node_boot_behaviour_bug(case, offline_node):
    """
    WHAT IS BEING TESTED: Node state after failed boot with zero battery
    EXPECTED BEHAVIOUR: boot() returns False AND state becomes ERROR
    ACTUAL BEHAVIOUR (bug): boot() returns False BUT state is ONLINE!
    BUG: Bug #2 - node.py boot()
    DATA SOURCE: tests/test_data/boot_cases.json
    """
    # Arrange
    node = offline_node
    node.battery_level = case["battery_level"]

    # Act
    result = node.boot()

    # Assert
    assert bool(result) == case["expected_result"], \
        f"[{case['id']}] {case['description']}\n" \
        f"Expected boot() result: {case['expected_result']}\n" \
        f"Actual boot() result:   {bool(result)}"
    assert node.state.value == case["expected_state"], \
        f"[{case['id']}] {case['description']}\n" \
        f"Expected state: {case['expected_state']}\n" \
        f"Actual state:   {node.state.value}"