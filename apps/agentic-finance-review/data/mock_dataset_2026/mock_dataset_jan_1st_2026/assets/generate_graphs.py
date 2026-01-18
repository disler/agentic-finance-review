#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pandas", "matplotlib", "numpy"]
# ///
"""
Generate 8 financial insight graphs from transaction data.
"""
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path
import numpy as np

# Color palette
COLORS = {
    "income": "#2ecc71",  # Green
    "expenses": "#e74c3c",  # Red
    "primary": "#3498db",  # Blue
    "secondary": "#9b59b6",  # Purple
    "neutral": "#95a5a6",  # Gray
}

CATEGORY_COLORS = [
    "#3498db",  # Blue
    "#e74c3c",  # Red
    "#2ecc71",  # Green
    "#9b59b6",  # Purple
    "#f39c12",  # Orange
    "#1abc9c",  # Teal
    "#e67e22",  # Dark Orange
    "#34495e",  # Dark Gray
    "#95a5a6",  # Light Gray
]

def setup_style():
    """Configure matplotlib style settings."""
    plt.style.use("seaborn-v0_8-whitegrid")
    plt.rcParams["figure.figsize"] = [12, 7]
    plt.rcParams["font.size"] = 11
    plt.rcParams["axes.titlesize"] = 14
    plt.rcParams["axes.labelsize"] = 12

def get_date_range_str(df):
    """Get formatted date range string for titles."""
    min_date = df["date"].min().strftime("%b %d, %Y")
    max_date = df["date"].max().strftime("%b %d, %Y")
    return f"{min_date} - {max_date}"

# Directory paths
base_dir = Path("/Users/indydevdan/Documents/projects/yt/agentic-finance-review/apps/agentic-finance-review/data/mock_dataset_2026/mock_dataset_jan_1st_2026")
csv_path = base_dir / "agentic_merged_transactions.csv"
output_dir = base_dir / "assets"

# Load data
df = pd.read_csv(csv_path)
df["date"] = pd.to_datetime(df["date"])
df["deposit"] = pd.to_numeric(df["deposit"], errors="coerce").fillna(0)
df["withdrawal"] = pd.to_numeric(df["withdrawal"], errors="coerce").fillna(0)
df["balance"] = pd.to_numeric(df["balance"], errors="coerce")

setup_style()
date_range = get_date_range_str(df)

# 1. Spending by Category Pie Chart
print("Generating plot_01_spending_by_category_pie.png...")
spending_df = df[df["withdrawal"] > 0].copy()
category_totals = spending_df.groupby("category")["withdrawal"].sum()
category_totals = category_totals.sort_values(ascending=False)

if len(category_totals) > 8:
    top_categories = category_totals.head(8)
    other_total = category_totals.tail(len(category_totals) - 8).sum()
    if other_total > 0:
        top_categories = pd.concat([top_categories, pd.Series({"Other": other_total})])
else:
    top_categories = category_totals

fig, ax = plt.subplots(figsize=(10, 8))
wedges, texts, autotexts = ax.pie(
    top_categories.values,
    labels=top_categories.index,
    autopct="%1.1f%%",
    colors=CATEGORY_COLORS[:len(top_categories)],
    startangle=90,
    explode=[0.02] * len(top_categories),
)
for autotext in autotexts:
    autotext.set_fontsize(10)
    autotext.set_fontweight("bold")
ax.set_title(f"Spending by Category\n{date_range}", fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig(output_dir / "plot_01_spending_by_category_pie.png", dpi=150)
plt.close()

# 2. Daily Spending Trend
print("Generating plot_02_daily_spending_trend.png...")
daily_spending = spending_df.groupby(spending_df["date"].dt.date)["withdrawal"].sum()
daily_spending = daily_spending.sort_index()

fig, ax = plt.subplots(figsize=(12, 7))
dates = pd.to_datetime(daily_spending.index)
ax.plot(dates, daily_spending.values, color=COLORS["expenses"], linewidth=2, marker="o", markersize=6)
ax.fill_between(dates, daily_spending.values, alpha=0.3, color=COLORS["expenses"])

# Add trend line
z = np.polyfit(range(len(daily_spending)), daily_spending.values, 1)
p = np.poly1d(z)
ax.plot(dates, p(range(len(daily_spending))), "--", color=COLORS["neutral"], linewidth=2, label="Trend")

ax.set_title(f"Daily Spending Trend\n{date_range}", fontsize=14, fontweight="bold")
ax.set_xlabel("Date")
ax.set_ylabel("Daily Spending ($)")
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))
ax.legend()
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig(output_dir / "plot_02_daily_spending_trend.png", dpi=150)
plt.close()

