
import pandas as pd
import numpy as np

SAVINGS_RATE = 0.20

# Load monthly spending
monthly = pd.read_csv("results/monthly_spending.csv")
monthly["Month"] = pd.to_datetime(monthly["Month"])
monthly = monthly.sort_values("Month").reset_index(drop=True)

# Calculate six-month Moving Average forecasts
monthly["Forecast"] = (
    monthly["Amount"].rolling(window=6).mean().shift(1)
)

# Estimate the safety buffer using validation data only
validation = monthly[
    (monthly["Month"] >= "2017-07-01") &
    (monthly["Month"] <= "2017-12-01")
].copy()

validation["Underestimation"] = (
    validation["Amount"] - validation["Forecast"]
).clip(lower=0)

buffer = float(
    np.percentile(validation["Underestimation"], 75)
)

print(f"\nSafety buffer from validation data: INR {buffer:,.2f}")

# Load recorded income
original = pd.read_csv("data/Daily Household Transactions.csv")
original["Date"] = pd.to_datetime(
    original["Date"], format="mixed", dayfirst=True
)
original["Month"] = original["Date"].dt.to_period("M")

income_data = (
    original[original["Income/Expense"] == "Income"]
    .groupby("Month")["Amount"]
    .sum()
)

# Evaluate January-August 2018
test = monthly[
    (monthly["Month"] >= "2018-01-01") &
    (monthly["Month"] <= "2018-08-01")
]

results = []

for _, row in test.iterrows():
    month = row["Month"].to_period("M")
    income = income_data.get(month, float("nan"))

    if pd.isna(income) or income <= 0:
        continue

    actual_spending = row["Amount"]
    forecast = row["Forecast"]

    spending_cap = income * (1 - SAVINGS_RATE)

    original_budget = min(forecast, spending_cap)
    improved_budget = min(forecast + buffer, spending_cap)
    baseline_budget = spending_cap

    for method, budget in [
        ("Original MA", original_budget),
        ("MA + Buffer", improved_budget),
        ("50/30/20", baseline_budget)
    ]:
        results.append({
            "Month": str(month),
            "Method": method,
            "Income": income,
            "Forecast": forecast,
            "Actual_Spending": actual_spending,
            "Spending_Budget": budget,
            "Recommended_Savings": income - budget,
            "Overrun": max(0, actual_spending - budget),
            "Overrun_Occurred": actual_spending > budget
        })

results_df = pd.DataFrame(results)

results_df.to_csv(
    "results/uncertainty_budget_comparison.csv",
    index=False
)

summary = (
    results_df.groupby("Method")
    .agg(
        Months=("Month", "count"),
        Average_Savings=("Recommended_Savings", "mean"),
        Average_Overrun=("Overrun", "mean"),
        Months_With_Overrun=("Overrun_Occurred", "sum")
    )
    .reset_index()
)

summary.to_csv(
    "results/uncertainty_budget_summary.csv",
    index=False
)

print("\nMONTHLY BUDGET COMPARISON")
print(
    results_df[[
        "Month", "Method", "Forecast",
        "Spending_Budget", "Recommended_Savings", "Overrun"
    ]].round(2).to_string(index=False)
)

print("\nSUMMARY")
print(summary.round(2).to_string(index=False))

print("\nResults saved successfully.")
