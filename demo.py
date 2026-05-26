#!/usr/bin/env python3
"""
Mesh Network Simulator — Demo Script

Run this to see the simulator in action before you start testing.
It creates a small mesh network, sends messages, and prints diagnostics.

Usage:
    python demo.py
"""

import logging
import sys
import os

# Set up path so imports work when running from scaffold/
sys.path.insert(0, os.path.dirname(__file__))

from mesh_simulator import MeshNode, MeshNetwork, MeshMessage, MessageType
from mesh_simulator.log_parser import LogParser

# Uncomment the next line to see detailed simulator logs:
# logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def separator(title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def demo_basic_network():
    """Create a 5-node mesh and send some messages."""
    separator("1. Setting Up a Mesh Network")

    net = MeshNetwork(network_id="demo_mesh")

    # Create 5 nodes representing IoT sensors
    node_names = {1: "Gateway", 2: "Sensor-A", 3: "Sensor-B", 4: "Relay-1", 5: "Sensor-C"}
    for nid in node_names:
        node = MeshNode(nid, firmware_version="1.2.3")
        net.add_node(node)
        print(f"  Added node {nid} ({node_names[nid]})")

    # Create mesh topology:
    #   1(Gateway) -- 2(Sensor-A) -- 4(Relay-1) -- 5(Sensor-C)
    #       |              |
    #   3(Sensor-B) -------+
    links = [(1, 2), (1, 3), (2, 3), (2, 4), (4, 5)]
    for a, b in links:
        net.create_link(a, b)
        print(f"  Linked {node_names[a]} <-> {node_names[b]}")

    # Boot all nodes
    net.boot_all()
    online = net.get_online_nodes()
    print(f"\n  Booted {len(online)} nodes. All online.")

    return net, node_names


def demo_send_messages(net: MeshNetwork, node_names: dict):
    """Send a few messages through the network."""
    separator("2. Sending Messages")

    # Direct neighbor message
    msg1 = MeshMessage(
        source_id=1, destination_id=2,
        msg_type=MessageType.DATA,
        payload=b"temperature=22.5C"
    )
    result = net.route_message(msg1)
    print(f"  Gateway -> Sensor-A (direct neighbor): {'delivered' if result else 'FAILED'}")

    # Multi-hop message: Gateway(1) -> Relay-1(4) -> Sensor-C(5)
    msg2 = MeshMessage(
        source_id=1, destination_id=5,
        msg_type=MessageType.DATA,
        payload=b"config_update=true"
    )
    result = net.route_message(msg2)
    print(f"  Gateway -> Sensor-C (multi-hop):       {'delivered' if result else 'FAILED'}")

    # Diagnostic request from Sensor-C back to Gateway
    msg3 = MeshMessage(
        source_id=5, destination_id=1,
        msg_type=MessageType.DIAGNOSTIC,
        payload=b'{"battery":85,"rssi":-67}'
    )
    result = net.route_message(msg3)
    print(f"  Sensor-C -> Gateway (diagnostic):      {'delivered' if result else 'FAILED'}")

    return net


def demo_diagnostics(net: MeshNetwork, node_names: dict):
    """Print diagnostics for all nodes."""
    separator("3. Node Diagnostics")

    for nid, name in node_names.items():
        diag = net.nodes[nid].get_diagnostics()
        print(f"  [{name}] (node {nid})")
        print(f"    State:      {diag['state']}")
        print(f"    Battery:    {diag['battery_level']:.1f}%")
        print(f"    Firmware:   {diag['firmware_version']}")
        print(f"    Neighbors:  {diag['neighbors']}")
        print(f"    TX/RX:      {diag['transmitted']}/{diag['received']}")
        print(f"    Queue:      {diag['queue_depth']}")
        if diag['errors']:
            print(f"    Errors:     {diag['errors']}")
        print()


def demo_firmware_update(net: MeshNetwork, node_names: dict):
    """Demonstrate firmware flashing on a node."""
    separator("4. Firmware Update")

    node = net.nodes[3]  # Sensor-B
    print(f"  Flashing {node_names[3]} from fw {node.firmware_version} to 2.0.0...")
    result = node.flash_firmware("2.0.0", b"\x00" * 256)
    print(f"  Flash result: {'success' if result else 'FAILED'}")
    print(f"  Node state after flash: {node.state.value}")
    print(f"  Firmware version: {node.firmware_version}")

    # Try sending a message to the flashed node
    msg = MeshMessage(
        source_id=1, destination_id=3,
        msg_type=MessageType.DATA,
        payload=b"hello_after_flash"
    )
    result = net.route_message(msg)
    print(f"  Sending message to {node_names[3]} after flash: {'delivered' if result else 'FAILED'}")


def demo_network_stats(net: MeshNetwork):
    """Print network-wide statistics."""
    separator("5. Network Statistics")

    try:
        stats = net.get_network_stats()
        for key, value in stats.items():
            if isinstance(value, float):
                print(f"  {key}: {value:.2f}")
            else:
                print(f"  {key}: {value}")
    except Exception as e:
        print(f"  ERROR getting stats: {e}")


def demo_log_parser():
    """Parse the sample log file and show results."""
    separator("6. Log File Analysis")

    log_path = os.path.join(os.path.dirname(__file__), "logs", "network_test_run_001.log")

    if not os.path.exists(log_path):
        print(f"  Log file not found: {log_path}")
        return

    parser = LogParser()
    entries = parser.parse_file(log_path)
    print(f"  Parsed {len(entries)} log entries")

    # Error summary
    errors = parser.get_error_summary(entries)
    if errors:
        print(f"\n  Error summary:")
        for node_id, components in errors.items():
            print(f"    Node 0x{node_id:04X}:")
            for comp, messages in components.items():
                for msg in messages:
                    print(f"      [{comp}] {msg}")

    # Reboot loop detection
    loops = parser.detect_reboot_loops(entries)
    if loops:
        print(f"\n  Reboot loops detected on nodes: {['0x%04X' % n for n in loops]}")
    else:
        print(f"\n  No reboot loops detected.")


def main():
    print("\n" + "=" * 60)
    print("   WIREPAS MESH NETWORK SIMULATOR — DEMO")
    print("=" * 60)

    net, node_names = demo_basic_network()
    net = demo_send_messages(net, node_names)
    demo_diagnostics(net, node_names)
    demo_firmware_update(net, node_names)
    demo_network_stats(net)
    demo_log_parser()

    separator("Done!")
    print("  The demo above shows the simulator in action.")
    print("  Some operations may have produced unexpected results —")
    print("  that's because the simulator contains intentional bugs.")
    print("  Your job is to write tests that find them!\n")


if __name__ == "__main__":
    main()