# 3. Income vs Expenses
print("Generating plot_03_income_vs_expenses.png...")
total_income = df["deposit"].sum()
total_expenses = df["withdrawal"].sum()
net_amount = total_income - total_expenses

fig, ax = plt.subplots(figsize=(10, 7))
categories = ["Income", "Expenses", "Net"]
values = [total_income, total_expenses, net_amount]
bar_colors = [
    COLORS["income"],
    COLORS["expenses"],
    COLORS["income"] if net_amount >= 0 else COLORS["expenses"],
]

bars = ax.bar(categories, values, color=bar_colors, width=0.6, edgecolor="white", linewidth=2)

for bar, value in zip(bars, values):
    height = bar.get_height()
    va = "bottom" if height >= 0 else "top"
    offset = 3 if height >= 0 else -15
    ax.annotate(
        f"${value:,.2f}",
        xy=(bar.get_x() + bar.get_width() / 2, height),
        xytext=(0, offset),
        textcoords="offset points",
        ha="center",
        va=va,
        fontsize=14,
        fontweight="bold",
    )

ax.set_title(f"Income vs Expenses\n{date_range}", fontsize=14, fontweight="bold")
ax.set_ylabel("Amount ($)")
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))
ax.axhline(y=0, color="black", linewidth=0.5)
plt.tight_layout()
plt.savefig(output_dir / "plot_03_income_vs_expenses.png", dpi=150)
plt.close()

# 4. Top Merchants
print("Generating plot_04_top_merchants.png...")
merchant_totals = spending_df.groupby("description")["withdrawal"].sum()
top_merchants = merchant_totals.sort_values(ascending=True).tail(10)

fig, ax = plt.subplots(figsize=(12, 8))
colors_gradient = plt.cm.Blues(np.linspace(0.4, 0.9, len(top_merchants)))
bars = ax.barh(top_merchants.index, top_merchants.values, color=colors_gradient)

for bar in bars:
    width = bar.get_width()
    ax.annotate(
        f"${width:,.2f}",
        xy=(width, bar.get_y() + bar.get_height() / 2),
        xytext=(5, 0),
        textcoords="offset points",
        ha="left",
        va="center",
        fontsize=10,
        fontweight="bold",
    )

ax.set_title(f"Top 10 Merchants by Spending\n{date_range}", fontsize=14, fontweight="bold")
ax.set_xlabel("Total Spent ($)")
ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))
plt.tight_layout()
plt.savefig(output_dir / "plot_04_top_merchants.png", dpi=150)
plt.close()

# 5. Category Over Time (Stacked Area)
print("Generating plot_05_category_over_time.png...")
spending_df["date_only"] = spending_df["date"].dt.date
category_by_date = spending_df.pivot_table(
    index="date_only",
    columns="category",
    values="withdrawal",
    aggfunc="sum",
    fill_value=0
)
category_by_date = category_by_date.sort_index()

fig, ax = plt.subplots(figsize=(14, 7))
dates = pd.to_datetime(category_by_date.index)
ax.stackplot(
    dates,
    category_by_date.T.values,
    labels=category_by_date.columns,
    colors=CATEGORY_COLORS[:len(category_by_date.columns)],
    alpha=0.8
)

ax.set_title(f"Category Spending Over Time\n{date_range}", fontsize=14, fontweight="bold")
ax.set_xlabel("Date")
ax.set_ylabel("Spending ($)")
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))
ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1), fontsize=9)
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig(output_dir / "plot_05_category_over_time.png", dpi=150)
plt.close()

