---
model: opus
description: Make modifications or report on csv files
argument-hint: [csv_file] [user_request]
allowed-tools: Glob, Grep, Read, Edit, Write
disable-model-invocation: false
hooks:
  PostToolUse:
    - matcher: "Read|Edit|Write"
      hooks:
        - type: command
          command: "uv run $CLAUDE_PROJECT_DIR/.claude/hooks/validators/csv-single-validator.py"
---

# Purpose

Make modifications or report on csv files.

## Workflow

1. Read the CSV File: $1
2. Make the modification or report: $2
3. Report the results
