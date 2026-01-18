#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Type Checker Validator for Claude Code Stop Hook

Runs `uvx ty check` for type checking and logs results.

Outputs JSON decision for Claude Code Stop hook:
- {"decision": "block", "reason": "..."} to block and retry
- {} to allow completion
"""
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

LOG_FILE = Path(__file__).parent / "ty-validator.log"


def log(message: str):
    """Append timestamped message to log file."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")


def main():
    log("=" * 50)
    log("TY VALIDATOR STOP HOOK TRIGGERED")

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

    # Run uvx ty check
    log("Running: uvx ty check")
    try:
        result = subprocess.run(
            ["uvx", "ty", "check"],
            capture_output=True,
            text=True,
            timeout=120
        )

        stdout = result.stdout.strip()
        stderr = result.stderr.strip()

        if stdout:
            for line in stdout.split('\n')[:20]:  # Limit log lines
                log(f"  {line}")

        if result.returncode == 0:
            log("RESULT: PASS - Type check successful")
            print(json.dumps({}))
        else:
            log(f"RESULT: BLOCK (exit code {result.returncode})")
            if stderr:
                for line in stderr.split('\n')[:10]:
                    log(f"  ✗ {line}")
            error_output = stderr or stdout or "Type check failed"
            print(json.dumps({
                "decision": "block",
                "reason": f"Type check failed:\n{error_output[:500]}"
            }))

    except subprocess.TimeoutExpired:
        log("RESULT: BLOCK (timeout)")
        print(json.dumps({
            "decision": "block",
            "reason": "Type check timed out after 120 seconds"
        }))
    except FileNotFoundError:
        log("RESULT: PASS (uvx ty not found, skipping)")
        print(json.dumps({}))


if __name__ == "__main__":
    main()