# 6. Running Balance
print("Generating plot_06_running_balance.png...")
df_sorted = df.sort_values("date")

fig, ax = plt.subplots(figsize=(12, 7))
ax.plot(df_sorted["date"], df_sorted["balance"], color=COLORS["primary"], linewidth=2)
ax.fill_between(df_sorted["date"], df_sorted["balance"], alpha=0.3, color=COLORS["primary"])

# Mark min and max
min_idx = df_sorted["balance"].idxmin()
max_idx = df_sorted["balance"].idxmax()
ax.scatter([df_sorted.loc[min_idx, "date"]], [df_sorted.loc[min_idx, "balance"]],
           color=COLORS["expenses"], s=100, zorder=5, label=f'Min: ${df_sorted.loc[min_idx, "balance"]:,.2f}')
ax.scatter([df_sorted.loc[max_idx, "date"]], [df_sorted.loc[max_idx, "balance"]],
           color=COLORS["income"], s=100, zorder=5, label=f'Max: ${df_sorted.loc[max_idx, "balance"]:,.2f}')

ax.set_title(f"Account Balance Over Time\n{date_range}", fontsize=14, fontweight="bold")
ax.set_xlabel("Date")
ax.set_ylabel("Balance ($)")
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))
ax.legend()
plt.tight_layout()
plt.savefig(output_dir / "plot_06_running_balance.png", dpi=150)
plt.close()

# 7. Spending Distribution (Histogram)
print("Generating plot_07_spending_distribution.png...")
fig, ax = plt.subplots(figsize=(12, 7))

withdrawal_amounts = spending_df["withdrawal"].values
bins = np.histogram_bin_edges(withdrawal_amounts, bins="auto")
n, bins, patches = ax.hist(withdrawal_amounts, bins=bins, color=COLORS["primary"],
                            edgecolor="white", linewidth=1.2, alpha=0.8)

# Color bins by size
cm = plt.cm.Blues
for i, patch in enumerate(patches):
    patch.set_facecolor(cm(0.4 + 0.5 * i / len(patches)))

ax.axvline(withdrawal_amounts.mean(), color=COLORS["expenses"], linestyle="--",
           linewidth=2, label=f'Mean: ${withdrawal_amounts.mean():,.2f}')
ax.axvline(np.median(withdrawal_amounts), color=COLORS["income"], linestyle="--",
           linewidth=2, label=f'Median: ${np.median(withdrawal_amounts):,.2f}')

ax.set_title(f"Spending Distribution\n{date_range}", fontsize=14, fontweight="bold")
ax.set_xlabel("Transaction Amount ($)")
ax.set_ylabel("Frequency")
ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))
ax.legend()
plt.tight_layout()
plt.savefig(output_dir / "plot_07_spending_distribution.png", dpi=150)
plt.close()

# 8. Spending by Weekday
print("Generating plot_08_spending_by_weekday.png...")
spending_df["weekday"] = spending_df["date"].dt.day_name()
weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
weekday_totals = spending_df.groupby("weekday")["withdrawal"].sum()
weekday_totals = weekday_totals.reindex(weekday_order).fillna(0)

fig, ax = plt.subplots(figsize=(10, 7))
colors_weekday = [COLORS["primary"]] * 5 + [COLORS["secondary"]] * 2  # Different color for weekends

bars = ax.bar(weekday_totals.index, weekday_totals.values, color=colors_weekday,
              edgecolor="white", linewidth=2)

for bar in bars:
    height = bar.get_height()
    if height > 0:
        ax.annotate(
            f"${height:,.0f}",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 5),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=11,
            fontweight="bold",
        )

ax.set_title(f"Spending by Day of Week\n{date_range}", fontsize=14, fontweight="bold")
ax.set_xlabel("Day of Week")
ax.set_ylabel("Total Spending ($)")
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig(output_dir / "plot_08_spending_by_weekday.png", dpi=150)
plt.close()

print("\nAll 8 graphs generated successfully!")
print(f"Output directory: {output_dir}")
