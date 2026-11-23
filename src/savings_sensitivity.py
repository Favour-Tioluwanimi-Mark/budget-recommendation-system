
import pandas as pd
import numpy as np

SAVINGS_TARGETS = [0.10, 0.20, 0.30]

# Load monthly spending and calculate MA forecasts
monthly = pd.read_csv("results/monthly_spending.csv")
monthly["Month"] = pd.to_datetime(monthly["Month"])
monthly = monthly.sort_values("Month").reset_index(drop=True)

monthly["Forecast"] = (
    monthly["Amount"].rolling(window=6).mean().shift(1)
)

# Calculate the buffer using validation months only
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

# Load income data
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

    for target in SAVINGS_TARGETS:
        spending_cap = income * (1 - target)

        spending_budget = min(
            forecast + buffer,
            spending_cap
        )

        results.append({
            "Month": str(month),
            "Savings_Target": f"{target:.0%}",
            "Income": income,
            "Forecast": forecast,
            "Buffer": buffer,
            "Actual_Spending": actual_spending,
            "Spending_Budget": spending_budget,
            "Recommended_Savings": income - spending_budget,
            "Actual_Savings_Allocation_Rate": (
                income - spending_budget
            ) / income,
            "Overrun": max(
                0, actual_spending - spending_budget
            ),
            "Overrun_Occurred": actual_spending > spending_budget,
            "Cap_Binding": forecast + buffer > spending_cap
        })

results_df = pd.DataFrame(results)

results_df.to_csv(
    "results/savings_sensitivity.csv",
    index=False
)

summary = (
    results_df.groupby("Savings_Target", sort=False)
    .agg(
        Months=("Month", "count"),
        Average_Savings=("Recommended_Savings", "mean"),
        Average_Overrun=("Overrun", "mean"),
        Months_With_Overrun=("Overrun_Occurred", "sum"),
        Months_Cap_Binding=("Cap_Binding", "sum")
    )
    .reset_index()
)

summary.to_csv(
    "results/savings_sensitivity_summary.csv",
    index=False
)

print(f"\nHistorical safety buffer: INR {buffer:,.2f}")

print("\nSAVINGS TARGET SENSITIVITY — MONTHLY RESULTS")
print(
    results_df[[
        "Month",
        "Savings_Target",
        "Spending_Budget",
        "Recommended_Savings",
        "Overrun",
        "Cap_Binding"
    ]].round(2).to_string(index=False)
)

print("\nSUMMARY BY SAVINGS TARGET")
print(summary.round(2).to_string(index=False))

print("\nResults saved successfully.")
