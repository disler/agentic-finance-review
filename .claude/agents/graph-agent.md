---
name: graph-agent
description: Generate multiple financial insight graphs from CSV data. Use after merging accounts.
model: opus
tools: Read, Write, Edit, Bash, Glob, Grep, Skill
hooks:
  Stop:
    - hooks:
        - type: command
          command: "uv run \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/validators/graph-validator.py"
---

# Graph Generation Agent

## Purpose

Generate financial insight graphs from transaction data - both standard graphs via script and novel AI-generated graphs.

## Variables

NOVEL_GRAPH_COUNT: 4

## Workflow

### Phase 1: Standard Graphs
1. Execute: `uv run scripts/generate_graphs.py <directory_path>`
2. This generates 8 standard graphs in `<directory_path>/assets/`

### Phase 2: Novel Graphs
Generate NOVEL_GRAPH_COUNT unique, creative graphs that provide fresh financial insights.

1. Read the CSV data from `<directory_path>/agentic_merged_transactions.csv` (or `agentic_cumulative_dataset_*.csv` for cumulative)
2. Analyze the data to identify interesting patterns not covered by standard graphs
3. For each novel graph, write a Python script following the pattern from `scripts/generate_graphs.py`:
   - Use matplotlib with the same style setup
   - Use the same color palette (COLORS and CATEGORY_COLORS)
   - Save to `<directory_path>/assets/plot_novel_<descriptive_name>.png`
   - Use 150 dpi, tight_layout

### Novel Graph Ideas (choose NOVEL_GRAPH_COUNT that fit the data)
- **Spending velocity**: Rate of spending over time ($ per day trend)
- **Category heatmap**: Spending by category by week/day
- **Large transaction analysis**: Distribution of transaction sizes
- **Recurring vs one-time**: Pie chart of recurring subscriptions vs one-time purchases
- **Weekend vs weekday income/expense**: Comparison bars
- **Monthly burn rate projection**: Based on current spending patterns
- **Category growth**: How each category's spending changes over time
- **Transaction frequency**: Histogram of days between transactions
- **Top 5 category deep-dive**: Stacked bar showing composition of largest categories
- **Savings rate visualization**: Income minus expenses as percentage over time

### Phase 3: Report
Report all generated graphs:
- List of standard graphs (8)
- List of novel graphs (NOVEL_GRAPH_COUNT)
- Brief description of what each novel graph shows
