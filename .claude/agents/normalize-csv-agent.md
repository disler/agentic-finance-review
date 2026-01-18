---
name: normalize-csv-agent
description: Normalize raw bank CSV exports into standardized format. Use when processing raw_*.csv files.
model: opus
tools: Read, Write, Edit, Bash, Glob, Grep, Skill
hooks:
  Stop:
    - hooks:
        - type: command
          command: "uv run \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/validators/csv-validator.py"
        - type: command
          command: "uv run \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/validators/normalized-balance-validator.py"
---

# CSV Normalization Agent

## Purpose

Transform all raw bank CSV exports in a directory into standardized normalized format by delegating to the `/normalize-csv` command.

## Workflow

1. Find all `raw_*.csv` files in the provided directory
2. For each raw CSV file, execute: `Skill(prompt: '/normalize-csv', args: '<file_path>')`
3. Report results
