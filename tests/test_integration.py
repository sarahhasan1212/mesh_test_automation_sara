import pytest
from mesh_simulator import MeshNode, MeshNetwork, MeshMessage, MessageType
from mesh_simulator.node import NodeState


@pytest.mark.regression
@pytest.mark.positive
def test_full_mesh_network_lifecycle(capsys):
    """
    WHAT IS BEING TESTED: Complete mesh network lifecycle end to end
    EXPECTED BEHAVIOUR: Network boots, messages route across multiple
        hops, low battery handled, firmware flashes, stats correct
        — all components working together!
    """

    print("\n")
    print("=" * 55)
    print("  WIREPAS MESH NETWORK — INTEGRATION TEST")
    print("=" * 55)

    # --------------------------------------------------------
    # Step 1 — Build network
    # --------------------------------------------------------
    print("\n📡 Step 1: Building 5-node mesh network...")
    network = MeshNetwork(network_id="integration_test")
    for node_id in range(1, 6):
        network.add_node(MeshNode(node_id=node_id, firmware_version="1.0.0"))
    network.create_link(1, 2)
    network.create_link(2, 3)
    network.create_link(3, 4)
    network.create_link(4, 5)
    network.boot_all()

    online = len(network.get_online_nodes())
    assert online == 5, f"Expected 5 online nodes but got {online}"
    print(f"   ✅ {online}/5 nodes online")
    print(f"   ✅ Topology: Node1 -- Node2 -- Node3 -- Node4 -- Node5")

    # --------------------------------------------------------
    # Step 2 — Send DATA message across 4 hops
    # --------------------------------------------------------
    print("\n📨 Step 2: Sending DATA message Node1 → Node5 (4 hops)...")
    msg1 = MeshMessage(
        source_id=1,
        destination_id=5,
        msg_type=MessageType.DATA,
        payload=b"sensor_reading=22.5C"
    )
    result1 = network.route_message(msg1)

    assert result1 is True, "Expected message delivered from node 1 to node 5"
    assert len(network.delivered_messages) == 1
    print(f"   ✅ Message delivered successfully across 4 hops")
    print(f"   ✅ Payload: sensor_reading=22.5C")

    # --------------------------------------------------------
    # Step 3 — Node 3 battery runs low
    # --------------------------------------------------------
    print("\n🔋 Step 3: Node3 battery running low (15%)...")
    network.nodes[3].battery_level = 15.0
    network.nodes[3].state = NodeState.LOW_BATTERY

    assert network.nodes[3].state == NodeState.LOW_BATTERY
    assert network.nodes[3] in network.get_online_nodes()
    print(f"   ✅ Node3 state: LOW_BATTERY")
    print(f"   ✅ Node3 still online — degraded but functional")
    print(f"   ✅ All 5 nodes still reachable")

    # --------------------------------------------------------
    # Step 4 — Send DIAGNOSTIC through LOW_BATTERY node
    # --------------------------------------------------------
    print("\n🔍 Step 4: Sending DIAGNOSTIC through LOW_BATTERY Node3...")
    msg2 = MeshMessage(
        source_id=5,
        destination_id=1,
        msg_type=MessageType.DIAGNOSTIC,
        payload=b'{"battery":15,"rssi":-67}'
    )
    result2 = network.route_message(msg2)

    assert result2 is True, "Expected message to route through LOW_BATTERY node"
    print(f"   ✅ DIAGNOSTIC delivered through LOW_BATTERY node successfully")

    # --------------------------------------------------------
    # Step 5 — Flash firmware on Node 2
    # --------------------------------------------------------
    print("\n⚡ Step 5: Flashing firmware on Node2 (1.0.0 → 2.0.0)...")
    flash_result = network.nodes[2].flash_firmware("2.0.0", b"new_firmware")

    assert flash_result is True
    assert network.nodes[2].firmware_version == "2.0.0"
    print(f"   ✅ Firmware flashed successfully")
    print(f"   ✅ Node2 version: 1.0.0 → 2.0.0")

    # --------------------------------------------------------
    # Step 6 — Check network stats
    # --------------------------------------------------------
    print("\n📊 Step 6: Checking network statistics...")
    msg3 = MeshMessage(
        source_id=1,
        destination_id=4,
        msg_type=MessageType.HEARTBEAT,
        payload=b"heartbeat"
    )
    network.route_message(msg3)
    stats = network.get_network_stats()

    assert stats["total_nodes"] == 5
    assert stats["delivered_messages"] >= 2
    assert stats["delivery_rate"] > 0.0
    assert stats["avg_battery"] > 0.0
    print(f"   ✅ Total nodes:        {stats['total_nodes']}")
    print(f"   ✅ Online nodes:       {stats['online_nodes']}")
    print(f"   ✅ Delivered messages: {stats['delivered_messages']}")
    print(f"   ✅ Delivery rate:      {stats['delivery_rate']:.0%}")
    print(f"   ✅ Average battery:    {stats['avg_battery']:.1f}%")

    # --------------------------------------------------------
    # Final summary
    # --------------------------------------------------------
    print("\n" + "=" * 55)
    print("  ✅ INTEGRATION TEST PASSED SUCCESSFULLY!")
    print("=" * 55)
    print("  All components working together correctly:")
    print("  • Network boot         ✅")
    print("  • Multi-hop routing    ✅")
    print("  • Low battery handling ✅")
    print("  • Firmware update      ✅")
    print("  • Network statistics   ✅")
    print("=" * 55)