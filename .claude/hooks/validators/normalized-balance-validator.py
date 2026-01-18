#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pandas"]
# ///
"""
Balance Validator for Normalized CSV Files

Validates that balances are mathematically consistent in normalized_*.csv files.
Starting from the oldest (bottom) row, each subsequent row's balance should equal:
    previous_balance - withdrawal + deposit

Only validates normalized_*.csv files (not raw or merged files).

Outputs JSON decision for Claude Code Stop hook:
- {"decision": "block", "reason": "..."} to block and retry
- {} to allow completion
"""
import json
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

# Default operations directory
ROOT_OPERATIONS_DIR = Path("apps/agentic-finance-review/data/mock_dataset_2026")

# Log file in same directory as this script
LOG_FILE = Path(__file__).parent / "normalized-balance-validator.log"


def log(message: str):
    """Append timestamped message to log file."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")


def is_normalized_csv(file_path: Path) -> bool:
    """Check if file is a normalized CSV that requires balance validation."""
    name = file_path.name.lower()
    return name.startswith("normalized_")


def parse_numeric(val) -> float:
    """Parse a numeric value, handling empty/NaN as 0."""
    if pd.isna(val) or val == "":
        return 0.0
    return float(str(val).replace(",", "").replace("$", ""))


def validate_balance_consistency(file_path: Path) -> list[str]:
    """
    Validate balance consistency in a normalized CSV.

    The CSV is ordered newest-to-oldest (top-to-bottom).
    Starting from the bottom (oldest), each row going up should have:
        balance = previous_row_balance - current_withdrawal + current_deposit
    """
    errors = []

    if not file_path.exists():
        return [f"File not found: {file_path}"]

    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        return [f"Failed to parse CSV {file_path.name}: {e}"]

    # Check required columns exist
    required = ["date", "deposit", "withdrawal", "balance"]
    missing = [col for col in required if col not in df.columns]
    if missing:
        return [f"{file_path.name}: Missing columns for balance validation: {missing}"]

    if len(df) < 2:
        # Need at least 2 rows to validate balance progression
        return []

    # Parse all values upfront
    try:
        deposits = [parse_numeric(v) for v in df["deposit"]]
        withdrawals = [parse_numeric(v) for v in df["withdrawal"]]
        balances = [parse_numeric(v) for v in df["balance"]]
        dates = list(df["date"])
    except Exception as e:
        return [f"{file_path.name}: Error parsing numeric values: {e}"]

    # Validate from bottom (oldest) to top (newest)
    # Index len-1 is oldest, index 0 is newest
    error_count = 0
    max_errors = 5  # Limit error output

    for i in range(len(df) - 2, -1, -1):  # Start from second-to-last, go up to 0
        prev_idx = i + 1  # Previous row (older, lower in file)
        curr_idx = i      # Current row (newer, higher in file)

        prev_balance = balances[prev_idx]
        curr_deposit = deposits[curr_idx]
        curr_withdrawal = withdrawals[curr_idx]
        curr_balance = balances[curr_idx]

        expected_balance = prev_balance - curr_withdrawal + curr_deposit

        # Allow small floating point tolerance
        if abs(expected_balance - curr_balance) > 0.01:
            error_count += 1
            if error_count <= max_errors:
                errors.append(
                    f"{file_path.name} row {curr_idx + 2} (date: {dates[curr_idx]}): "
                    f"Balance mismatch!\n"
                    f"    Expected: ${expected_balance:,.2f} = "
                    f"${prev_balance:,.2f} (prev balance) - ${curr_withdrawal:,.2f} (withdrawal) + ${curr_deposit:,.2f} (deposit)\n"
                    f"    Actual:   ${curr_balance:,.2f}\n"
                    f"    Fix: Set balance to ${expected_balance:,.2f} or check withdrawal/deposit values"
                )

    if error_count > max_errors:
        errors.append(f"... and {error_count - max_errors} more balance errors in {file_path.name}")

    return errors


def validate_directory(dir_path: Path) -> list[str]:
    """Validate all normalized CSV files in a directory."""
    errors = []

    if not dir_path.exists():
        log(f"  ✗ Directory not found: {dir_path}")
        return [f"Directory not found: {dir_path}"]

    # Find all normalized CSV files recursively
    csv_files = list(dir_path.glob("**/normalized_*.csv"))
    log(f"  Found {len(csv_files)} normalized CSV files")

    if not csv_files:
        log("  (no normalized CSV files to validate)")
        return []

    for csv_file in csv_files:
        rel_path = csv_file.relative_to(dir_path) if csv_file.is_relative_to(dir_path) else csv_file
        file_errors = validate_balance_consistency(csv_file)
        if file_errors:
            log(f"  ✗ {rel_path}: {len(file_errors)} balance errors")
        else:
            log(f"  ✓ {rel_path}: balance validated")
        errors.extend(file_errors)

    return errors


def main():
    log("=" * 50)
    log("NORMALIZED BALANCE VALIDATOR STOP HOOK TRIGGERED")
    log(f"sys.argv: {sys.argv}")

    # Read hook input from stdin
    try:
        stdin_data = sys.stdin.read()
        log(f"stdin_data length: {len(stdin_data)}")
    except Exception:
        pass

    # Get target from command line arg, default to ROOT_OPERATIONS_DIR
    if len(sys.argv) > 1:
        target = Path(sys.argv[1])
        log(f"Target (from arg): {target}")
    else:
        target = ROOT_OPERATIONS_DIR
        log(f"Target (default): {target}")

    # Validate based on target type
    if target.is_file():
        if is_normalized_csv(target):
            log(f"Validating single file: {target}")
            errors = validate_balance_consistency(target)
        else:
            log(f"Skipping non-normalized file: {target}")
            errors = []
    elif target.is_dir():
        log(f"Validating directory: {target}")
        errors = validate_directory(target)
    else:
        errors = [f"Target not found: {target}"]
        log(f"✗ Target not found: {target}")

    # Output decision JSON
    if errors:
        log(f"RESULT: BLOCK ({len(errors)} errors)")
        for err in errors[:10]:  # Log first 10
            log(f"  ✗ {err}")
        print(json.dumps({
            "decision": "block",
            "reason": "Balance validation failed:\n" + "\n".join(errors)
        }))
    else:
        log("RESULT: PASS - Balance validation successful")
        print(json.dumps({}))


if __name__ == "__main__":
    main()
