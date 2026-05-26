# Wirepas Mesh Simulator — Test Automation Challenge

## Overview

You are given a **simplified mesh network simulator** written in Python. It models a Wirepas-like IoT mesh network where nodes communicate by relaying messages through neighbors.

The simulator contains **intentional bugs**. Your primary job is to find them through testing and document them clearly.

### Simulator Concepts

**Nodes** are battery-operated devices, each with a unique integer ID. Every node runs a state machine with the following states: `OFFLINE`, `BOOTING`, `ONLINE`, `LOW_BATTERY`, and `ERROR`. A node must be `ONLINE` (or `LOW_BATTERY`) to send or receive messages. Nodes start `OFFLINE` and must be explicitly booted.

**Battery model**: each transmission drains more battery than a reception. When the battery level drops below a threshold, the node transitions to `LOW_BATTERY`. A node with no battery cannot boot successfully. Firmware flashing requires a minimum battery level.

**Neighbor tables**: each node maintains a list of directly reachable neighbor node IDs. Links between nodes are bidirectional -- when a link is created, both nodes register each other as neighbors.

**Hop-based routing**: messages travel through intermediate relay nodes to reach their destination. Each time a message passes through a relay, its hop counter is incremented. A message is considered expired and gets dropped when its hop count exceeds `max_hops`. The network uses BFS to find the shortest path between source and destination.

**Message types**: `DATA` carries application payloads (e.g. sensor readings), `DIAGNOSTIC` carries node health info, `HEARTBEAT` signals liveness, `ROUTE_UPDATE` signals topology changes, and `FIRMWARE_UPDATE` carries OTAP payloads. There is a maximum payload size per message.

**OTAP flow**: firmware updates are applied node by node. The node must be online and have sufficient battery. After flashing, the node shuts down and must reboot to come back online with the new firmware version.

**Log format**: nodes emit structured serial log lines identified by a hex node ID, a log level (`INFO`, `WARN`, `ERROR`, `DEBUG`), a component tag (e.g. `BOOT`, `BATT`, `MESH`), and a free-text message. These logs are the primary tool for post-hoc analysis of network events.

**Time estimate:** 2–4 hours
**Choose your tools:** You may use **pytest**, **Robot Framework**, **unittest**, or plain Python — whichever you're most comfortable with.

---

## Getting Started

Start by running the demo script to see the simulator in action:

```bash
python demo.py
```

This creates a small mesh network, sends messages, updates firmware, and parses a log file. Pay attention to the output — some things may already look off. No dependencies beyond Python 3.10+ are needed to run the demo.

---

## What You Receive

```
scaffold/
├── demo.py                  # Run this first to see the simulator in action
├── mesh_simulator/          # The simulator code (with bugs)
│   ├── __init__.py
│   ├── message.py           # Message types and routing metadata
│   ├── node.py              # Individual mesh node simulation
│   ├── network.py           # Network topology and message routing
│   └── log_parser.py        # Serial log file parser
├── logs/
│   └── network_test_run_001.log   # Sample serial log output
├── tests/                   # Place your tests here 
│   └── test.py | test.robot
└── requirements.txt         # Empty — you decide the dependencies
```

---

## Tasks

### Task 1: Write Tests (Primary Focus)

Implement a comprehensive test suite into `tests/` directory that covers:

1. **Node behavior**
2. **Message handling**
3. **Network routing**
4. **Log parsing**
5. **Integration scenarios**

We evaluate:
- **Coverage breadth** — did you test the important behaviors?
- **Test quality** — are tests isolated, readable, and well-named?
- **Bug detection** — how many of the planted bugs did your tests catch?
- **Edge cases** — did you think about boundary conditions?

### Task 2: Bug Report

Create a file called `BUG_REPORT.md` listing each bug you found. For each bug, include:

- **Location**: file and function name
- **Description**: what's wrong
- **Impact**: what would happen in a real system
- **How your test catches it**: reference the specific test

### Task 3 (Bonus): Fix the Bugs

If you have time, fix the bugs you identified in the simulator code. Create a copy of the simulator or work on the original — your choice. Make sure all your tests pass against the fixed code.

### Task 4 (Bonus): Log Analysis

Using the provided log file (`logs/network_test_run_001.log`), write a script or test that:

- Identifies which node is stuck in a reboot loop
- Calculates message delivery statistics from the log
- Detects the node that went offline due to low battery
- Produces a brief summary report (printed to stdout or written to a file)

---

## Submission

Please submit the entire project as a **zip file** or a **git repository link**. Your submission must include:

1. Your complete test suite (all test files)
2. `BUG_REPORT.md`
3. A **README.md** with:
   - How to set up the environment (dependencies, virtual environment, etc.)
   - How to run the full test suite
   - How to run individual test files or specific tests
   - Any assumptions or design decisions you made
4. A properly filled `requirements.txt` with all dependencies needed to run your tests
5. (Bonus) Fixed simulator code
6. (Bonus) Log analysis script/output

We should be able to clone/unzip your submission and get the tests running by following your README. Think of it as handing off your work to a colleague.

---

## Evaluation Criteria

| Criteria | Weight |
|---|---|
| Test coverage and quality | 45% |
| Bugs found and reported | 25% |
| Project setup and documentation (README, requirements.txt, runnable) | 15% |
| Code quality and structure | 10% |
| Bonus tasks (bug fixes, log analysis) | 5% |

---

## Notes

- You do **not** need to add features to the simulator — just test it and find bugs.
- The `requirements.txt` is intentionally empty. Part of the evaluation is seeing how you manage dependencies and project setup.
- We value clear, maintainable test code over clever tricks.
- Feel free to restructure the test files however you like.
- If you use Robot Framework, you can convert the Python tests to `.robot` files or create a hybrid approach.

Good luck! We look forward to reviewing your work.
