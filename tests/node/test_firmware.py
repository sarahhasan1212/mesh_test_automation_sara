import pytest
from helpers import load_cases

from mesh_simulator.node import NodeState


_ALL_FIRMWARE_CASES = load_cases("firmware_cases.json")
_NORMAL_CASES = [c for c in _ALL_FIRMWARE_CASES if not c.get("is_bug")]
_BUG_CASES = [c for c in _ALL_FIRMWARE_CASES if c.get("is_bug")]


@pytest.mark.regression
@pytest.mark.parametrize(
    "case",
    _NORMAL_CASES,
    ids=[c["id"] for c in _NORMAL_CASES]
)
def test_firmware_flash_behaviour(case, offline_node):
    """
    WHAT IS BEING TESTED: Firmware flash acceptance and version update
    EXPECTED BEHAVIOUR: Flash succeeds only when ONLINE and battery >= 30%
        Flash rejected when battery too low or node offline
    DATA SOURCE: tests/test_data/firmware_cases.json
    """
    # Arrange
    node = offline_node
    if case["node_booted"]:
        node.boot()
    node.battery_level = case["battery_level"]

    # Act
    result = node.flash_firmware(case["new_version"], b"new_firmware")

    # Assert result
    if case["expected_result"] is not None:
        assert bool(result) == case["expected_result"], \
            f"[{case['id']}] {case['description']}\n" \
            f"Expected flash result: {case['expected_result']}\n" \
            f"Actual flash result:   {bool(result)}"

    # Assert state
    if case["expected_state"] is not None:
        assert node.state.value == case["expected_state"], \
            f"[{case['id']}] {case['description']}\n" \
            f"Expected state: {case['expected_state']}\n" \
            f"Actual state:   {node.state.value}"

    # Assert version
    assert node.firmware_version == case["expected_version"], \
        f"[{case['id']}] {case['description']}\n" \
        f"Expected version: {case['expected_version']}\n" \
        f"Actual version:   {node.firmware_version}"


@pytest.mark.bug
@pytest.mark.parametrize(
    "case",
    _BUG_CASES,
    ids=[c["id"] for c in _BUG_CASES]
)
def test_firmware_flash_behaviour_bug(case, offline_node):
    """
    WHAT IS BEING TESTED: Node state after successful firmware flash
    EXPECTED BEHAVIOUR: Node should reboot automatically to ONLINE
        after successful flash with good battery
    ACTUAL BEHAVIOUR (bug): Node stays OFFLINE after flash
        — flash_firmware() never calls boot() after shutdown!
    BUG: Bug #3 - node.py flash_firmware()
    DATA SOURCE: tests/test_data/firmware_cases.json
    """
    # Arrange
    node = offline_node
    node.boot()
    node.battery_level = case["battery_level"]

    # Act
    node.flash_firmware(case["new_version"], b"new_firmware")

    # Assert node rebooted to ONLINE
    assert node.state.value == case["expected_state"], \
        f"[{case['id']}] {case['description']}\n" \
        f"Expected state: {case['expected_state']}\n" \
        f"Actual state:   {node.state.value}" \
        f" — node never rebooted after flash!"

    # Assert version updated
    assert node.firmware_version == case["expected_version"], \
        f"[{case['id']}] {case['description']}\n" \
        f"Expected version: {case['expected_version']}\n" \
        f"Actual version:   {node.firmware_version}"