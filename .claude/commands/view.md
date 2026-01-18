---
model: haiku
description: View Dashboard
argument-hint: <month|year>
allowed-tools: Bash
---

# View Dashboard

## Purpose

Open a finance dashboard in Chrome.

## Arguments
- `$ARGUMENTS`: Date in natural language (e.g., "feb", "january 2026", "2026")

## Variables
ROOT_OPERATIONS_DIR: CLAUDE.md: ROOT_OPERATIONS_DIR

## Workflow

1. Parse the argument:
   - If just a year (e.g., "2026"): Open ROOT_OPERATIONS_DIR/index.html (cumulative yearly view)
   - If month specified (e.g., "feb", "january 2026"): Find matching `mock_dataset_{month}_1st_{year}/index.html`
2. Open in Chrome: `open -a "Google Chrome" <path>/index.html`

## Examples
```
/view 2026          # Opens yearly cumulative dashboard
/view feb           # Opens February dashboard
/view january 2026  # Opens January 2026 dashboard
```
