import pytest

from mesh_simulator.log_parser import LogParser


@pytest.mark.regression
@pytest.mark.positive
def test_filter_by_node_returns_only_that_nodes_entries(parsed_log_entries):
    """
    WHAT IS BEING TESTED: filter_by_node() filtering accuracy
    EXPECTED BEHAVIOUR: Should return only entries for node
        0x001A (decimal 26) — not entries from any other node
    """
    # Arrange — parsed_log_entries fixture provides real log entries
    parser = LogParser()

    # Act
    filtered = parser.filter_by_node(parsed_log_entries, 26)

    # Assert
    assert len(filtered) > 0, \
        f"Expected entries for node 26 but got none"
    assert all(e.node_id == 26 for e in filtered), \
        f"Expected all entries node_id 26 but found other nodes"


@pytest.mark.regression
@pytest.mark.positive
def test_filter_by_level_returns_only_matching_level(parsed_log_entries):
    """
    WHAT IS BEING TESTED: filter_by_level() filtering accuracy
    EXPECTED BEHAVIOUR: Should return only ERROR level entries
        not INFO, WARN or DEBUG entries
    """
    # Arrange — parsed_log_entries fixture provides real log entries
    parser = LogParser()

    # Act
    filtered = parser.filter_by_level(parsed_log_entries, "ERROR")

    # Assert
    assert len(filtered) > 0, \
        f"Expected ERROR entries but got none"
    assert all(e.level == "ERROR" for e in filtered), \
        f"Expected all entries ERROR but found other levels"