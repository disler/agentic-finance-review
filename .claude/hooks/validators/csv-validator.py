#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pandas"]
# ///
"""
CSV Validator for Agentic Finance Review

Validates CSV files in apps/agentic-finance-review/data/:

For normalized_*.csv and agentic_merged_transactions.csv files:
- Required columns: date, description, category, deposit, withdrawal, balance, account_name
- Date format: YYYY-MM-DD (ISO 8601)
- Numeric columns properly formatted
- account_name populated

For other CSV files (raw_*.csv, etc.):
- Valid CSV structure (can be parsed)
- Not empty

Outputs JSON decision for Claude Code Stop hook:
- {"decision": "block", "reason": "..."} to block and retry
- {} to allow completion
"""
import json
import sys
from pathlib import Path
from datetime import datetime

import pandas as pd

# Default operations directory - used when no argument provided
ROOT_OPERATIONS_DIR = Path("apps/agentic-finance-review/data/mock_dataset_2026")

# Log file in same directory as this script
LOG_FILE = Path(__file__).parent / "csv-validator.log"

REQUIRED_COLUMNS = [
    "date",
    "description",
    "category",
    "deposit",
    "withdrawal",
    "balance",
    "account_name",
]


def log(message: str):
    """Append timestamped message to log file."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")


def is_normalized_csv(file_path: Path) -> bool:
    """Check if file is a normalized CSV that requires full column validation."""
    name = file_path.name.lower()
    return name.startswith("normalized_") or name == "agentic_merged_transactions.csv"


def validate_csv_structure(file_path: Path) -> list[str]:
    """Validate basic CSV structure (can be parsed, not empty)."""
    errors = []

    if not file_path.exists():
        return [f"File not found: {file_path}"]

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
    """Validate a normalized CSV file with full column and format checking."""
    errors = []

    if not file_path.exists():
        return [f"File not found: {file_path}"]

    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        return [f"Failed to parse CSV {file_path.name}: {e}"]

    # Check required columns
    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        errors.append(f"{file_path.name}: Missing required columns: {missing_cols}")
        return errors  # Can't continue validation without required columns

    # Check for empty dataframe
    if len(df) == 0:
        errors.append(f"{file_path.name}: CSV file is empty")
        return errors

    # Validate date format (YYYY-MM-DD)
    date_errors = 0
    for idx, date_val in enumerate(df["date"]):
        try:
            datetime.strptime(str(date_val), "%Y-%m-%d")
        except ValueError:
            date_errors += 1
            if date_errors <= 3:
                errors.append(
                    f"{file_path.name} row {idx+1}: Invalid date format '{date_val}', expected YYYY-MM-DD"
                )
    if date_errors > 3:
        errors.append(
            f"{file_path.name}: ... and {date_errors - 3} more date format errors"
        )

    # Validate numeric columns
    for col in ["deposit", "withdrawal", "balance"]:
        col_errors = 0
        for idx, val in enumerate(df[col]):
            if pd.isna(val) or val == "":
                continue
            try:
                float(str(val).replace(",", "").replace("$", ""))
            except ValueError:
                col_errors += 1
                if col_errors <= 2:
                    errors.append(
                        f"{file_path.name} row {idx+1}: Invalid {col} value '{val}'"
                    )
        if col_errors > 2:
            errors.append(
                f"{file_path.name}: ... and {col_errors - 2} more {col} errors"
            )

    # Check account_name is populated
    if df["account_name"].isna().all() or (df["account_name"] == "").all():
        errors.append(f"{file_path.name}: account_name column is empty")

    return errors


def validate_csv(file_path: Path) -> list[str]:
    """Validate a CSV file - full validation for normalized, structure-only for others."""
    if is_normalized_csv(file_path):
        return validate_normalized_csv(file_path)
    else:
        return validate_csv_structure(file_path)


def validate_directory(dir_path: Path, recursive: bool = True) -> list[str]:
    """Validate all CSV files in a directory (optionally recursive)."""
    errors = []

    if not dir_path.exists():
        log(f"  ✗ Directory not found: {dir_path}")
        return [f"Directory not found: {dir_path}"]

    # Use recursive glob to find all CSV files
    pattern = "**/*.csv" if recursive else "*.csv"
    csv_files = list(dir_path.glob(pattern))
    log(f"  Found {len(csv_files)} CSV files {'(recursive)' if recursive else ''}")

    if not csv_files:
        # No CSV files is not an error - might be running before files are created
        log("  (no CSV files to validate)")
        return []

    normalized_count = 0
    other_count = 0

    for csv_file in csv_files:
        # Show relative path for clarity
        rel_path = (
            csv_file.relative_to(dir_path)
            if csv_file.is_relative_to(dir_path)
            else csv_file
        )
        file_errors = validate_csv(csv_file)
        if file_errors:
            log(f"  ✗ {rel_path}: {len(file_errors)} errors")
        else:
            log(f"  ✓ {rel_path}")
        errors.extend(file_errors)
        if is_normalized_csv(csv_file):
            normalized_count += 1
        else:
            other_count += 1

    log(f"  Summary: {normalized_count} normalized, {other_count} other")
    return errors


def main():
    log("=" * 50)
    log("CSV VALIDATOR STOP HOOK TRIGGERED")
    log(f"sys.argv: {sys.argv}")

    # Check if a direct CSV file path was passed
    direct_csv = None
    if len(sys.argv) > 1:
        target = Path(sys.argv[1])
        if target.suffix.lower() == ".csv" and target.is_file():
            direct_csv = target
            log(f"Direct CSV file mode: {direct_csv}")

    # Only read stdin if not in direct CSV mode
    if not direct_csv:
        try:
            stdin_data = sys.stdin.read()
            log(f"stdin_data length: {len(stdin_data)}")
            if stdin_data.strip():
                hook_input = json.loads(stdin_data)
                log(f"hook_input keys: {list(hook_input.keys())}")
                log(f"hook_input value: {hook_input}")
            else:
                hook_input = {}
                log("hook_input: (empty)")
        except json.JSONDecodeError as e:
            hook_input = {}
            log(f"JSON decode error: {e}")

    # Validate based on mode
    if direct_csv:
        # Direct CSV file mode - validate just this one file
        log(f"Validating single file: {direct_csv}")
        errors = validate_csv(direct_csv)
        if errors:
            log(f"  ✗ {direct_csv.name}: {len(errors)} errors")
        else:
            log(f"  ✓ {direct_csv.name}")
    elif len(sys.argv) > 1:
        # Directory or non-CSV file passed
        target = Path(sys.argv[1])
        log(f"Target (from arg): {target}")
        if target.is_dir():
            log(f"Validating directory: {target}")
            errors = validate_directory(target)
        elif target.is_file():
            # Non-CSV file - validate parent directory
            parent_dir = target.parent
            log(f"Validating directory (from file): {parent_dir}")
            errors = validate_directory(parent_dir)
        else:
            errors = [f"Target not found: {target}"]
            log(f"✗ Target not found: {target}")
    else:
        # No args - use default directory
        target = ROOT_OPERATIONS_DIR
        log(f"Target (default): {target}")
        if target.is_dir():
            log(f"Validating directory: {target}")
            errors = validate_directory(target)
        else:
            errors = [f"Target not found: {target}"]
            log(f"✗ Target not found: {target}")

    # Output decision JSON
    if errors:
        log(f"RESULT: BLOCK ({len(errors)} errors)")
        for err in errors:
            log(f"  ✗ {err}")
        print(
            json.dumps(
                {
                    "decision": "block",
                    "reason": "CSV validation failed:\n" + "\n".join(errors),
                }
            )
        )
    else:
        log("RESULT: PASS - CSV validation successful")
        print(json.dumps({}))


if __name__ == "__main__":
    main()
