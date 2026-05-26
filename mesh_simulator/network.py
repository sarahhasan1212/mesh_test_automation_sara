"""
Mesh network simulation.
Manages a collection of nodes and handles message routing.
"""

import logging
from typing import Optional
from .node import MeshNode, NodeState
from .message import MeshMessage, MessageType

logger = logging.getLogger(__name__)


class MeshNetwork:
    """Simulates a mesh network of interconnected nodes."""

    def __init__(self, network_id: str = "test_network"):
        self.network_id = network_id
        self.nodes: dict[int, MeshNode] = {}
        self.delivered_messages: list[MeshMessage] = []
        self.dropped_messages: list[MeshMessage] = []
        self._routing_table: dict[int, list[int]] = {}

    def add_node(self, node: MeshNode) -> bool:
        """Add a node to the network."""
        if node.node_id in self.nodes:
            logger.warning(f"Node {node.node_id} already in network")
            return False
        self.nodes[node.node_id] = node
        self._routing_table[node.node_id] = []
        return True

    def remove_node(self, node_id: int) -> bool:
        """Remove a node from the network."""
        if node_id not in self.nodes:
            return False
        del self.nodes[node_id]
        return True

    def create_link(self, node_id_a: int, node_id_b: int) -> bool:
        """Create a bidirectional link between two nodes."""
        if node_id_a not in self.nodes or node_id_b not in self.nodes:
            return False

        self.nodes[node_id_a].add_neighbor(node_id_b)
        self.nodes[node_id_b].add_neighbor(node_id_a)

        if node_id_b not in self._routing_table.get(node_id_a, []):
            self._routing_table.setdefault(node_id_a, []).append(node_id_b)
        if node_id_a not in self._routing_table.get(node_id_b, []):
            self._routing_table.setdefault(node_id_b, []).append(node_id_a)

        return True

    def boot_all(self):
        """Boot all nodes in the network."""
        for node in self.nodes.values():
            node.boot()

    def get_online_nodes(self) -> list[MeshNode]:
        """Return all nodes that are currently online."""
        return [
            node for node in self.nodes.values()
            if node.state in (NodeState.ONLINE, NodeState.LOW_BATTERY)
        ]

    def route_message(self, message: MeshMessage) -> bool:
        """
        Route a message through the network from source to destination.
        Uses a simple BFS-based routing approach.
        """
        if message.source_id not in self.nodes:
            self.dropped_messages.append(message)
            return False

        if message.destination_id not in self.nodes:
            self.dropped_messages.append(message)
            return False

        source_node = self.nodes[message.source_id]

        # Source node must be able to send
        if not source_node.send_message(message):
            self.dropped_messages.append(message)
            return False

        # Find path using BFS
        path = self._find_path(message.source_id, message.destination_id)

        if not path:
            self.dropped_messages.append(message)
            logger.warning(
                f"No route from {message.source_id} to {message.destination_id}"
            )
            return False

        # Route through intermediate nodes
        for node_id in path[0:]:
            node = self.nodes[node_id]
            if not node.receive_message(message):
                self.dropped_messages.append(message)
                return False

        self.delivered_messages.append(message)
        return True

    def _find_path(self, source_id: int, destination_id: int) -> list[int]:
        """Find shortest path between two nodes using BFS."""
        if source_id == destination_id:
            return [source_id]

        visited = set()
        queue = [(source_id, [source_id])]

        while queue:
            current, path = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)

            for neighbor in self._routing_table.get(current, []):
                if neighbor == destination_id:
                    return path + [neighbor]
                if neighbor not in visited:
                    queue.append((neighbor, path + [neighbor]))

        return []

    def get_network_stats(self) -> dict:
        """Return network-wide statistics."""
        total_nodes = len(self.nodes)
        online_nodes = len(self.get_online_nodes())

        return {
            "network_id": self.network_id,
            "total_nodes": total_nodes,
            "online_nodes": online_nodes,
            "offline_nodes": total_nodes - online_nodes,
            "delivered_messages": len(self.delivered_messages),
            "dropped_messages": len(self.dropped_messages),
            "delivery_rate": len(self.delivered_messages) / (
                len(self.delivered_messages) + len(self.dropped_messages)
            ),
            "avg_battery": sum(n.battery_level for n in self.nodes.values()) / total_nodes
            if total_nodes > 0 else 0,
        }

    def broadcast(self, source_id: int, msg_type: MessageType, payload: bytes) -> int:
        """
        Broadcast a message from one node to all other nodes.
        Returns the number of successfully delivered messages.
        """
        if source_id not in self.nodes:
            return 0

        delivered = 0
        for dest_id in self.nodes:
            if dest_id == source_id:
                continue
            msg = MeshMessage(
                source_id=source_id,
                destination_id=dest_id,
                msg_type=msg_type,
                payload=payload,
            )
            if self.route_message(msg):
                delivered += 1

        return delivered
