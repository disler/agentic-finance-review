---
description: Accumulate monthly merged transactions into a cumulative yearly dataset
argument-hint: <month-dir>
hooks:
  Stop:
    - hooks:
        - type: command
          command: "uv run \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/validators/csv-validator.py"
---

# Accumulate CSVs Command

Roll a new month's merged transactions into the cumulative yearly dataset.

## Variables
ROOT_OPERATIONS_DIR: CLAUDE.md: ROOT_OPERATIONS_DIR

## Arguments
- `$ARGUMENTS`: Month directory path (e.g., `ROOT_OPERATIONS_DIR/mock_dataset_jan_1st_2026`)

## Input
- New month's merged file: `<new-dir>/agentic_merged_transactions.csv`
- Existing cumulative (if exists): `ROOT_OPERATIONS_DIR/agentic_cumulative_dataset_2026.csv`

## Output
- Updated cumulative file: `ROOT_OPERATIONS_DIR/agentic_cumulative_dataset_2026.csv`

## Accumulation Rules

### First Month
If cumulative doesn't exist:
1. Copy the new month's merged transactions
2. Create agentic_cumulative_dataset_2026.csv

### Subsequent Months
1. Read existing cumulative file
2. Read new month's merged transactions
3. Verify no date overlap (warn if found)
4. Concatenate new month's data
5. Sort by date descending
6. Write updated cumulative

### Date Validation
- New month's dates should not overlap with existing cumulative
- Warn if there's a gap between months (missing data?)
- All dates should be within 2026

### Duplicate Prevention
- Check for exact duplicate rows before merging
- Warn if duplicates found (same date, description, amount, account)

## Output Location
```
ROOT_OPERATIONS_DIR/
├── agentic_cumulative_dataset_2026.csv  <- Updated here
├── mock_dataset_jan_1st_2026/
│   └── agentic_merged_transactions.csv
└── mock_dataset_feb_1st_2026/
    └── agentic_merged_transactions.csv
```

## Workflow

1. Parse new directory path from `$ARGUMENTS`
2. Read the new month's agentic_merged_transactions.csv
3. Check if cumulative exists in parent directory
4. If exists, merge with existing data
5. Sort combined data by date descending
6. Write to agentic_cumulative_dataset_2026.csv
7. Stop hook validates the cumulative file

## Example
```
/accumulate-csvs ROOT_OPERATIONS_DIR/mock_dataset_feb_1st_2026
```
This adds February's transactions to the cumulative dataset.
