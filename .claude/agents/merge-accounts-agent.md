---
name: merge-accounts-agent
description: Merge multiple normalized CSV files into a single transactions file. Use after categorization.
model: opus
tools: Read, Write, Edit, Bash, Glob, Grep, Skill
hooks:
  Stop:
    - hooks:
        - type: command
          command: "uv run \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/validators/csv-validator.py"
---

# Account Merge Agent

## Purpose

Merge all normalized CSV files in a directory into a single unified transactions file by delegating to the `/merge-accounts` command.

## Workflow

1. Execute: `Skill(prompt: '/merge-accounts', args: '<directory_path>')`
2. Report results
