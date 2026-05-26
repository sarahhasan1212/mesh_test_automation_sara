# Bug Report — Wirepas Mesh Network Simulator

**Project:** mesh_simulator  
**Total bugs found:** 10  
**Bug tests:** 11 (Bug #1 has two parametrized test cases)  
**Severities:** 3 CRITICAL · 4 HIGH · 3 MEDIUM

To reproduce all bugs in one command:

```bash
python -m pytest -m bug -v
```

All 11 tests will FAIL. Each failure is reproducible proof that the bug exists.

---

## Bug #1

**Title:** Payload size reported incorrectly — always 3 bytes too large

**Location:** `mesh_simulator/message.py` · `MeshMessage.payload_size()`

**Severity:** MEDIUM

**Description:**  
`payload_size()` calls `len(str(self.payload))` instead of `len(self.payload)`.
Converting a `bytes` object to a string wraps it in `b'...'` notation before
measuring, adding 3 extra characters (`b`, `'`, `'`) to every result.

```python
# Buggy
def payload_size(self) -> int:
    return len(str(self.payload))   # b'hello' → "b'hello'" → 8, not 5

# Fixed
def payload_size(self) -> int:
    return len(self.payload)        # b'hello' → 5
```

**Impact:**  
In a real IoT deployment, the gateway uses payload size to enforce the 102-byte
Wirepas frame limit. With this bug, a 99-byte payload is reported as 102 bytes and
rejected as oversized — valid sensor readings are silently dropped.

**How the test catches it:**  
`tests/message/test_payload.py::test_payload_size_method_bug`  
Parametrized over two cases: a 5-byte and an 11-byte payload. Both assert that
`payload_size()` equals `len(payload)`. The buggy code returns values 3 higher in
each case, so both parametrized instances fail.

---

## Bug #2

**Title:** Dead node (0% battery) marked ONLINE instead of ERROR

**Location:** `mesh_simulator/node.py` · `MeshNode.boot()`

**Severity:** CRITICAL

**Description:**  
When `battery_level == 0`, the `else` branch in `boot()` sets
`self.state = NodeState.ONLINE` before returning `False`. The return value
signals failure, but the state is set to ONLINE — the opposite of what it should be.

```python
# Buggy
else:
    self.state = NodeState.ONLINE   # wrong — node is dead, not online
    logger.error(...)
    return False

# Fixed
else:
    self.state = NodeState.ERROR    # correctly marks node as failed
    logger.error(...)
    return False
```

**Impact:**  
A deployed meter with a dead battery appears ONLINE on the network dashboard.
Operators see it as active and expect it to be reporting. No alerts are raised,
maintenance is not dispatched, and data gaps go undetected until they cause
billing or safety incidents.

**How the test catches it:**  
`tests/node/test_boot.py::test_node_boot_behaviour_bug[boot-zero-battery]`  
Boots a node with `battery_level = 0`, asserts `boot()` returns `False` AND
`node.state == NodeState.ERROR`. The buggy code returns `False` but leaves state
as `ONLINE`, so the state assertion fails.

---

## Bug #3

**Title:** Node stays OFFLINE after successful firmware update

**Location:** `mesh_simulator/node.py` · `MeshNode.flash_firmware()`

**Severity:** HIGH

**Description:**  
`flash_firmware()` calls `self.shutdown()` to take the node offline for flashing,
updates `self.firmware_version`, then returns `True` — but never calls `self.boot()`
to bring the node back online. The flash succeeds but the node is permanently stuck
in OFFLINE state.

```python
# Buggy
self.shutdown()
self.firmware_version = new_version
return True             # node is still OFFLINE

# Fixed
self.shutdown()
self.firmware_version = new_version
self.boot()             # reboot after flash
return True
```

**Impact:**  
Every OTA firmware update permanently takes the device offline. In a large
industrial deployment, a routine firmware rollout silently bricks every meter in
the network. No sensor data is collected, no alerts are sent, and the network
appears to be operating normally until someone physically inspects the hardware.

**How the test catches it:**  
`tests/node/test_firmware.py::test_firmware_flash_behaviour_bug[flash-success-full-battery]`  
Flashes a node with full battery, asserts the return value is `True` AND
`node.state == NodeState.ONLINE`. The buggy code returns `True` but leaves the
node OFFLINE, so the state assertion fails.

---

## Bug #4

**Title:** Diagnostics reports wrong queue depth — shows received count instead

**Location:** `mesh_simulator/node.py` · `MeshNode.get_diagnostics()`

**Severity:** MEDIUM

**Description:**  
The `queue_depth` field in the diagnostics dictionary uses
`len(self.received_messages)` instead of `len(self.message_queue)`.
These are two separate lists: `message_queue` holds messages waiting to be
transmitted; `received_messages` holds messages already processed.

```python
# Buggy
"queue_depth": len(self.received_messages)   # wrong list

# Fixed
"queue_depth": len(self.message_queue)       # correct list
```

**Impact:**  
Network operators use queue depth to detect backlogged nodes. With this bug, the
reported queue depth reflects historic received traffic, not pending outbound work.
A node with 50 messages stuck in its transmit queue shows a depth of 0 if it has
received nothing — no alert is raised, the backlog grows, and messages are
eventually dropped without any warning.

**How the test catches it:**  
`tests/node/test_diagnostics.py::test_diagnostics_queue_depth_shows_message_queue_not_received`  
Sends a message to the node's queue without receiving anything, then asserts
`get_diagnostics()["queue_depth"] == 1`. The buggy code returns 0 (the length of
the empty `received_messages` list), so the assertion fails.

---

## Bug #5

**Title:** Messages travel one hop too many — off-by-one in expiry check

**Location:** `mesh_simulator/message.py` · `MeshMessage.is_expired()`

**Severity:** HIGH

**Description:**  
`is_expired()` uses strict greater-than (`>`) instead of greater-than-or-equal
(`>=`). A message with `hop_count == max_hops` is not considered expired and is
forwarded one more time before being dropped at `hop_count == max_hops + 1`.

```python
# Buggy
def is_expired(self) -> bool:
    return self.hop_count > self.max_hops   # allows one extra hop

# Fixed
def is_expired(self) -> bool:
    return self.hop_count >= self.max_hops  # expires exactly at the limit
```

**Impact:**  
In a Wirepas mesh, `max_hops` is a hard protocol boundary set to prevent routing
loops. Messages that exceed it consume radio airtime and battery on every node they
pass through. In a large network, loop conditions involving expired messages can
cause measurable battery drain and increased packet collision rates.

**How the test catches it:**  
`tests/message/test_hops.py::test_hop_count_and_expiry_bug[expired-at-exactly-max]`  
Creates a message with `hop_count == max_hops` and asserts `is_expired()` returns
`True`. The buggy code returns `False`, so the assertion fails.

---

## Bug #6

**Title:** Source node receives its own message

**Location:** `mesh_simulator/network.py` · `MeshNetwork.route_message()`

**Severity:** HIGH

**Description:**  
After finding the BFS path, `route_message()` iterates over `path[0:]` — starting
at index 0, which is the source node. The source node already called
`send_message()` to originate the message; iterating from index 0 causes it to
also call `receive_message()`, adding the message to its own received list.

```python
# Buggy
for node_id in path[0:]:    # includes source at index 0
    node.receive_message(message)

# Fixed
for node_id in path[1:]:    # skip source, deliver only to intermediates + dest
    node.receive_message(message)
```

**Impact:**  
Every node in a Wirepas mesh will process a copy of every message it originates.
Application logic that counts received messages (e.g., acknowledgement tracking,
duplicate detection) will double-count. Diagnostics will show impossible RX/TX
ratios, and any deduplication logic downstream will be confused.

**How the test catches it:**  
`tests/network/test_routing.py::test_message_routing_bug[source-does-not-receive-own-message]`  
Routes a message from node 1 to node 2, then asserts that node 1's
`received_messages` list is empty. The buggy code adds the message to node 1's
received list, so the assertion fails.

---

## Bug #7

**Title:** Network dashboard crashes on startup — division by zero

**Location:** `mesh_simulator/network.py` · `MeshNetwork.get_network_stats()`

**Severity:** CRITICAL

**Description:**  
`get_network_stats()` computes delivery rate as
`delivered / (delivered + dropped)` with no guard for the case where both
are zero (i.e., no messages have been sent yet). This raises a `ZeroDivisionError`
whenever the function is called on a fresh network.

```python
# Buggy
"delivery_rate": len(self.delivered_messages) / (
    len(self.delivered_messages) + len(self.dropped_messages)
)

# Fixed
"delivery_rate": delivered / total_messages if total_messages > 0 else 0.0
```

**Impact:**  
Any monitoring dashboard or health-check endpoint that calls `get_network_stats()`
on startup — before any traffic has flowed — will crash with an unhandled exception.
In a production deployment, this means the network management system is unavailable
exactly when operators most need it: during initial bring-up and after a full
network restart.

**How the test catches it:**  
`tests/network/test_stats.py::test_network_stats_no_crash_with_zero_messages`  
Calls `get_network_stats()` on a freshly created network with no messages sent,
wrapped in a `pytest.raises` check. The buggy code raises `ZeroDivisionError`,
so the test fails (the exception propagates instead of being caught).

---

## Bug #8

**Title:** Removed nodes remain in routing tables and neighbor lists

**Location:** `mesh_simulator/network.py` · `MeshNetwork.remove_node()`

**Severity:** CRITICAL

**Description:**  
`remove_node()` deletes the node from `self.nodes` but does not remove it from
other nodes' `neighbors` lists or from `self._routing_table`. Routes through the
removed node remain valid in the routing table, and other nodes still list it as
a neighbor.

```python
# Buggy
def remove_node(self, node_id: int) -> bool:
    if node_id not in self.nodes:
        return False
    del self.nodes[node_id]   # only removes from nodes dict
    return True

# Fixed
def remove_node(self, node_id: int) -> bool:
    if node_id not in self.nodes:
        return False
    for other_node in self.nodes.values():
        other_node.remove_neighbor(node_id)
    for routes in self._routing_table.values():
        if node_id in routes:
            routes.remove(node_id)
    del self._routing_table[node_id]
    del self.nodes[node_id]
    return True
```

**Impact:**  
When a physical device is decommissioned or fails, the network continues routing
traffic through it. Messages destined for other nodes are lost without a dropped
count being recorded — they simply vanish. In a smart metering deployment, this
produces silent data loss that is extremely hard to diagnose because the routing
table looks correct.

**How the test catches it:**  
`tests/network/test_topology.py::test_remove_node_cleans_up_neighbors`  
Creates a three-node network (1–2–3), removes node 2, then asserts that node 1's
`neighbors` list no longer contains node 2. The buggy code leaves node 2 in node 1's
neighbor list, so the assertion fails.

---

## Bug #9

**Title:** LOW_BATTERY nodes cannot send — degraded devices silently drop readings

**Location:** `mesh_simulator/node.py` · `MeshNode.send_message()`

**Severity:** HIGH

**Description:**  
`send_message()` checks `if self.state != NodeState.ONLINE` and rejects any node
that is not in the exact ONLINE state. Nodes in `LOW_BATTERY` state are blocked
from sending even though the protocol allows degraded-but-functional nodes to
transmit. The `receive_message()` method correctly allows `LOW_BATTERY` nodes —
making the inconsistency clear.

```python
# Buggy
if self.state != NodeState.ONLINE:   # rejects LOW_BATTERY
    return False

# Fixed
if self.state not in (NodeState.ONLINE, NodeState.LOW_BATTERY):   # allows both
    return False
```

**Impact:**  
In field deployments, battery levels vary. A node at 15% battery is degraded but
still operational — it should continue reporting until it is replaced. With this
bug, the moment a node drops below the 20% threshold it stops transmitting entirely.
Operators see a healthy-looking node (it is not ERROR or OFFLINE) but receive no
data from it, with no indication of why.

**How the test catches it:**  
`tests/node/test_send_receive.py::test_node_send_receive_behaviour_bug[low-battery-can-send-bug]`  
Sets a node to `LOW_BATTERY` state, calls `send_message()`, and asserts the return
value is `True`. The buggy code returns `False`, so the assertion fails.

---

## Bug #10

**Title:** Log parser crashes on missing file — no error handling

**Location:** `mesh_simulator/log_parser.py` · `LogParser.parse_file()`

**Severity:** MEDIUM

**Description:**  
`parse_file()` opens the file with a bare `open()` call and no exception handling.
If the file does not exist, Python raises an unhandled `FileNotFoundError` that
propagates to the caller. The function should return an empty list and let the
caller decide how to handle a missing log file.

```python
# Buggy
def parse_file(self, filepath: str) -> list[LogEntry]:
    entries = []
    with open(filepath, 'r') as f:   # crashes if file missing
        ...
    return entries

# Fixed
def parse_file(self, filepath: str) -> list[LogEntry]:
    try:
        entries = []
        with open(filepath, 'r') as f:
            ...
        return entries
    except FileNotFoundError:
        return []
```

**Impact:**  
A missing or misconfigured log path crashes the entire diagnostic pipeline. In
production, log files rotate and are sometimes temporarily unavailable. A single
missing file brings down log ingestion for all nodes, making it impossible to
monitor any part of the network until the file reappears or the path is corrected.

**How the test catches it:**  
`tests/log_parser/test_parsing.py::test_log_parser_behaviour_bug[missing-file-handled-gracefully-bug]`  
Calls `parse_file()` with a path that does not exist and asserts the return value
is an empty list `[]`. The buggy code raises `FileNotFoundError` instead of
returning gracefully, so the test fails.

---

## Summary Table

| # | File | Method | Severity | Root Cause |
|---|------|--------|----------|------------|
| 1 | `message.py` | `payload_size()` | MEDIUM | `len(str(payload))` instead of `len(payload)` |
| 2 | `node.py` | `boot()` | CRITICAL | Sets `ONLINE` instead of `ERROR` on battery failure |
| 3 | `node.py` | `flash_firmware()` | HIGH | Missing `self.boot()` call after flash |
| 4 | `node.py` | `get_diagnostics()` | MEDIUM | Reports `received_messages` length as queue depth |
| 5 | `message.py` | `is_expired()` | HIGH | `>` should be `>=` |
| 6 | `network.py` | `route_message()` | HIGH | `path[0:]` should be `path[1:]` |
| 7 | `network.py` | `get_network_stats()` | CRITICAL | Division by zero when message counts are both 0 |
| 8 | `network.py` | `remove_node()` | CRITICAL | Routing table and neighbor lists not cleaned up |
| 9 | `node.py` | `send_message()` | HIGH | `LOW_BATTERY` state not permitted to send |
| 10 | `log_parser.py` | `parse_file()` | MEDIUM | No `FileNotFoundError` handling |

---

*All bugs are fixed in `mesh_simulator_fixed/`. Run `python run_fixed_tests.py` to verify: 58 passed, 0 failed.*
