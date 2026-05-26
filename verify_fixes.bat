@echo off
REM ============================================================
REM  Wirepas Mesh Network — Bug Verification Script
REM
REM  STEP 1 — Run against the ORIGINAL buggy code.
REM           Expected: 11 tests FAIL  (bugs confirmed to exist)
REM
REM  STEP 2 — Run against the FIXED code (auto-swap + restore).
REM           Expected:  0 tests FAIL  (all bugs confirmed fixed)
REM ============================================================

echo.
echo ============================================================
echo  STEP 1: Testing ORIGINAL code (bugs should be visible)
echo  Command: python -m pytest tests/ -v
echo  Expected: 11 FAILED (one per bug test)
echo ============================================================
echo.

python -m pytest tests/ -v

echo.
echo ============================================================
echo  STEP 2: Testing FIXED code (all bugs should be resolved)
echo  Command: python run_fixed_tests.py
echo  Expected: 0 FAILED
echo ============================================================
echo.

python run_fixed_tests.py

echo.
echo ============================================================
echo  Done. Compare STEP 1 vs STEP 2 to see the difference.
echo ============================================================
echo.
pause
