---
description: Generate mock CSV financial data for testing the agentic finance review workflow
argument-hint: <type> <month> <year> <account_name>
hooks:
  Stop:
    - hooks:
        - type: command
          command: "uv run \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/validators/csv-validator.py"

---

# CSV Mock Data Generator

Generate realistic mock financial transaction data for testing.

## Variables
ROOT_OPERATIONS_DIR: CLAUDE.md: ROOT_OPERATIONS_DIR

## Arguments
- `$ARGUMENTS` contains: `<type> <month> <year> <account_name>`
  - type: "raw" or "normalized"
  - month: "january", "february", etc.
  - year: "2026"
  - account_name: "checkings", "savings", etc.

## Output Location
- Raw files: `ROOT_OPERATIONS_DIR/mock_dataset_<month>_1st_<year>/raw_<account_name>.csv`
- Normalized files: Same location with `normalized_` prefix

## Raw CSV Format (Bank Export Style)
Bank exports have varying formats. Generate realistic messy data:
```csv
Date,Description,Withdrawals,Deposits,Category,Balance
"01/31/2026","DEBIT CARD PURCHASE   XXXXX4291 Amazon Prime*KV2819YT5    Amzn.com/bi WA","$148.32","","Subscriptions and Renewals","$42,156.78"
```

## Normalized CSV Format (Our Standard)
```csv
date,description,category,deposit,withdrawal,balance,account_name
2026-01-31,Amazon Prime Subscription,,148.32,,42156.78,checkings
```

## Personal Category Mappings
Map bank categories to our personal categories:
- "Subscriptions and Renewals", "Services and Supplies" -> "engineering" (for dev tools like Cursor, OpenAI, Anthropic)
- "General Merchandise" + Amazon -> "amazon"
- "Groceries", "Restaurants and Dining" -> "food"
- "Entertainment" -> "entertainment"
- "Utilities", "Cable" -> "bills"
- "Transfers" -> "transfers"
- "Other Income", "Interest" -> "income"
- "Loans" -> "loans"
- "Travel" -> "travel"
- Anything with "REPLICATE", "OPENAI", "ANTHROPIC", "CURSOR", "TRADINGVIEW", "GOOGLE CLOUD" -> "engineering"
- Anything with "TRADING" in description -> "trading"

## Transaction Types to Include
Generate 50-100 transactions per month including:
- Regular income (paycheck deposits)
- Recurring bills (rent, utilities, subscriptions)
- Food (groceries, restaurants)
- Engineering tools (Cursor, OpenAI, Anthropic, Google Cloud, etc.)
- Entertainment subscriptions (Netflix, Spotify, etc.)
- Random purchases (Amazon, etc.)
- Transfers between accounts

## Instructions

1. Parse the arguments from `$ARGUMENTS`
2. Determine the output directory based on month/year
3. Create the directory if it doesn't exist
4. Generate realistic transaction data with:
   - Dates within the specified month only
   - Realistic amounts and descriptions
   - Mix of deposits and withdrawals
   - Running balance that makes sense
5. If type is "raw": Generate bank-style messy format with wrong/generic categories
6. If type is "normalized": Generate clean format with correct personal categories
7. Write the CSV file to the correct location
8. Report what was generated

## Example Usage
```
/csv-mock-generator raw january 2026 checkings
/csv-mock-generator normalized february 2026 savings
```
