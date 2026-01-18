#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Demo Validator for showcasing Claude Code Stop hook functionality.

Logs all inputs and demonstrates the block/retry pattern:
- Pass 'fail:<message>' to trigger a one-time failure with <message> as feedback
- Subsequent runs with the same message will pass (tracks state in .demo-validator-state)

Usage:
  uv run .claude/hooks/validators/demo-validator.py "hello world"     # passes
  uv run .claude/hooks/validators/demo-validator.py "fail:fix this"   # fails once, then passes

Outputs JSON decision for Claude Code Stop hook:
- {"decision": "block", "reason": "..."} to block and retry
- {} to allow completion
"""
import json
import sys
from datetime import datetime
from pathlib import Path

LOG_FILE = Path(__file__).parent / "demo-validator.log"
STATE_FILE = Path(__file__).parent / ".demo-validator-state"


def log(message: str):
    """Append timestamped message to log file."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")


def get_failed_messages() -> set[str]:
    """Load messages that have already failed once."""
    if STATE_FILE.exists():
        return set(STATE_FILE.read_text().strip().split("\n"))
    return set()


def mark_as_failed(message: str):
    """Mark a message as having failed (so it passes next time)."""
    failed = get_failed_messages()
    failed.add(message)
    STATE_FILE.write_text("\n".join(failed))


def main():
    log("=" * 50)
    log("DEMO VALIDATOR STOP HOOK TRIGGERED")

    # Read hook input from stdin
    try:
        stdin_data = sys.stdin.read()
        if stdin_data.strip():
            hook_input = json.loads(stdin_data)
            log(f"stdin hook_input keys: {list(hook_input.keys())}")
            log(f"stdin hook_input value: {hook_input}")
        else:
            hook_input = {}
            log("stdin: (empty)")
    except json.JSONDecodeError:
        hook_input = {}
        log("stdin: (invalid JSON)")

    # Log command line arguments
    log(f"sys.argv: {sys.argv}")

    # Get the argument passed to the validator
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        log(f"Argument received: {arg}")
    else:
        arg = ""
        log("Argument: (none)")

    # Check for fail: prefix
    if arg.startswith("fail:"):
        feedback = arg[5:]  # Everything after 'fail:'
        log(f"Detected 'fail:' prefix with message: {feedback}")

        # Check if we've already failed this message
        failed_messages = get_failed_messages()
        if arg in failed_messages:
            log(f"Already failed once for this message - PASSING this time")
            log("RESULT: PASS (retry after previous failure)")
            print(json.dumps({}))
        else:
            # First time seeing this - fail and record it
            mark_as_failed(arg)
            log(f"First failure for this message - BLOCKING")
            log(f"RESULT: BLOCK")
            log(f"  Feedback: {feedback}")
            print(json.dumps({"decision": "block", "reason": feedback}))
    else:
        log("No 'fail:' prefix - passing")
        log("RESULT: PASS")
        print(json.dumps({}))


if __name__ == "__main__":
    main()
