import pytest

from mesh_simulator.log_parser import LogParser


@pytest.mark.smoke
@pytest.mark.regression
@pytest.mark.positive
def test_detect_reboot_loops_identifies_stuck_node(parsed_log_entries):
    """
    WHAT IS BEING TESTED: detect_reboot_loops() detection accuracy
    EXPECTED BEHAVIOUR: Should identify node 0x0020 (decimal 32)
        as stuck in reboot loop — rebooted 4 times within 60 seconds
    """
    # Arrange — parsed_log_entries fixture provides real log entries
    parser = LogParser()

    # Act
    looping_nodes = parser.detect_reboot_loops(parsed_log_entries)

    # Assert
    assert 32 in looping_nodes, \
        f"Expected node 32 (0x0020) in reboot loops but got {looping_nodes}"


@pytest.mark.regression
@pytest.mark.negative
def test_detect_reboot_loops_does_not_flag_stable_nodes(parsed_log_entries):
    """
    WHAT IS BEING TESTED: detect_reboot_loops() false positive check
    EXPECTED BEHAVIOUR: Stable nodes that booted once and stayed
        online should NOT appear in reboot loop detection results
    """
    # Arrange — parsed_log_entries fixture provides real log entries
    parser = LogParser()

    # Act
    looping_nodes = parser.detect_reboot_loops(parsed_log_entries)

    # Assert
    assert 26 not in looping_nodes, \
        f"Expected node 26 (0x001A) NOT in reboot loops but found it!"
    assert 27 not in looping_nodes, \
        f"Expected node 27 (0x001B) NOT in reboot loops but found it!"