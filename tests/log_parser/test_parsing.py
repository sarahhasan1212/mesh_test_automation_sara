import pytest
from pathlib import Path

from mesh_simulator.log_parser import LogParser
from helpers import load_cases


_ALL_CASES = load_cases("log_line_cases.json")
_NORMAL_CASES = [c for c in _ALL_CASES if not c.get("missing_file")]
_BUG_CASES = [c for c in _ALL_CASES if c.get("missing_file")]


@pytest.mark.regression
@pytest.mark.parametrize(
    "case",
    _NORMAL_CASES,
    ids=[c["id"] for c in _NORMAL_CASES]
)
def test_log_parser_behaviour(case):
    """
    WHAT IS BEING TESTED: LogParser parse_line() and parse_file() accuracy
    EXPECTED BEHAVIOUR: Valid lines parse to LogEntry with correct node_id
        Invalid lines return None
        parse_file() returns non-empty list
    DATA SOURCE: tests/test_data/log_line_cases.json
    """
    # Arrange
    parser = LogParser()

    if case["from_file"]:
        # Act
        log_path = str(
            Path(__file__).parent.parent.parent / "logs" / "network_test_run_001.log"
        )
        entries = parser.parse_file(log_path)

        # Assert
        assert isinstance(entries, list), \
            f"[{case['id']}] {case['description']}\n" \
            f"Expected list but got {type(entries)}"
        assert len(entries) > 0, \
            f"[{case['id']}] {case['description']}\n" \
            f"Expected non-empty list but got empty list"

    elif case["expected_valid"]:
        # Act
        entry = parser.parse_line(case["line"])

        # Assert valid
        assert entry is not None, \
            f"[{case['id']}] {case['description']}\n" \
            f"Expected a LogEntry but got None"
        assert entry.node_id == case["expected_node_id"], \
            f"[{case['id']}] {case['description']}\n" \
            f"Expected node_id: {case['expected_node_id']}\n" \
            f"Actual node_id:   {entry.node_id}"

    else:
        # Act
        entry = parser.parse_line(case["line"])

        # Assert invalid
        assert entry is None, \
            f"[{case['id']}] {case['description']}\n" \
            f"Expected None for invalid line but got {entry}"


@pytest.mark.bug
@pytest.mark.parametrize(
    "case",
    _BUG_CASES,
    ids=[c["id"] for c in _BUG_CASES]
)
def test_log_parser_behaviour_bug(case):
    """
    WHAT IS BEING TESTED: parse_file() error handling for missing file
    EXPECTED BEHAVIOUR: Should handle missing file gracefully
        return empty list or raise clear error — not crash!
    ACTUAL BEHAVIOUR (bug): Raises unhandled FileNotFoundError
        with no meaningful error message to the caller
    BUG: Bug #11 - log_parser.py parse_file()
    DATA SOURCE: tests/test_data/log_line_cases.json
    """
    # Arrange
    parser = LogParser()

    # Act & Assert
    try:
        entries = parser.parse_file("logs/this_file_does_not_exist.log")
        assert entries == [], \
            f"[{case['id']}] {case['description']}\n" \
            f"Expected empty list for missing file but got {entries}"
    except FileNotFoundError:
        pytest.fail(
            f"[{case['id']}] {case['description']}\n"
            f"Bug: parse_file() raises unhandled FileNotFoundError "
            f"— should handle missing file gracefully not crash!"
        )