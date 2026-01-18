---
model: opus
description: Categorize transactions in normalized CSV files based on descriptions
argument-hint: <month-dir>
hooks:
  Stop:
    - hooks:
        - type: command
          command: "uv run \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/validators/csv-validator.py"
---

# Categorize CSV Command

## Purpose

Analyze transaction descriptions in normalized CSV files and populate the empty `category` column with appropriate personal spending categories.

## Variables

DIR_PATH: $ARGUMENTS

## Categories

| Category | Keywords |
|----------|----------|
| `engineering` | CURSOR, OPENAI, ANTHROPIC, REPLICATE, GOOGLE CLOUD, NEON.TECH, VERCEL, AWS, GITHUB, ELEVENLABS |
| `trading` | TRADINGVIEW |
| `food` | TRADER JOE, WHOLE FOODS, DOORDASH, UBER EATS, restaurant, grocery |
| `bills` | RENT, CON EDISON, NATIONAL GRID, SPECTRUM, utilities |
| `entertainment` | NETFLIX, SPOTIFY, MAX.COM, DISNEY, MIDJOURNEY |
| `amazon` | AMAZON, AMZN (purchases, not Prime) |
| `subscriptions` | Prime, recurring monthly services |
| `transfers` | VENMO, APPLE CASH, ZELLE, bank transfers |
| `income` | PAYCHECK, salary, ACH CREDIT, interest |
| `loans` | STUDENT LN, DEPT EDUCATION |
| `travel` | Airlines, hotels, Uber/Lyft rides |
| `health` | BROOKLYN BOULDERS, pharmacy, medical |
| `other` | Default fallback |

## Workflow

1. Find all `normalized_*.csv` files in DIR_PATH
2. For each transaction, analyze description and assign category
3. Update the category column in place
4. Report results
