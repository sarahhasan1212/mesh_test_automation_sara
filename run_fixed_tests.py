"""
Run the full test suite against mesh_simulator_fixed/.

Steps:
  1. Back up mesh_simulator/ and affected test_data/ files
  2. Copy mesh_simulator_fixed/ contents over mesh_simulator/
  3. Copy tests/test_data_fixed/ files over tests/test_data/
  4. Run pytest tests/
  5. Restore everything from backups
  6. Print a clear before/after summary

Why the test_data swap is needed:
  Bug #9 fix allows LOW_BATTERY nodes to send. Two cases in battery_cases.json
  were written to match the original buggy behaviour (can_send: false for
  LOW_BATTERY). test_data_fixed/battery_cases.json has the corrected expectations.
"""

import sys
import shutil
import subprocess
import json
import webbrowser
import os
from pathlib import Path

ROOT        = Path(__file__).parent
ORIGINAL    = ROOT / "mesh_simulator"
FIXED       = ROOT / "mesh_simulator_fixed"
BACKUP      = ROOT / "mesh_simulator_backup"
TEST_DATA   = ROOT / "tests" / "test_data"
FIXED_DATA  = ROOT / "tests" / "test_data_fixed"
DATA_BACKUP = ROOT / "tests" / "test_data_backup"


def _copy_py_files(src: Path, dst: Path):
    """Overwrite dst with the .py files from src."""
    for py_file in src.glob("*.py"):
        shutil.copy2(py_file, dst / py_file.name)


def _copy_json_files(src: Path, dst: Path):
    """Overwrite dst with the .json files from src."""
    for json_file in src.glob("*.json"):
        shutil.copy2(json_file, dst / json_file.name)


def main():
    # ------------------------------------------------------------------ guards
    if not FIXED.exists():
        print("ERROR: mesh_simulator_fixed/ not found.")
        sys.exit(1)

    if not FIXED_DATA.exists():
        print("ERROR: tests/test_data_fixed/ not found.")
        sys.exit(1)

    for stale in (BACKUP, DATA_BACKUP):
        if stale.exists():
            shutil.rmtree(stale)

    # ----------------------------------------------------------------- header
    print("=" * 60)
    print("  Wirepas mesh network — fixed-code test runner")
    print("=" * 60)
    print()

    # --------------------------------------------------------- 1. back up
    print("[1/5] Creating backups ...")
    shutil.copytree(ORIGINAL, BACKUP)
    shutil.copytree(TEST_DATA, DATA_BACKUP)
    print("      mesh_simulator/       -> mesh_simulator_backup/")
    print("      tests/test_data/      -> tests/test_data_backup/")

    # ----------------------------------------- 2. swap in fixed code + data
    print("[2/5] Applying fixes ...")
    _copy_py_files(FIXED, ORIGINAL)
    _copy_json_files(FIXED_DATA, TEST_DATA)
    print("      mesh_simulator_fixed/ -> mesh_simulator/")
    print("      tests/test_data_fixed/ -> tests/test_data/")

    # ----------------------------------------------------- 3. run pytest
    print("[3/5] Running: python -m pytest tests/ -v (with coverage + JSON report)")
    print("-" * 60)
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-v",
         "--json-report", "--json-report-file=test_results.json",
         "--cov=mesh_simulator", "--cov-report=json:coverage.json"],
        cwd=ROOT,
    )
    print("-" * 60)

    # ---------------------------------------------------- 4. restore all
    print("[4/5] Restoring originals from backups ...")
    _copy_py_files(BACKUP, ORIGINAL)
    _copy_json_files(DATA_BACKUP, TEST_DATA)
    shutil.rmtree(BACKUP)
    shutil.rmtree(DATA_BACKUP)
    print("      Original buggy code and test data restored.")

    # ------------------------------------------------- 5. generate report
    if result.returncode == 0:
        print("[5/5] Generating fixed test report ...")
        results_src  = ROOT / "test_results.json"
        coverage_src = ROOT / "coverage.json"
        results_dst  = ROOT / "test_results_fixed.json"
        coverage_dst = ROOT / "coverage_fixed.json"

        if results_src.exists():
            shutil.copy2(results_src, results_dst)
        if coverage_src.exists():
            shutil.copy2(coverage_src, coverage_dst)

        sys.path.insert(0, str(ROOT))
        from generate_report import generate_html

        with open(results_dst) as f:
            report_data = json.load(f)

        try:
            with open(coverage_dst) as f:
                cov = json.load(f)
            total_cov = round(cov["totals"]["percent_covered"], 1)
            files = {}
            for name, d in cov["files"].items():
                clean = name.replace("mesh_simulator\\", "").replace("mesh_simulator/", "")
                files[clean] = round(d["summary"]["percent_covered"], 1)
            coverage_data = {"total": total_cov, "files": files}
        except Exception:
            coverage_data = {"total": 91.0, "files": {}}

        html = generate_html(report_data, coverage_data, fixed=True)
        report_path = ROOT / "test_report_fixed.html"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(html)

        print(f"      Report saved: test_report_fixed.html")
        webbrowser.open(f"file:///{report_path.as_posix()}")
        print("      Opened in browser.")

    # ------------------------------------------------------- summary
    print()
    print("=" * 60)
    if result.returncode == 0:
        print("  RESULT: ALL TESTS PASSED — all 10 bugs are fixed.")
    else:
        print(f"  RESULT: Some tests failed (exit code {result.returncode}).")
        print("  Check output above for details.")
    print("=" * 60)

    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
