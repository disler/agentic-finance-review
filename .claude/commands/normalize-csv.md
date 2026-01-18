---
description: Normalize a raw bank CSV export into our standard format
argument-hint: <raw_csv_file>
hooks:
  Stop:
    - hooks:
        - type: command
          command: "uv run \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/validators/csv-validator.py"
        - type: command
          command: "uv run \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/validators/normalized-balance-validator.py"
---

# Normalize CSV Command

Transform a single raw bank CSV export into our standardized normalized format.

## Variables
ROOT_OPERATIONS_DIR: CLAUDE.md: ROOT_OPERATIONS_DIR

## Arguments
- `$ARGUMENTS`: Path to a raw CSV file (e.g., `ROOT_OPERATIONS_DIR/mock_dataset_jan_1st_2026/raw_checkings.csv`)

## Input Format (Raw Bank Export)
Bank CSVs have varying formats:
```csv
Date,Description,Withdrawals,Deposits,Category,Balance
"01/31/2026","DEBIT CARD PURCHASE   XXXXX4291 Amazon Prime*KV2819YT5","$148.32","","Subscriptions","$42,156.78"
```

## Output Format (Normalized)
```csv
date,description,category,deposit,withdrawal,balance,account_name
2026-01-31,Amazon Prime Subscription,,148.32,,42156.78,checkings
```

## Normalization Rules

### Date Conversion
- Convert MM/DD/YYYY to YYYY-MM-DD (ISO 8601)
- Filter out transactions from previous months (keep only current month)

### Amount Parsing
- Remove $ symbols and commas
- Withdrawals go in withdrawal column
- Deposits go in deposit column
- Leave blank (not 0) if no value

### Description Cleaning
- Remove card numbers (XXXXX1234)
- Remove excess whitespace
- Clean up merchant names
- Keep essential transaction info

### Category (Leave Empty)
- Set category to empty string
- Categorization happens in the next step via categorize-csv-agent

### Account Name
- Extract from filename: raw_checkings.csv -> checkings
- raw_savings.csv -> savings

## Workflow

1. Read the CSV file path from `$ARGUMENTS`
2. Parse the bank-format CSV
3. Apply normalization rules
4. Filter to only include transactions from the target month (derive from parent directory name)
5. Write to normalized_<account>.csv in the same directory
6. The Stop hook will validate the output CSV

## Critical Requirements
- Dates MUST be in YYYY-MM-DD format
- Only include transactions from the target month (derive from directory name)
- Balance column must have numeric values (no $ or commas)
- category column should be empty (will be filled by categorize agent)
- account_name must be populated from the source filename

## Example
```
/normalize-csv ROOT_OPERATIONS_DIR/mock_dataset_jan_1st_2026/raw_checkings.csv
```
Output: `normalized_checkings.csv` in the same directory
