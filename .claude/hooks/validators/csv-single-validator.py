#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pandas"]
# ///
"""
Single CSV Validator for PostToolUse Hook

Validates a single CSV file after Edit|Write operations.
Reads the file path from the PostToolUse hook input JSON.

For any .csv file:
- Validates CSV can be parsed
- Validates not empty

For normalized_*.csv files (additional checks):
- Validates required columns exist
- Validates balance consistency (prev_balance - withdrawal + deposit = current_balance)

Outputs JSON decision for Claude Code hook:
- {"decision": "block", "reason": "..."} to block and retry
- {} to allow completion
"""
import json
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

LOG_FILE = Path(__file__).parent / "csv-single-validator.log"


def log(message: str):
    """Append timestamped message to log file."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")


def parse_numeric(val) -> float:
    """Parse a numeric value, handling empty/NaN as 0."""
    if pd.isna(val) or val == "":
        return 0.0
    return float(str(val).replace(",", "").replace("$", ""))


def is_normalized_csv(file_path: Path) -> bool:
    """Check if file is a normalized CSV that requires full validation."""
    name = file_path.name.lower()
    return name.startswith("normalized_")


def validate_csv_parseable(file_path: Path) -> list[str]:
    """Validate that a CSV file can be parsed and is not empty."""
    errors = []

    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        return [f"Failed to parse CSV {file_path.name}: {e}"]

    if len(df) == 0:
        errors.append(f"{file_path.name}: CSV file is empty")

    if len(df.columns) == 0:
        errors.append(f"{file_path.name}: CSV has no columns")

    return errors


def validate_normalized_csv(file_path: Path) -> list[str]:
    """Validate a normalized CSV file with column and balance checks."""
    errors = []

    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        return [f"Failed to parse CSV {file_path.name}: {e}"]

    # Check required columns
    required_columns = [
        "date",
        "description",
        "category",
        "deposit",
        "withdrawal",
        "balance",
        "account_name",
    ]
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        errors.append(f"{file_path.name}: Missing required columns: {missing}")
        return errors

    if len(df) < 2:
        return errors  # Need at least 2 rows for balance validation

    # Parse values for balance validation
    try:
        deposits = [parse_numeric(v) for v in df["deposit"]]
        withdrawals = [parse_numeric(v) for v in df["withdrawal"]]
        balances = [parse_numeric(v) for v in df["balance"]]
        dates = list(df["date"])
    except Exception as e:
        errors.append(f"{file_path.name}: Error parsing numeric values: {e}")
        return errors

    # Validate balance consistency (bottom to top)
    error_count = 0
    max_errors = 3

    for i in range(len(df) - 2, -1, -1):
        prev_idx = i + 1
        curr_idx = i

        prev_balance = balances[prev_idx]
        curr_deposit = deposits[curr_idx]
        curr_withdrawal = withdrawals[curr_idx]
        curr_balance = balances[curr_idx]

        expected_balance = prev_balance - curr_withdrawal + curr_deposit

        if abs(expected_balance - curr_balance) > 0.01:
            error_count += 1
            if error_count <= max_errors:
                errors.append(
                    f"{file_path.name} row {curr_idx + 2} (date: {dates[curr_idx]}): "
                    f"Balance mismatch! Expected ${expected_balance:,.2f}, got ${curr_balance:,.2f}"
                )

    if error_count > max_errors:
        errors.append(f"... and {error_count - max_errors} more balance errors")

    return errors


def main():
    log("=" * 50)
    log("CSV SINGLE VALIDATOR (PostToolUse)")
    log(f"sys.argv: {sys.argv}")

    # Read hook input from stdin
    file_path = None
    try:
        stdin_data = sys.stdin.read()
        log(f"stdin_data length: {len(stdin_data)}")
        if stdin_data.strip():
            hook_input = json.loads(stdin_data)
            log(f"hook_event: {hook_input.get('hook_event_name')}")
            log(f"tool_name: {hook_input.get('tool_name')}")

            # Get file path from tool_input
            tool_input = hook_input.get("tool_input", {})
            file_path = tool_input.get("file_path")
            log(f"file_path: {file_path}")
    except json.JSONDecodeError as e:
        log(f"JSON decode error: {e}")
    except Exception as e:
        log(f"Error reading stdin: {e}")

    # If no file path from stdin, check CLI arg
    if not file_path and len(sys.argv) > 1:
        file_path = sys.argv[1]
        log(f"file_path (from arg): {file_path}")

    if not file_path:
        log("No file path provided, skipping validation")
        print(json.dumps({}))
        return

    file_path = Path(file_path)

    # Only validate .csv files
    if file_path.suffix.lower() != ".csv":
        log(f"Skipping non-CSV file: {file_path.name}")
        print(json.dumps({}))
        return

    if not file_path.exists():
        log(f"File not found: {file_path}")
        print(
            json.dumps({"decision": "block", "reason": f"File not found: {file_path}"})
        )
        return

    # Validate the CSV
    log(f"Validating: {file_path.name}")
    errors = []

    # Basic parsing check for all CSVs
    parse_errors = validate_csv_parseable(file_path)
    errors.extend(parse_errors)

    # Additional checks for normalized CSVs
    if is_normalized_csv(file_path) and not parse_errors:
        log("  Running normalized CSV validation (columns + balance)")
        normalized_errors = validate_normalized_csv(file_path)
        errors.extend(normalized_errors)

    # Output result
    if errors:
        log(f"RESULT: BLOCK ({len(errors)} errors)")
        for err in errors:
            log(f"  ✗ {err}")
        print(
            json.dumps(
                {
                    "decision": "block",
                    "reason": f"Resolve this CSV error in {file_path.name}:\n"
                    + "\n".join(errors),
                }
            )
        )
    else:
        log(f"RESULT: PASS - {file_path.name} validated")
        print(json.dumps({}))


if __name__ == "__main__":
    main()
