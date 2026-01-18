---
description: Merge normalized CSV files from multiple accounts into a single transactions file
argument-hint: <month-dir>
hooks:
  Stop:
    - hooks:
        - type: command
          command: "uv run \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/validators/csv-validator.py"
---

# Merge Accounts Command

Merge all normalized_*.csv files in a directory into a single agentic_merged_transactions.csv.

## Variables
ROOT_OPERATIONS_DIR: CLAUDE.md: ROOT_OPERATIONS_DIR

## Arguments
- `$ARGUMENTS`: Month directory path (e.g., `ROOT_OPERATIONS_DIR/mock_dataset_jan_1st_2026`)

## Input
Multiple normalized CSV files in the directory:
- normalized_checkings.csv
- normalized_savings.csv
- etc.

## Output
Single merged file: `agentic_merged_transactions.csv`

## Merge Rules

### Combining Records
1. Read all normalized_*.csv files in the directory
2. Concatenate all records
3. Sort by date (descending - newest first)
4. Preserve account_name to track source

### Date Ordering
- All transactions sorted by date descending
- When dates match, preserve original order within each account
- Verify no date gaps (warn if unusual gaps detected)

### Balance Handling
- Each row keeps its original balance from source account
- Do NOT recalculate balances across accounts
- Balance represents account-specific balance at that time

### Duplicate Detection
- Warn about potential duplicates (same date, amount, description across accounts)
- Do NOT auto-remove - transfers between accounts look like duplicates but aren't

## Output Format
Same normalized format:
```csv
date,description,category,deposit,withdrawal,balance,account_name
2026-01-31,Paycheck Deposit,income,5000.00,,45000.00,checkings
2026-01-31,Transfer to Savings,transfers,,1000.00,44000.00,checkings
2026-01-31,Transfer from Checkings,transfers,1000.00,,15000.00,savings
```

## Workflow

1. Read directory path from `$ARGUMENTS`
2. Find all normalized_*.csv files
3. Read and validate each file
4. Concatenate all DataFrames
5. Sort by date descending
6. Write to agentic_merged_transactions.csv
7. Stop hook validates the output

## Validation
The csv-validator.py Stop hook will verify:
- All required columns present
- Date format correct
- Numeric columns valid
- File not empty
