---
model: opus
description: Execute a prompt and build the requested feature.
argument-hint: <prompt>
hooks:
  Stop:
    - hooks:
        - type: command
          command: "uv run \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/validators/ty-validator.py"
        - type: command
          command: "uv run \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/validators/ruff-validator.py"
---

# Build Command

## Purpose

Execute a user prompt and build the requested feature.

## Variables

USER_PROMPT: $ARGUMENTS

## Instructions

- Execute the user's prompt as the primary task
- Focus on writing clean, well-typed Python code
- If validation fails, fix the issues and try again

## Workflow

1. Read and understand the USER_PROMPT
2. Execute the requested task
3. Ensure any code written follows Python best practices
4. Report the results of your work

## Report

After completing the task:

## Build Complete

**Task**: [brief summary of what was done]

**Files modified**: [list of files]
