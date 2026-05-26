import json
from pathlib import Path


def load_cases(filename):
    """
    Load test cases from JSON file in test_data folder.
    Used by all data-driven test files.
    """
    path = Path(__file__).parent / "test_data" / filename
    with open(path) as f:
        return json.load(f)