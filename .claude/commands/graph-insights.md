---
description: Generate insightful financial graphs from CSV transaction data
argument-hint: <csv_file>
hooks:
  Stop:
    - hooks:
        - type: command
          command: "uv run \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/validators/graph-validator.py"
---

# Graph Insights Command

Generate a single insightful graph from CSV financial data.

## Variables
ROOT_OPERATIONS_DIR: CLAUDE.md: ROOT_OPERATIONS_DIR

## Arguments
- `$ARGUMENTS`: Path to a CSV file (e.g., `ROOT_OPERATIONS_DIR/mock_dataset_jan_1st_2026/agentic_merged_transactions.csv`)

## Output
- PNG file in the `assets/` subdirectory of the CSV's parent folder
- Filename: `plot_<insight_type>_<timestamp>.png`

## Graph Types to Generate

### Required Standard Graphs (run multiple times)
1. **Balance Over Time** - Line chart showing balance progression
2. **Category Breakdown** - Pie chart of spending by category
3. **Monthly Spending Trend** - Bar chart of total spending per category
4. **Income vs Expenses** - Comparison bar chart
5. **Top Merchants** - Horizontal bar chart of top spending destinations

### Novel/Interesting Graphs
6. **Daily Spending Pattern** - Heatmap of spending by day of week
7. **Category Trend Lines** - Multi-line chart showing category spending over time
8. **Savings Rate** - Line chart of (income - spending) / income over time
9. **Large Transaction Highlights** - Scatter plot highlighting outliers
10. **Recurring vs One-time** - Stacked area chart

## Graph Requirements

### Visual Quality
- Use matplotlib with a clean style (seaborn-v0_8-whitegrid or similar)
- Clear titles and axis labels
- Readable font sizes (minimum 10pt)
- Color-blind friendly palettes
- Legend when multiple series
- Figure size: minimum 10x6 inches for readability

### Data Accuracy
- CRITICAL: All values must be accurate from the source data
- Double-check totals and percentages
- Handle missing/empty values gracefully
- Show data ranges in title or subtitle

### File Output
- Save as PNG with tight bounding box
- Resolution: 150 DPI minimum
- Output to assets/ directory relative to CSV location

## Workflow

1. Read CSV path from `$ARGUMENTS`
2. Load and validate the data
3. Determine which graph type to generate (can be specified or auto-selected)
4. Create the visualization using matplotlib/pandas
5. Save to assets/ directory
6. Report what was generated

## Example Usage
The graph-agent will call this multiple times:
```
/graph-insights apps/.../mock_dataset_jan_1st_2026/agentic_merged_transactions.csv
```

Each call should generate a different insight. Use the existing graphs in assets/ to avoid duplicates.

## Python Libraries
Use these for graph generation:
```python
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
```
