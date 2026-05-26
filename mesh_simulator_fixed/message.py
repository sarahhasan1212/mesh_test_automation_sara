"""
Mesh network message definitions.
Messages are routed between nodes in the simulated mesh network.
"""

from enum import Enum
from dataclasses import dataclass, field
import time


class MessageType(Enum):
    DATA = "data"
    DIAGNOSTIC = "diagnostic"
    ROUTE_UPDATE = "route_update"
    FIRMWARE_UPDATE = "firmware_update"
    HEARTBEAT = "heartbeat"


@dataclass
class MeshMessage:
    source_id: int
    destination_id: int
    msg_type: MessageType
    payload: bytes
    hop_count: int = 0
    max_hops: int = 10
    timestamp: float = field(default_factory=time.time)
    message_id: str = ""

    def __post_init__(self):
        if not self.message_id:
            self.message_id = f"{self.source_id}-{self.destination_id}-{self.timestamp}"

    def increment_hop(self):
        """Increment hop count when message passes through a relay node."""
        self.hop_count += 1

    def is_expired(self) -> bool:
        """Check if message has exceeded maximum hop count."""
        return self.hop_count >= self.max_hops  # Fix #5: >= so max_hops itself is the limit

    def payload_size(self) -> int:
        """Return payload size in bytes."""
        return len(self.payload)  # Fix #1: measure bytes directly, not str(bytes)
