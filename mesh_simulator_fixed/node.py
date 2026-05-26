"""
Mesh network node simulation.
Each node represents a physical device in the Wirepas-like mesh network.
"""

import time
import logging
from enum import Enum
from typing import Optional
from .message import MeshMessage, MessageType

logger = logging.getLogger(__name__)


class NodeState(Enum):
    OFFLINE = "offline"
    BOOTING = "booting"
    ONLINE = "online"
    LOW_BATTERY = "low_battery"
    ERROR = "error"


class MeshNode:
    """Simulates a single mesh network node (e.g., a sensor or actuator)."""

    MAX_PAYLOAD_SIZE = 102  # Maximum payload in bytes for a single message
    BATTERY_DRAIN_PER_TX = 0.1  # Battery % drained per transmission
    BATTERY_DRAIN_PER_RX = 0.05  # Battery % drained per reception
    LOW_BATTERY_THRESHOLD = 20.0

    def __init__(self, node_id: int, firmware_version: str = "1.0.0"):
        self.node_id = node_id
        self.firmware_version = firmware_version
        self.state = NodeState.OFFLINE
        self.battery_level: float = 100.0
        self.neighbors: list[int] = []
        self.message_queue: list[MeshMessage] = []
        self.received_messages: list[MeshMessage] = []
        self.transmitted_count: int = 0
        self.received_count: int = 0
        self.error_log: list[str] = []
        self._boot_time: Optional[float] = None

    def boot(self) -> bool:
        """Boot the node. Returns True if successful."""
        if self.state == NodeState.ONLINE:
            logger.warning(f"Node {self.node_id} is already online")
            return True

        self.state = NodeState.BOOTING
        self._boot_time = time.time()

        if self.battery_level > 0:
            self.state = NodeState.ONLINE
            logger.info(f"Node {self.node_id} booted successfully (fw: {self.firmware_version})")
            return True
        else:
            self.state = NodeState.ERROR  # Fix #2: dead nodes go to ERROR, not ONLINE
            logger.error(f"Node {self.node_id} failed to boot: no battery")
            return False

    def shutdown(self):
        """Shut down the node."""
        self.state = NodeState.OFFLINE
        self._boot_time = None
        logger.info(f"Node {self.node_id} shut down")

    def get_uptime(self) -> float:
        """Return uptime in seconds. Returns -1 if node is not online."""
        if self._boot_time is None or self.state != NodeState.ONLINE:
            return -1
        return time.time() - self._boot_time

    def add_neighbor(self, neighbor_id: int):
        """Register a neighboring node."""
        self.neighbors.append(neighbor_id)

    def remove_neighbor(self, neighbor_id: int):
        """Remove a neighboring node."""
        if neighbor_id in self.neighbors:
            self.neighbors.remove(neighbor_id)

    def send_message(self, message: MeshMessage) -> bool:
        """
        Send a message from this node.
        Returns True if the message was queued successfully.
        """
        if self.state not in (NodeState.ONLINE, NodeState.LOW_BATTERY):  # Fix #9: LOW_BATTERY can send
            self.error_log.append(f"Cannot send: node is {self.state.value}")
            return False

        if len(message.payload) > self.MAX_PAYLOAD_SIZE:
            self.error_log.append(
                f"Payload too large: {len(message.payload)} > {self.MAX_PAYLOAD_SIZE}"
            )
            return False

        # Drain battery for transmission
        self.battery_level -= self.BATTERY_DRAIN_PER_TX
        if self.battery_level < self.LOW_BATTERY_THRESHOLD:
            self.state = NodeState.LOW_BATTERY

        self.message_queue.append(message)
        self.transmitted_count += 1
        logger.info(
            f"Node {self.node_id} queued message {message.message_id} "
            f"to node {message.destination_id}"
        )
        return True

    def receive_message(self, message: MeshMessage) -> bool:
        """
        Receive and process an incoming message.
        Returns True if the message was accepted.
        """
        if self.state not in (NodeState.ONLINE, NodeState.LOW_BATTERY):
            self.error_log.append(f"Cannot receive: node is {self.state.value}")
            return False

        if message.is_expired():
            self.error_log.append(f"Message {message.message_id} expired (hops: {message.hop_count})")
            return False

        # Drain battery for reception
        self.battery_level -= self.BATTERY_DRAIN_PER_RX

        self.received_messages.append(message)
        self.received_count += 1

        if message.destination_id != self.node_id:
            # This is a relay — forward to next hop
            self.message_queue.append(message)
            self.transmitted_count += 1

        logger.info(
            f"Node {self.node_id} received message {message.message_id} "
            f"from node {message.source_id}"
        )
        return True

    def get_diagnostics(self) -> dict:
        """Return node diagnostic information."""
        return {
            "node_id": self.node_id,
            "state": self.state.value,
            "firmware_version": self.firmware_version,
            "battery_level": self.battery_level,
            "neighbors": self.neighbors,
            "transmitted": self.transmitted_count,
            "received": self.received_count,
            "uptime": self.get_uptime(),
            "errors": self.error_log,
            "queue_depth": len(self.message_queue),  # Fix #4: report message_queue, not received_messages
        }

    def flash_firmware(self, new_version: str, firmware_data: bytes) -> bool:
        """
        Flash new firmware to the node.
        Node must be online and will reboot after flashing.
        """
        if self.state not in (NodeState.ONLINE, NodeState.LOW_BATTERY):
            self.error_log.append("Cannot flash: node not online")
            return False

        if self.battery_level < 30.0:
            self.error_log.append("Cannot flash: battery too low (need >30%)")
            return False

        logger.info(f"Node {self.node_id} flashing firmware {self.firmware_version} -> {new_version}")
        self.shutdown()
        self.firmware_version = new_version
        self.boot()  # Fix #3: reboot the node after flashing so it comes back online
        return True
