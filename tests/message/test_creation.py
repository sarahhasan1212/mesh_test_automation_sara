import pytest

from mesh_simulator import MeshMessage, MessageType


@pytest.mark.regression
@pytest.mark.positive
def test_message_id_auto_generated_when_not_provided():
    """
    WHAT IS BEING TESTED: Auto generation of message_id
    EXPECTED BEHAVIOUR: message_id should not be empty
        when no ID is provided — system generates one automatically
    """
    # Arrange & Act — creation is both arrange and act here
    msg = MeshMessage(
        source_id=1,
        destination_id=2,
        msg_type=MessageType.DATA,
        payload=b"hello"
    )

    # Assert
    assert msg.message_id != "", \
        f"Expected auto generated message_id but got empty string"
    assert msg.message_id is not None, \
        f"Expected auto generated message_id but got None"


@pytest.mark.regression
@pytest.mark.positive
def test_message_custom_id_is_preserved():
    """
    WHAT IS BEING TESTED: Custom message_id preservation
    EXPECTED BEHAVIOUR: When a custom ID is provided it should
        not be overwritten by auto generation
    """
    # Arrange & Act — creation is both arrange and act here
    msg = MeshMessage(
        source_id=1,
        destination_id=2,
        msg_type=MessageType.DATA,
        payload=b"hello",
        message_id="my-message-123"
    )

    # Assert
    assert msg.message_id == "my-message-123", \
        f"Expected my-message-123 but got {msg.message_id}"