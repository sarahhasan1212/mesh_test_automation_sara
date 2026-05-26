import sys
import os
import json
import builtins
import pytest
from pathlib import Path

# ============================================================
# PATH SETUP — fixes imports for all test files automatically
# No need to repeat sys.path.insert in every test file!
# ============================================================
sys.path.insert(0, str(Path(__file__).parent.parent))


# ============================================================
# DATA LOADER — shared helper for all data-driven test files
# No need to repeat load_cases() in every test file!
# ============================================================


def _with_marks(cases):
    """Wrap parametrize cases, applying pytest.mark.smoke where case has 'smoke': true."""
    return [
        pytest.param(c, marks=[pytest.mark.smoke], id=c["id"]) if c.get("smoke")
        else pytest.param(c, id=c["id"])
        for c in cases
    ]


builtins._with_marks = _with_marks


# ============================================================
# SHARED FIXTURES — available to ALL test files automatically
# ============================================================
from mesh_simulator import MeshNode, MeshNetwork, MeshMessage, MessageType
from mesh_simulator.node import NodeState
from mesh_simulator.log_parser import LogParser


@pytest.fixture
def online_node():
    """A booted ONLINE node ready for testing."""
    node = MeshNode(node_id=1, firmware_version="1.0.0")
    node.boot()
    return node


@pytest.fixture
def offline_node():
    """An unbooted OFFLINE node."""
    return MeshNode(node_id=99, firmware_version="1.0.0")


@pytest.fixture
def low_battery_node():
    """A booted node in LOW_BATTERY state."""
    node = MeshNode(node_id=2, firmware_version="1.0.0")
    node.boot()
    node.battery_level = 15.0
    node.state = NodeState.LOW_BATTERY
    return node


@pytest.fixture
def sample_message():
    """A basic DATA message from node 1 to node 2."""
    return MeshMessage(
        source_id=1,
        destination_id=2,
        msg_type=MessageType.DATA,
        payload=b"hello mesh"
    )


@pytest.fixture
def simple_network():
    """
    A three node linear network 1--2--3
    all nodes booted and linked.
    TEARDOWN: clears all nodes after test.
    """
    network = MeshNetwork(network_id="test_network")
    for node_id in (1, 2, 3):
        network.add_node(MeshNode(node_id=node_id))
    network.create_link(1, 2)
    network.create_link(2, 3)
    network.boot_all()
    yield network
    # TEARDOWN — clean state after each test
    network.nodes.clear()
    network.delivered_messages.clear()
    network.dropped_messages.clear()


@pytest.fixture(scope="session")
def parsed_log_entries():
    """
    Parse the real log file ONCE for the entire test session.
    Session scoped — expensive operation done only once!
    """
    log_path = Path(__file__).parent.parent / "logs" / "network_test_run_001.log"
    parser = LogParser()
    return parser.parse_file(str(log_path))

