---
model: opus
description: Main orchestrator - runs the full agentic finance review workflow
argument-hint: <month> <csv1> [csv2] ...
hooks:
  Stop:
    - hooks:
        - type: command
          command: "uv run \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/validators/html-validator.py"
---

# Review Finances

## Purpose

Orchestrate the complete agentic finance review workflow by chaining multiple specialized subagents to process raw bank CSV exports into a comprehensive HTML dashboard with financial insights and visualizations.

## Variables

MONTH: $1
CSV_FILES: $2, $3, $4, ... (remaining arguments - file paths or pasted CSV content)
YEAR: `date +%Y` (get current year from CLI)
ROOT_OPERATIONS_DIR: CLAUDE.md: ROOT_OPERATIONS_DIR
MONTH_DIR: ROOT_OPERATIONS_DIR/mock_dataset_{MONTH}_1st_{YEAR}

## Instructions

- First, set up the target directory and ensure raw CSV files are in place
- Chain through each agent in sequential order - do NOT proceed to next agent if current fails
- Wait for each agent to complete before proceeding to the next
- All agents receive MONTH_DIR as their directory path
- Report progress after each step completes
- Do NOT skip any agents in the chain

## Workflow

1. Get current year: `date +%Y`
2. Parse arguments: MONTH and CSV_FILES
3. Construct MONTH_DIR path: `ROOT_OPERATIONS_DIR/mock_dataset_{MONTH}_1st_{YEAR}`
4. Execute the setup and agent chain in order:

### Step 0: Setup Directory and CSV Files

Create or verify the target directory and populate with raw CSV files:

1. Check if MONTH_DIR exists, if not create it with `mkdir -p`
2. Create `assets/` subdirectory if needed
3. For each CSV file provided in CSV_FILES:
   - **Infer account name from filename** if possible:
     - `checkings.csv`, `checking.csv`, `chk.csv` → `checkings`
     - `savings.csv`, `saving.csv`, `sav.csv` → `savings`
     - `credit.csv`, `creditcard.csv`, `cc.csv` → `credit`
     - `raw_*.csv` → extract name between `raw_` and `.csv`
   - **If account name cannot be inferred**, use AskUserQuestion:
     ```
     Question: "What account does this CSV represent?"
     Header: "Account"
     Options:
       - "checkings" - Primary checking account
       - "savings" - Savings account
       - "credit" - Credit card account
     ```
   - **If it's a file path** (exists): Copy to MONTH_DIR as `raw_{account_name}.csv`
   - **If it's pasted CSV content**: Write to MONTH_DIR as `raw_{account_name}.csv`
4. Verify at least one `raw_*.csv` file exists in MONTH_DIR

### Agent Chain

#### Step 1: Normalize Agent
Invoke: `Use the normalize-csv-agent to process MONTH_DIR`
- **Input**: raw_*.csv files in MONTH_DIR
- **Output**: normalized_*.csv files (category column empty)

#### Step 2: Categorize Agent
Invoke: `Use the categorize-csv-agent to categorize transactions in MONTH_DIR`
- **Input**: normalized_*.csv files
- **Output**: Same files with category column populated

#### Step 3: Merge Agent
Invoke: `Use the merge-accounts-agent to merge accounts in MONTH_DIR`
- **Input**: normalized_*.csv files (now categorized)
- **Output**: agentic_merged_transactions.csv

#### Step 4: Accumulate
Invoke: `/accumulate-csvs MONTH_DIR`
- **Input**: agentic_merged_transactions.csv
- **Output**: ROOT_OPERATIONS_DIR/agentic_cumulative_dataset_{YEAR}.csv

#### Step 5: Graph Agent (Monthly)
Invoke: `Use the graph-agent to generate visualizations for MONTH_DIR`
- **Input**: agentic_merged_transactions.csv
- **Output**: MONTH_DIR/assets/*.png (8 graphs)

#### Step 6: Graph Agent (Cumulative)
Invoke: `Use the graph-agent to generate visualizations for ROOT_OPERATIONS_DIR using agentic_cumulative_dataset_{YEAR}.csv`
- **Input**: ROOT_OPERATIONS_DIR/agentic_cumulative_dataset_{YEAR}.csv
- **Output**: ROOT_OPERATIONS_DIR/assets/*.png (8 graphs for full year)

#### Step 7: Generative UI Agent (Monthly)
Invoke: `Use the generative-ui-agent to create the dashboard for MONTH_DIR`
- **Input**: CSVs + MONTH_DIR/assets/*.png
- **Output**: MONTH_DIR/index.html

#### Step 8: Generative UI Agent (Cumulative)
Invoke: `Use the generative-ui-agent to create the dashboard for ROOT_OPERATIONS_DIR`
- **Input**: agentic_cumulative_dataset_{YEAR}.csv + ROOT_OPERATIONS_DIR/assets/*.png
- **Output**: ROOT_OPERATIONS_DIR/index.html (yearly dashboard)

#### Step 9: Open Dashboard
Open the generated dashboard in Chrome:
```bash
open -a "Google Chrome" MONTH_DIR/index.html
```

5. Now follow the `Report` section to report the completed work

## Report

Present progress and completion in this format:

## Finance Review: [MONTH] [YEAR]

### Setup
- Directory: [MONTH_DIR]
- Raw files: [list of raw_*.csv files]

### Progress
- [x] Setup: Directory created, [count] CSV files placed
- [x] Normalize: [count] files processed
- [x] Categorize: [count] transactions categorized
- [x] Merge: Combined into agentic_merged_transactions.csv
- [x] Accumulate: Updated cumulative dataset
- [x] Graph (Monthly): [count] visualizations generated
- [x] Graph (Cumulative): [count] visualizations generated for year
- [x] Dashboard (Monthly): index.html created
- [x] Dashboard (Cumulative): yearly index.html created
- [x] View: Opened dashboard in Chrome

### Final Deliverables

**Monthly (MONTH_DIR):**
1. `normalized_*.csv` - Clean, normalized transaction files
2. `agentic_merged_transactions.csv` - Combined transactions
3. `assets/*.png` - Financial insight graphs
4. `index.html` - Monthly dashboard

**Cumulative (ROOT_OPERATIONS_DIR):**
5. `agentic_cumulative_dataset_{YEAR}.csv` - Yearly cumulative data
6. `assets/*.png` - Yearly insight graphs
7. `index.html` - Yearly dashboard

### Examples
```
# With existing CSV files
/review-finances feb /path/to/checkings.csv /path/to/savings.csv

# With just month (if raw files already exist in target dir)
/review-finances jan
```
