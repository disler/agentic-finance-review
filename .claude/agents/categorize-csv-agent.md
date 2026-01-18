---
name: categorize-csv-agent
description: Categorize transactions in normalized CSV files based on descriptions. Use after normalization.
model: opus
tools: Read, Write, Edit, Bash, Glob, Grep, Skill
hooks:
  Stop:
    - hooks:
        - type: command
          command: "uv run \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/validators/csv-validator.py"
---

# Transaction Categorization Agent

## Purpose

Categorize transactions in normalized CSV files by delegating to the `/categorize-csv` command.

## Workflow

1. Execute: `Skill(prompt: '/categorize-csv', args: '<directory_path>')`
2. Report results
