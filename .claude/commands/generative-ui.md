---
model: opus
description: Generate the index.html financial dashboard from CSV data and graphs
argument-hint: <month-dir>
hooks:
  Stop:
    - hooks:
        - type: command
          command: "uv run \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/validators/html-validator.py"
---

# Generative UI Command

## Purpose

Generate a stunning, modern HTML dashboard visualizing financial data with a premium fintech aesthetic.

## Variables

DIRECTORY: $ARGUMENTS
ROOT_OPERATIONS_DIR: CLAUDE.md: ROOT_OPERATIONS_DIR

## Instructions

- IMPORTANT: Adhere strongly to the design theme detailed below. 2 columns. theme. heatmap. sortable table. Make sure to build out these details.

### Input Files
- `normalized_*.csv` - Individual account transactions
- `agentic_merged_transactions.csv` - Combined transactions (or `agentic_cumulative_dataset_*.csv` for yearly)
- `assets/*.png` - Generated graphs (standard + novel)

### Output
- `index.html` - Single-page dashboard with embedded styles

### Design System

#### Visual Style
Modern, minimalist fintech aesthetic inspired by premium finance apps:

- **Layout**: Card-based bento grid with generous whitespace
- **Colors**:
  - Light mode: Clean white (#FFFFFF) cards on soft gray (#F5F7FA) background
  - Accent: Emerald green (#10B981) for positive/income, Coral red (#EF4444) for negative/expenses
  - Secondary accents: Soft purple (#8B5CF6), Ocean blue (#3B82F6), Amber (#F59E0B)
- **Typography**:
  - Large, bold numbers for key metrics (48-64px, font-weight 700)
  - Clean sans-serif (system-ui, Inter, or SF Pro)
  - Subtle gray (#6B7280) for labels and secondary text
- **Cards**:
  - Rounded corners (16-24px border-radius)
  - Subtle shadows (0 4px 6px -1px rgba(0,0,0,0.1))
  - No harsh borders - use shadow for depth
- **Charts/Graphs**: Display with clean white card backgrounds
- **Progress indicators**: Circular gauges, horizontal progress bars with rounded ends
- **Spacing**: Generous padding (24-32px), consistent gaps (16-24px)

#### Component Patterns
- **Metric cards**: Large number, small label below, optional trend indicator (↑ 2.1%)
- **Donut charts**: Center text showing total/percentage
- **Transaction rows**: Subtle hover states, alternating backgrounds optional
- **Category pills**: Colored dots + labels for legends
- **Time range selectors**: Pill-style buttons (7D, 1M, 3M, YTD, All)

#### What NOT to do
- No mobile responsive breakpoints needed
- No dark mode required
- No external CDN dependencies
- No complex JavaScript frameworks
- No gradients or overly decorative elements
- No borders on cards (shadows only)

### Dashboard Sections

1. **Header**
   - Title: "Financial Review - [Month] [Year]"
   - Date range subtitle
   - Minimal, clean

2. **Summary Metrics Row**
   - Total Income (green)
   - Total Expenses (red)
   - Net Cash Flow (green/red based on value)
   - Transaction Count
   - Each in its own card with large number + label

3. **Graphs Section**
   - **Two-column grid layout**
   - `display: grid; grid-template-columns: 1fr 1fr; gap: 24px;`
   - Each graph in a white card
   - Title above each graph
   - Images fill their container: `img { width: 100%; height: auto; }`

4. **Spending by Category Treemap**
   - CSS-based treemap visualization (no JS libraries)
   - Each category is a colored rectangle
   - Rectangle size proportional to spending amount
   - Display category name + amount inside each rectangle
   - Use flexbox with `flex-grow` based on percentage
   - Color palette: use distinct colors per category
   - Example structure:
     ```html
     <div class="treemap">
       <div class="treemap-item" style="flex-grow: 45; background: #10B981;">
         <span class="category">Bills</span>
         <span class="amount">$2,395.00</span>
       </div>
       <!-- more items... -->
     </div>
     ```
   - Treemap container: `display: flex; flex-wrap: wrap; height: 400px;`
   - Items: `min-width: 100px; min-height: 80px; padding: 12px;`

5. **Recent Transactions Table**
   - Clean table with subtle styling
   - Columns: Date, Description, Category, Amount, Balance
   - Green/red text for deposit/withdrawal
   - **Sortable by column** - vanilla JS click handlers on `<th>` elements
   - Sort indicator: ▲/▼ arrows in header
   - Example sort implementation:
     ```javascript
     document.querySelectorAll('th[data-sort]').forEach(th => {
       th.style.cursor = 'pointer';
       th.onclick = () => sortTable(th.dataset.sort);
     });
     ```
   - Show all transactions (not limited)

## Workflow

1. Read directory path from `$ARGUMENTS`
2. Load CSV data and compute summaries:
   - Total income (sum of deposits)
   - Total expenses (sum of withdrawals)
   - Net cash flow
   - Transaction count
   - Category totals
3. Find all PNG files in assets/ directory
4. Generate HTML with:
   - Embedded CSS following the design system above
   - Summary metric cards
   - Graph cards (single column, full width)
   - Spending by category treemap
   - Transaction table
5. Write to `index.html` in the directory
6. Stop hook validates the HTML

## Report

After generating, confirm:
- File: `[DIRECTORY]/index.html`
- Metrics displayed: [count]
- Graphs embedded: [count]
- Transactions shown: [count]
