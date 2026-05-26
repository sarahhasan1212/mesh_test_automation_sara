"""
Log parser for mesh node serial output.
Parses structured log lines from node serial consoles.
"""

import re
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class LogEntry:
    timestamp: datetime
    node_id: int
    level: str  # INFO, WARN, ERROR, DEBUG
    component: str
    message: str
    raw_line: str


class LogParser:
    """
    Parses mesh node serial log files.

    Expected log format:
        [2025-01-15 08:30:01.123] NODE:0x001A LEVEL:INFO COMP:BOOT MSG:Node booted successfully
        [2025-01-15 08:30:01.456] NODE:0x001A LEVEL:WARN COMP:BATT MSG:Battery at 19%
    """

    LOG_PATTERN = re.compile(
        r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3})\] '
        r'NODE:0x([0-9A-Fa-f]+) '
        r'LEVEL:(\w+) '
        r'COMP:(\w+) '
        r'MSG:(.*)'
    )

    def parse_line(self, line: str) -> Optional[LogEntry]:
        """Parse a single log line. Returns None if the line doesn't match."""
        match = self.LOG_PATTERN.match(line.strip())
        if not match:
            return None

        timestamp_str, node_hex, level, component, message = match.groups()

        return LogEntry(
            timestamp=datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S.%f"),
            node_id=int(node_hex, 16),
            level=level,
            component=component,
            message=message.strip(),
            raw_line=line.strip(),
        )

    def parse_file(self, filepath: str) -> list[LogEntry]:
        """Parse an entire log file and return list of entries."""
        entries = []
        with open(filepath, 'r') as f:
            for line in f:
                entry = self.parse_line(line)
                if entry:
                    entries.append(entry)
        return entries

    def filter_by_node(self, entries: list[LogEntry], node_id: int) -> list[LogEntry]:
        """Filter entries for a specific node."""
        return [e for e in entries if e.node_id == node_id]

    def filter_by_level(self, entries: list[LogEntry], level: str) -> list[LogEntry]:
        """Filter entries by log level."""
        return [e for e in entries if e.level == level]

    def get_error_summary(self, entries: list[LogEntry]) -> dict:
        """
        Generate a summary of errors grouped by node and component.
        Returns: {node_id: {component: [error_messages]}}
        """
        summary = {}
        errors = self.filter_by_level(entries, "ERROR")

        for entry in errors:
            if entry.node_id not in summary:
                summary[entry.node_id] = {}
            if entry.component not in summary[entry.node_id]:
                summary[entry.node_id][entry.component] = []
            summary[entry.node_id][entry.component].append(entry.message)

        return summary

    def detect_reboot_loops(self, entries: list[LogEntry], threshold: int = 3,
                            window_seconds: int = 60) -> list[int]:
        """
        Detect nodes that are stuck in reboot loops.
        A reboot loop is defined as `threshold` or more boot events within
        `window_seconds` for the same node.

        Returns list of node_ids that are in reboot loops.
        """
        boot_events = [e for e in entries if e.component == "BOOT" and "booted" in e.message.lower()]

        nodes_boots: dict[int, list[datetime]] = {}
        for event in boot_events:
            nodes_boots.setdefault(event.node_id, []).append(event.timestamp)

        reboot_loop_nodes = []
        for node_id, timestamps in nodes_boots.items():
            timestamps.sort()
            for i in range(len(timestamps)):
                count = 1
                for j in range(i + 1, len(timestamps)):
                    delta = (timestamps[j] - timestamps[i]).total_seconds()
                    if delta <= window_seconds:
                        count += 1
                    else:
                        break
                if count >= threshold:
                    reboot_loop_nodes.append(node_id)
                    break

        return reboot_loop_nodes
