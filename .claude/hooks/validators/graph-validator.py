#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Graph Validator for Agentic Finance Review

Validates that PNG graph files have been generated in the assets/ directory.
Checks recursively for assets/ directories containing at least one PNG file.

Outputs JSON decision for Claude Code Stop hook:
- {"decision": "block", "reason": "..."} to block and retry
- {} to allow completion
"""
import json
import sys
from datetime import datetime
from pathlib import Path

# Default operations directory - used when no argument provided
ROOT_OPERATIONS_DIR = Path("apps/agentic-finance-review/data/mock_dataset_2026")

# Log file in same directory as this script
LOG_FILE = Path(__file__).parent / "graph-validator.log"

MIN_GRAPHS = 5  # Expect at least 5 required graphs


def log(message: str):
    """Append timestamped message to log file."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")


def validate_graphs(dir_path: Path) -> list[str]:
    """Validate that PNG files exist in assets/ directories."""
    errors = []

    if not dir_path.exists():
        log(f"  ✗ Directory not found: {dir_path}")
        return [f"Directory not found: {dir_path}"]

    # Find all assets directories
    assets_dirs = [d for d in dir_path.rglob("assets") if d.is_dir()]
    log(f"  Found {len(assets_dirs)} assets/ directories")

    if not assets_dirs:
        # No assets directories - nothing to validate, pass
        log("  (no assets/ directories to validate)")
        return []

    # Check each assets directory
    for assets_dir in assets_dirs:
        pngs = list(assets_dir.glob("*.png"))
        rel_path = assets_dir.relative_to(dir_path) if assets_dir.is_relative_to(dir_path) else assets_dir

        if len(pngs) < MIN_GRAPHS:
            log(f"  ✗ {rel_path}: {len(pngs)} PNGs, expected at least {MIN_GRAPHS}")
            errors.append(f"{rel_path}: Found {len(pngs)} PNG files, expected at least {MIN_GRAPHS}")
        else:
            log(f"  ✓ {rel_path}: {len(pngs)} PNGs")
            for png in pngs:
                log(f"    ✓ {png.name}")

    return errors


def main():
    log("=" * 50)
    log("GRAPH VALIDATOR STOP HOOK TRIGGERED")

    # Read hook input from stdin (Claude Code passes JSON)
    try:
        stdin_data = sys.stdin.read()
        if stdin_data.strip():
            hook_input = json.loads(stdin_data)
            log(f"hook_input keys: {list(hook_input.keys())}")
        else:
            hook_input = {}
    except json.JSONDecodeError:
        hook_input = {}

    # Get target from command line arg, default to ROOT_OPERATIONS_DIR
    if len(sys.argv) > 1:
        target = Path(sys.argv[1])
        log(f"Target (from arg): {target}")
    else:
        target = ROOT_OPERATIONS_DIR
        log(f"Target (default): {target}")

    log(f"Validating graphs in: {target}")
    errors = validate_graphs(target)

    # Output decision JSON
    if errors:
        log(f"RESULT: BLOCK ({len(errors)} errors)")
        for err in errors:
            log(f"  ✗ {err}")
        print(json.dumps({
            "decision": "block",
            "reason": "Graph validation failed:\n" + "\n".join(errors)
        }))
    else:
        log("RESULT: PASS - Graph validation successful")
        print(json.dumps({}))


if __name__ == "__main__":
    main()
