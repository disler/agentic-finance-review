#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pandas", "matplotlib"]
# ///
"""
Financial graph generation script for the Agentic Finance Review project.

Generates multiple financial insight graphs from merged transaction CSV data.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import TYPE_CHECKING

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure

# Color palette
COLORS = {
    "income": "#2ecc71",  # Green
    "expenses": "#e74c3c",  # Red
    "primary": "#3498db",  # Blue
    "secondary": "#9b59b6",  # Purple
    "neutral": "#95a5a6",  # Gray
}

# Category colors for pie/bar charts
CATEGORY_COLORS = [
    "#3498db",  # Blue
    "#e74c3c",  # Red
    "#2ecc71",  # Green
    "#9b59b6",  # Purple
    "#f39c12",  # Orange
    "#1abc9c",  # Teal
    "#e67e22",  # Dark Orange
    "#34495e",  # Dark Gray
    "#95a5a6",  # Light Gray (for "Other")
]


def setup_style() -> None:
    """Configure matplotlib style settings."""
    plt.style.use("seaborn-v0_8-whitegrid")
    plt.rcParams["figure.figsize"] = [12, 7]
    plt.rcParams["font.size"] = 11
    plt.rcParams["axes.titlesize"] = 14
    plt.rcParams["axes.labelsize"] = 12


def load_transactions(directory: Path) -> pd.DataFrame:
    """Load the merged transactions CSV file."""
    csv_path = directory / "agentic_merged_transactions.csv"
    if not csv_path.exists():
        print(f"Error: {csv_path} not found", file=sys.stderr)
        sys.exit(1)

    df = pd.read_csv(csv_path)
    df["date"] = pd.to_datetime(df["date"])
    df["deposit"] = pd.to_numeric(df["deposit"], errors="coerce").fillna(0)
    df["withdrawal"] = pd.to_numeric(df["withdrawal"], errors="coerce").fillna(0)
    df["balance"] = pd.to_numeric(df["balance"], errors="coerce")
    return df


def get_date_range_str(df: pd.DataFrame) -> str:
    """Get formatted date range string for titles."""
    min_date = df["date"].min().strftime("%b %d, %Y")
    max_date = df["date"].max().strftime("%b %d, %Y")
    return f"{min_date} - {max_date}"


def generate_balance_chart(df: pd.DataFrame, output_dir: Path) -> None:
    """Generate balance over time line chart."""
    fig: Figure
    ax: Axes
    fig, ax = plt.subplots(figsize=(12, 7))

    for account in df["account_name"].unique():
        account_df = df[df["account_name"] == account].sort_values("date")
        ax.plot(
            account_df["date"],
            account_df["balance"],
            label=account.title(),
            linewidth=2,
        )

    ax.set_title(f"Account Balance Over Time\n{get_date_range_str(df)}")
    ax.set_xlabel("Date")
    ax.set_ylabel("Balance ($)")
    ax.legend()
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))

    plt.tight_layout()
    plt.savefig(output_dir / "plot_balance_over_time.png", dpi=150)
    plt.close()
    print("  Generated: plot_balance_over_time.png")


def generate_category_breakdown(df: pd.DataFrame, output_dir: Path) -> None:
    """Generate pie chart of spending by category."""
    # Filter out income (deposits) and get spending by category
    spending_df = df[df["withdrawal"] > 0].copy()

    if spending_df.empty:
        print("  Skipped: plot_category_breakdown.png (no spending data)")
        return

    category_totals = spending_df.groupby("category")["withdrawal"].sum()
    category_totals = category_totals.sort_values(ascending=False)

    # Top 8 categories, rest as "Other"
    if len(category_totals) > 8:
        top_categories = category_totals.head(8)
        other_total = category_totals.tail(len(category_totals) - 8).sum()
        if other_total > 0:
            top_categories = pd.concat(
                [top_categories, pd.Series({"Other": other_total})]
            )
    else:
        top_categories = category_totals

    fig: Figure
    ax: Axes
    fig, ax = plt.subplots(figsize=(10, 8))

    wedges, texts, autotexts = ax.pie(
        top_categories.values,
        labels=top_categories.index,
        autopct="%1.1f%%",
        colors=CATEGORY_COLORS[: len(top_categories)],
        startangle=90,
    )

    ax.set_title(f"Spending by Category\n{get_date_range_str(df)}")

    plt.tight_layout()
    plt.savefig(output_dir / "plot_category_breakdown.png", dpi=150)
    plt.close()
    print("  Generated: plot_category_breakdown.png")


def generate_income_vs_expenses(df: pd.DataFrame, output_dir: Path) -> None:
    """Generate bar chart comparing income and expenses."""
    total_income = df["deposit"].sum()
    total_expenses = df["withdrawal"].sum()
    net_amount = total_income - total_expenses

    fig: Figure
    ax: Axes
    fig, ax = plt.subplots(figsize=(10, 7))

    categories = ["Income", "Expenses", "Net"]
    values = [total_income, total_expenses, net_amount]
    bar_colors = [
        COLORS["income"],
        COLORS["expenses"],
        COLORS["income"] if net_amount >= 0 else COLORS["expenses"],
    ]

    bars = ax.bar(categories, values, color=bar_colors, width=0.6)

    # Add value labels on bars
    for bar, value in zip(bars, values, strict=False):
        height = bar.get_height()
        ax.annotate(
            f"${value:,.2f}",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=12,
            fontweight="bold",
        )

    ax.set_title(f"Income vs Expenses\n{get_date_range_str(df)}")
    ax.set_ylabel("Amount ($)")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    ax.axhline(y=0, color="black", linewidth=0.5)

    plt.tight_layout()
    plt.savefig(output_dir / "plot_income_vs_expenses.png", dpi=150)
    plt.close()
    print("  Generated: plot_income_vs_expenses.png")


def generate_spending_by_category(df: pd.DataFrame, output_dir: Path) -> None:
    """Generate horizontal bar chart of spending by category."""
    spending_df = df[df["withdrawal"] > 0].copy()

    if spending_df.empty:
        print("  Skipped: plot_spending_by_category.png (no spending data)")
        return

    category_totals = spending_df.groupby("category")["withdrawal"].sum()
    category_totals = category_totals.sort_values(ascending=True)

    fig: Figure
    ax: Axes
    fig, ax = plt.subplots(figsize=(12, max(7, len(category_totals) * 0.4)))

    bars = ax.barh(
        category_totals.index,
        category_totals.values,
        color=COLORS["primary"],
    )

    # Add value labels
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
        )

    ax.set_title(f"Spending by Category\n{get_date_range_str(df)}")
    ax.set_xlabel("Amount ($)")
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))

    plt.tight_layout()
    plt.savefig(output_dir / "plot_spending_by_category.png", dpi=150)
    plt.close()
    print("  Generated: plot_spending_by_category.png")


def generate_daily_transactions(df: pd.DataFrame, output_dir: Path) -> None:
    """Generate bar chart of daily transaction count."""
    daily_counts = df.groupby(df["date"].dt.date).size()

    fig: Figure
    ax: Axes
    fig, ax = plt.subplots(figsize=(14, 7))

    dates = pd.to_datetime(daily_counts.index)
    ax.bar(dates, daily_counts.values, color=COLORS["primary"], width=0.8)

    ax.set_title(
        f"Daily Transaction Count\n{get_date_range_str(df)} (n={len(df)} transactions)"
    )
    ax.set_xlabel("Date")
    ax.set_ylabel("Number of Transactions")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(daily_counts) // 15)))
    plt.xticks(rotation=45, ha="right")

    plt.tight_layout()
    plt.savefig(output_dir / "plot_daily_transactions.png", dpi=150)
    plt.close()
    print("  Generated: plot_daily_transactions.png")


def generate_top_merchants(df: pd.DataFrame, output_dir: Path) -> None:
    """Generate horizontal bar chart of top merchants by spending."""
    spending_df = df[df["withdrawal"] > 0].copy()

    if spending_df.empty:
        print("  Skipped: plot_top_merchants.png (no spending data)")
        return

    merchant_totals = spending_df.groupby("description")["withdrawal"].sum()
    top_merchants = merchant_totals.sort_values(ascending=True).tail(15)

    fig: Figure
    ax: Axes
    fig, ax = plt.subplots(figsize=(12, 8))

    bars = ax.barh(
        top_merchants.index,
        top_merchants.values,
        color=COLORS["secondary"],
    )

    for bar in bars:
        width = bar.get_width()
        ax.annotate(
            f"${width:,.2f}",
            xy=(width, bar.get_y() + bar.get_height() / 2),
            xytext=(5, 0),
            textcoords="offset points",
            ha="left",
            va="center",
            fontsize=9,
        )

    ax.set_title(f"Top 15 Merchants by Spending\n{get_date_range_str(df)}")
    ax.set_xlabel("Total Spent ($)")
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))

    plt.tight_layout()
    plt.savefig(output_dir / "plot_top_merchants.png", dpi=150)
    plt.close()
    print("  Generated: plot_top_merchants.png")


def generate_cumulative_spending(df: pd.DataFrame, output_dir: Path) -> None:
    """Generate cumulative spending curve over time."""
    spending_df = df[df["withdrawal"] > 0].copy()

    if spending_df.empty:
        print("  Skipped: plot_cumulative_spending.png (no spending data)")
        return

    daily_spending = spending_df.groupby(spending_df["date"].dt.date)["withdrawal"].sum()
    daily_spending = daily_spending.sort_index()
    cumulative = daily_spending.cumsum()

    fig: Figure
    ax: Axes
    fig, ax = plt.subplots(figsize=(12, 7))

    dates = pd.to_datetime(cumulative.index)
    ax.fill_between(dates, cumulative.values, alpha=0.3, color=COLORS["expenses"])
    ax.plot(dates, cumulative.values, color=COLORS["expenses"], linewidth=2)

    total = cumulative.iloc[-1] if len(cumulative) > 0 else 0
    ax.set_title(
        f"Cumulative Spending Over Time\n{get_date_range_str(df)} (Total: ${total:,.2f})"
    )
    ax.set_xlabel("Date")
    ax.set_ylabel("Cumulative Spending ($)")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))

    plt.tight_layout()
    plt.savefig(output_dir / "plot_cumulative_spending.png", dpi=150)
    plt.close()
    print("  Generated: plot_cumulative_spending.png")


def generate_spending_by_weekday(df: pd.DataFrame, output_dir: Path) -> None:
    """Generate bar chart of spending by day of week."""
    spending_df = df[df["withdrawal"] > 0].copy()

    if spending_df.empty:
        print("  Skipped: plot_spending_by_weekday.png (no spending data)")
        return

    spending_df["weekday"] = spending_df["date"].dt.day_name()
    weekday_order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    weekday_totals = spending_df.groupby("weekday")["withdrawal"].sum()
    weekday_totals = weekday_totals.reindex(weekday_order).fillna(0)

    fig: Figure
    ax: Axes
    fig, ax = plt.subplots(figsize=(10, 7))

    bars = ax.bar(
        weekday_totals.index,
        weekday_totals.values,
        color=COLORS["primary"],
    )

    for bar in bars:
        height = bar.get_height()
        if height > 0:
            ax.annotate(
                f"${height:,.0f}",
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=10,
            )

    ax.set_title(f"Spending by Day of Week\n{get_date_range_str(df)}")
    ax.set_xlabel("Day of Week")
    ax.set_ylabel("Total Spending ($)")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    plt.xticks(rotation=45, ha="right")

    plt.tight_layout()
    plt.savefig(output_dir / "plot_spending_by_weekday.png", dpi=150)
    plt.close()
    print("  Generated: plot_spending_by_weekday.png")


def main() -> None:
    """Main entry point for graph generation."""
    parser = argparse.ArgumentParser(
        description="Generate financial insight graphs from transaction data."
    )
    parser.add_argument(
        "directory",
        type=Path,
        help="Directory containing agentic_merged_transactions.csv",
    )
    args = parser.parse_args()

    directory = args.directory.resolve()
    if not directory.exists():
        print(f"Error: Directory {directory} does not exist", file=sys.stderr)
        sys.exit(1)

    # Create assets directory
    assets_dir = directory / "assets"
    assets_dir.mkdir(exist_ok=True)

    print(f"Generating graphs from: {directory}")
    print(f"Output directory: {assets_dir}")

    setup_style()
    df = load_transactions(directory)

    print(f"\nLoaded {len(df)} transactions")
    print(f"Date range: {get_date_range_str(df)}")
    print(f"Accounts: {', '.join(df['account_name'].unique())}")

    # Generate required graphs
    print("\nGenerating required graphs:")
    generate_balance_chart(df, assets_dir)
    generate_category_breakdown(df, assets_dir)
    generate_income_vs_expenses(df, assets_dir)
    generate_spending_by_category(df, assets_dir)
    generate_daily_transactions(df, assets_dir)

    # Generate novel graphs
    print("\nGenerating novel graphs:")
    generate_top_merchants(df, assets_dir)
    generate_cumulative_spending(df, assets_dir)
    generate_spending_by_weekday(df, assets_dir)

    print("\nGraph generation complete!")
    print(f"Files saved to: {assets_dir}")


if __name__ == "__main__":
    main()
