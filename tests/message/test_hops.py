import pytest

from mesh_simulator import MeshMessage, MessageType
from helpers import load_cases


# Split cases — normal ones and bug ones separately
_ALL_HOP_CASES = load_cases("hop_cases.json")
_NORMAL_CASES = [c for c in _ALL_HOP_CASES if not c.get("is_bug")]
_BUG_CASES = [c for c in _ALL_HOP_CASES if c.get("is_bug")]


@pytest.mark.regression
@pytest.mark.parametrize(
    "case",
    _NORMAL_CASES,
    ids=[c["id"] for c in _NORMAL_CASES]
)
def test_hop_count_and_expiry(case):
    """
    WHAT IS BEING TESTED: increment_hop() and is_expired() behaviour
    EXPECTED BEHAVIOUR: hop_count increments correctly
        is_expired() returns correct result based on hop count
    DATA SOURCE: tests/test_data/hop_cases.json
    """
    # Arrange
    msg = MeshMessage(
        source_id=1,
        destination_id=2,
        msg_type=MessageType.DATA,
        payload=b"hello",
        hop_count=case["hop_count"],
        max_hops=case["max_hops"]
    )

    if case["action"] == "increment":
        # Act
        msg.increment_hop()
        # Assert
        assert msg.hop_count == case["expected_hop_count"], \
            f"[{case['id']}] {case['description']}\n" \
            f"Expected hop_count: {case['expected_hop_count']}\n" \
            f"Actual hop_count:   {msg.hop_count}"

    elif case["action"] == "check_expired":
        # Act
        result = msg.is_expired()
        # Assert
        assert result == case["expected_expired"], \
            f"[{case['id']}] {case['description']}\n" \
            f"Expected is_expired: {case['expected_expired']}\n" \
            f"Actual is_expired:   {result}"


@pytest.mark.bug
@pytest.mark.parametrize(
    "case",
    _BUG_CASES,
    ids=[c["id"] for c in _BUG_CASES]
)
def test_hop_count_and_expiry_bug(case):
    """
    WHAT IS BEING TESTED: is_expired() off-by-one bug
    EXPECTED BEHAVIOUR: Message at exactly max_hops should be expired
    ACTUAL BEHAVIOUR (bug): Returns False because uses > instead of >=
    BUG: Bug #6 - message.py is_expired()
    DATA SOURCE: tests/test_data/hop_cases.json
    """
    # Arrange
    msg = MeshMessage(
        source_id=1,
        destination_id=2,
        msg_type=MessageType.DATA,
        payload=b"hello",
        hop_count=case["hop_count"],
        max_hops=case["max_hops"]
    )

    # Act
    result = msg.is_expired()

    # Assert
    assert result == case["expected_expired"], \
        f"[{case['id']}] {case['description']}\n" \
        f"Expected is_expired: {case['expected_expired']}\n" \
        f"Actual is_expired:   {result}"