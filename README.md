# Wirepas Mesh Network — Test Suite

## 🚀 Quick Start — Run Everything in 4 Steps

**Step 1 — Install:**
```bash
pip install -r requirements.txt
```

**Step 2 — See bugs proven (report opens automatically):**
```bash
python generate_report.py
```

**Step 3 — See integration test:**
```bash
python -m pytest tests/test_integration.py -v -s
```

**Step 4 — See all bugs fixed (report opens automatically):**
```bash
python run_fixed_tests.py
```

> That's it! Both HTML reports open in your browser automatically.

---

A professional pytest-based test suite for a simulated Wirepas mesh network. The suite covers node lifecycle, message routing, network topology, and log parsing — and intentionally documents **11 bug tests** covering 10 real bugs discovered in the simulator code.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Project Structure](#2-project-structure)
3. [Setup](#3-setup)
4. [Running Tests](#4-running-tests)
5. [Generating Reports](#5-generating-reports)
6. [Test Framework Design](#6-test-framework-design)
7. [Bugs Found](#7-bugs-found)
8. [How to Verify the Bugs](#8-how-to-verify-the-bugs)
9. [Assumptions and Design Decisions](#9-assumptions-and-design-decisions)

---

## 1. Project Overview

This project tests a Python simulator (`mesh_simulator/`) that models a **Wirepas mesh network** — a low-power wireless protocol used in industrial IoT deployments (smart meters, asset tracking, building automation, etc.).

The simulator intentionally contains bugs. The test suite's job is to find them, document them clearly, and prove each one fails with a reproducible test. All bugs are separated into dedicated `_bug`-suffixed tests so they can be run in isolation.

**What is tested:**

| Area | What it covers |
|------|---------------|
| Node lifecycle | Boot, shutdown, firmware flash, battery states |
| Message handling | Payload size, hop limits, expiry logic |
| Network routing | Path finding, message delivery, broadcast |
| Network topology | Adding/removing nodes, link creation |
| Log parsing | Parsing log files, filtering by node/level, reboot detection |

---

## 2. Project Structure

```
scaffold/
├── mesh_simulator/           # The simulator under test (contains bugs)
│   ├── node.py               # Node states, boot, send/receive, diagnostics
│   ├── message.py            # Message creation, payload, hop logic
│   ├── network.py            # Routing, topology, stats, broadcast
│   └── log_parser.py         # Log file reader and analyzer
│
├── mesh_simulator_fixed/     # Bonus: fixed version of the simulator
│
├── tests/
│   ├── conftest.py           # Shared fixtures (nodes, messages, network)
│   ├── helpers.py            # Utility: load_cases() for JSON test data
│   │
│   ├── test_data/            # Data-driven test inputs (JSON)
│   │   ├── boot_cases.json
│   │   ├── battery_cases.json
│   │   ├── firmware_cases.json
│   │   ├── send_receive_cases.json
│   │   ├── hop_cases.json
│   │   ├── payload_cases.json
│   │   ├── routing_cases.json
│   │   └── log_line_cases.json
│   │
│   ├── node/                 # Node lifecycle tests
│   │   ├── test_boot.py
│   │   ├── test_battery.py
│   │   ├── test_firmware.py
│   │   ├── test_send_receive.py
│   │   └── test_diagnostics.py
│   │
│   ├── message/              # Message behaviour tests
│   │   ├── test_creation.py
│   │   ├── test_hops.py
│   │   └── test_payload.py
│   │
│   ├── network/              # Network-level tests
│   │   ├── test_topology.py
│   │   ├── test_routing.py
│   │   ├── test_broadcast.py
│   │   └── test_stats.py
│   │
│   └── log_parser/           # Log analysis tests
│       ├── test_parsing.py
│       ├── test_filtering.py
│       └── test_reboot_detection.py
│
├── logs/
│   └── network_test_run_001.log   # Sample log file for parser tests
│
├── generate_report.py        # Custom HTML report generator (start here!)
├── run_fixed_tests.py        # Proves all bugs are fixed in mesh_simulator_fixed/
├── pytest.ini                # Pytest config and mark registration
├── BUG_REPORT.md             # Detailed bug documentation
└── requirements.txt          # Python dependencies
```

---

## 3. Setup

**Requirements:** Python 3.10+

```bash
# Clone or unzip the project, then:
pip install -r requirements.txt
```

That's it. No database, no external services, no environment variables needed.

---

## 4. Running Tests

### Run the full suite

```bash
python -m pytest tests/ -v
```

Expected: **11 failed** (bugs proven) **48 passed** (correct behaviour verified)

### Run only bug tests (all 11 will FAIL — that is expected and correct)

```bash
python -m pytest -m bug -v
```

### Run only smoke tests (fast critical-path checks)

```bash
python -m pytest -m smoke -v
```

### Run only regression tests

```bash
python -m pytest -m regression -v
```

### Run a specific test file

```bash
python -m pytest tests/node/test_boot.py -v
```

### Run tests by category

```bash
python -m pytest tests/node/ -v         # All node tests
python -m pytest tests/network/ -v      # All network tests
python -m pytest tests/message/ -v      # All message tests
python -m pytest tests/log_parser/ -v   # All log parser tests
```

---

## 5. Generating Reports

### 🌟 Custom Visual Report (Start Here — Highly Recommended!)

```bash
python generate_report.py
```

The report opens automatically in your browser!

This report is **generated fresh every run** from actual test and coverage results.
It is designed for non-technical stakeholders — every bug is explained in plain English
with its real-world impact on IoT deployments.

| Section | What you see |
|---------|-------------|
| 📊 Summary cards | Total tests · Passing · Bugs found · Pass rate · Code coverage % |
| 🏥 Health bar | Visual pass rate indicator |
| 📈 Coverage breakdown | Per-file coverage with progress bars — generated from real run |
| 🐛 Bug cards | Every bug in plain English with real-world IoT impact, sorted by severity |
| ✅ Passing checks | Full list of what works correctly |

> All numbers in the report come from the actual test run —
> nothing is hardcoded.

---

### Standard pytest HTML Report

```bash
python -m pytest tests/ --html=report.html --self-contained-html
```

### Run with Coverage in Terminal

```bash
python -m pytest tests/ --cov=mesh_simulator --cov-report=term
```

### Detailed Line-by-Line Coverage

```bash
python -m pytest tests/ --cov=mesh_simulator --cov-report=html
# Then open htmlcov/index.html
```

### Verify Fixed Code Passes All Tests (Bonus)

```bash
python run_fixed_tests.py
```

Expected: **59 passed, 0 failed** — all 10 bugs fixed!

---

## 6. Test Framework Design

### Data-driven testing with JSON

Test cases live in `tests/test_data/` as JSON files. Each file maps to a test area (e.g., `boot_cases.json` for boot tests). The `helpers.load_cases(filename)` utility loads them, and pytest's `@pytest.mark.parametrize` runs each case as a separate test. This keeps test logic and test data cleanly separated — adding a new scenario means editing JSON, not Python.

### Custom marks

| Mark | Purpose |
|------|---------|
| `smoke` | Fast, critical-path checks — run these first |
| `regression` | Core functionality tests that should always pass |
| `bug` | Tests that prove a specific bug exists — expected to FAIL |
| `positive` | Tests for correct/happy-path behaviour |
| `negative` | Tests for edge cases, invalid inputs, and error conditions |

Marks are registered in `pytest.ini` to avoid warnings. Run any combination with `-m "smoke and regression"` etc.

### Fixtures in conftest.py

| Fixture | Scope | What it provides |
|---------|-------|-----------------|
| `parsed_log_entries` | session | Parses `network_test_run_001.log` once for all log parser tests |
| `online_node` | function | A booted ONLINE node (node_id=1) |
| `offline_node` | function | An unbooted OFFLINE node (node_id=99) |
| `low_battery_node` | function | A booted LOW_BATTERY node at 15% (node_id=2) |
| `sample_message` | function | A DATA message from node 1 → node 2 with payload `b"hello mesh"` |
| `simple_network` | function | A three-node linear network (1--2--3) with teardown cleanup |

### Bug tests vs. normal tests

Every bug has its own dedicated test method ending in `_bug` (e.g., `test_node_boot_behaviour_bug`). These are marked `@pytest.mark.bug` and are expected to **FAIL** — a failing bug test is a passing assertion that the bug is real. Normal tests (without `_bug`) cover the same area but test correct behaviour and should always pass.

### helpers.py

`helpers.load_cases(filename)` resolves paths relative to `tests/test_data/` and returns the parsed JSON as a list. Used in every parametrized test to keep file path logic in one place.

---

## 7. Bugs Found

10 bugs were identified across the simulator, covered by 11 bug tests (Bug #1 has two test cases). Severity follows standard IoT industry risk classification.

| # | File | Method | Severity | Description |
|---|------|--------|----------|-------------|
| 1 | `message.py` | `payload_size()` | MEDIUM | Returns size 3 bytes larger than actual — wraps bytes in `b'...'` string representation before measuring |
| 2 | `node.py` | `boot()` | CRITICAL | Dead nodes (0% battery) are marked ONLINE instead of ERROR — dead meters appear active on the dashboard |
| 3 | `node.py` | `flash_firmware()` | HIGH | Node stays OFFLINE after a successful firmware update — `shutdown()` is called but `boot()` is never called to bring it back online |
| 4 | `node.py` | `get_diagnostics()` | MEDIUM | Queue depth in diagnostics reports `received_messages` count instead of `message_queue` depth — misleads operators about backlog |
| 5 | `message.py` | `is_expired()` | HIGH | Uses `>` instead of `>=` — a message at exactly `max_hops` is not expired, causing it to travel one hop too many |
| 6 | `network.py` | `route_message()` | HIGH | Path iteration starts at index 0 instead of 1 — the source node receives its own message |
| 7 | `network.py` | `get_network_stats()` | CRITICAL | Division by zero when no messages have been sent yet — the network dashboard crashes on startup |
| 8 | `network.py` | `remove_node()` | CRITICAL | Removed nodes are deleted from `self.nodes` but not from neighbors' lists or routing tables — removed devices still receive traffic |
| 9 | `node.py` | `send_message()` | HIGH | Only `ONLINE` nodes can send — `LOW_BATTERY` nodes are blocked, meaning degraded-but-functional devices silently drop their readings |
| 10 | `log_parser.py` | `parse_file()` | MEDIUM | Raises an unhandled `FileNotFoundError` when the log file is missing, instead of returning an empty result or a meaningful error message |

---

## 8. How to Verify the Bugs

Run the bug tests:

```bash
python -m pytest -m bug -v
```

All 11 tests will **FAIL**. Each failure is a confirmed, reproducible proof that the bug exists in the simulator. The test output tells you exactly what was expected versus what the buggy code returned.

To see bugs explained in plain English with real-world impact:

```bash
python generate_report.py
# then open test_report.html
```

To verify all bugs are fixed in `mesh_simulator_fixed/`:

```bash
python run_fixed_tests.py
# Expected: 59 passed, 0 failed
```

---

## 9. Assumptions and Design Decisions

**Bugs are not fixed in the original simulator.** The simulator code is left intentionally broken. The test suite's purpose is detection and documentation, not correction. Fixed code lives in `mesh_simulator_fixed/` — run `python run_fixed_tests.py` to verify.

**Bug tests are expected to fail.** `pytest -m bug` will always show 11 failures against the original code. This is correct behaviour. The CI/CD interpretation would be: "these are known bugs, tracked separately, not regressions."

**Severity is based on operational impact.** CRITICAL bugs cause crashes or silent data corruption at the system level. HIGH bugs cause incorrect behavior that would mislead operators. MEDIUM bugs produce wrong values that could cause incorrect decisions over time.

**Data-driven testing was chosen for scalability.** Adding a new boot scenario means adding a JSON object to `boot_cases.json` — no Python changes needed. This makes the test suite maintainable by QA engineers who may not write Python daily.

**The `smoke` mark subset covers startup confidence.** Running `-m smoke` gives fast feedback (under 5 seconds) that the most critical paths — adding nodes, broadcasting, detecting reboots — are at least partially functional.

**`conftest.py` fixtures use function scope by default** to ensure test isolation. The one exception is `parsed_log_entries` (session scope) since parsing the log file is an I/O operation that doesn't mutate state.

**`LOW_BATTERY` nodes are expected to send.** The test for Bug #9 assumes that a node at low battery should still be able to transmit — it's degraded, not dead. Silently dropping readings from a deployed meter is a data-loss bug, not safe behaviour.
