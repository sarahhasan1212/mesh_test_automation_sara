import pytest

from mesh_simulator import MeshMessage, MessageType
from helpers import load_cases


_ALL_CASES = load_cases("payload_cases.json")
_NORMAL_CASES = [c for c in _ALL_CASES if not c.get("is_bug")]
_BUG_CASES = [c for c in _ALL_CASES if c.get("is_bug")]


@pytest.mark.regression
@pytest.mark.parametrize(
    "case",
    _NORMAL_CASES,
    ids=[c["id"] for c in _NORMAL_CASES]
)
def test_payload_size_boundary(case, online_node):
    """
    WHAT IS BEING TESTED: Payload size limits enforcement
    EXPECTED BEHAVIOUR: Payloads within 102 byte limit accepted
        Payloads over limit rejected by send_message()
    DATA SOURCE: tests/test_data/payload_cases.json
    """
    # Arrange
    payload = b"x" * case["payload_size"]
    msg = MeshMessage(
        source_id=1,
        destination_id=2,
        msg_type=MessageType.DATA,
        payload=payload
    )

    # Act
    result = online_node.send_message(msg)

    # Assert
    assert bool(result) == case["should_accept"], \
        f"[{case['id']}] {case['description']}\n" \
        f"Expected should_accept: {case['should_accept']}\n" \
        f"Actual result: {bool(result)}"


@pytest.mark.bug
@pytest.mark.parametrize(
    "case",
    _BUG_CASES,
    ids=[c["id"] for c in _BUG_CASES]
)
def test_payload_size_method_bug(case):
    """
    WHAT IS BEING TESTED: payload_size() byte length accuracy
    EXPECTED BEHAVIOUR: payload_size() returns exact byte count
        5 for b'hello', 11 for b'hello world'
    ACTUAL BEHAVIOUR (bug): Returns inflated size because str()
        wraps bytes in b'...' adding 3 extra characters every time!
    BUG: Bug #1 - message.py payload_size()
    DATA SOURCE: tests/test_data/payload_cases.json
    """
    # Arrange
    raw = case["raw_payload"].encode()
    msg = MeshMessage(
        source_id=1,
        destination_id=2,
        msg_type=MessageType.DATA,
        payload=raw
    )

    # Act
    actual_size = msg.payload_size()

    # Assert
    assert actual_size == case["payload_size"], \
        f"[{case['id']}] {case['description']}\n" \
        f"Expected payload_size: {case['payload_size']}\n" \
        f"Actual payload_size:   {actual_size} — str() wraps bytes incorrectly!"