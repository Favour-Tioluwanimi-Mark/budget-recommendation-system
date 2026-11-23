
import pandas as pd
from statsmodels.tsa.holtwinters import SimpleExpSmoothing

SAVINGS_RATE = 0.20
SES_ALPHA = 0.20

# Load monthly consumption spending
monthly = pd.read_csv("results/monthly_spending.csv")
monthly["Month"] = pd.to_datetime(monthly["Month"])
monthly = monthly.sort_values("Month").reset_index(drop=True)

# Calculate 6-month Moving Average forecasts
monthly["MA_Forecast"] = (
    monthly["Amount"].rolling(window=6).mean().shift(1)
)

# Generate rolling one-step-ahead SES forecasts
ses_forecasts = []

for i in range(len(monthly)):
    if i < 6:
        ses_forecasts.append(float("nan"))
        continue

    history = monthly.loc[:i - 1, "Amount"]

    model = SimpleExpSmoothing(
        history,
        initialization_method="estimated"
    ).fit(
        smoothing_level=SES_ALPHA,
        optimized=False
    )

    ses_forecasts.append(float(model.forecast(1).iloc[0]))

monthly["SES_Forecast"] = ses_forecasts

# Load classified transactions
transactions = pd.read_csv(
    "results/classified_transactions.csv"
)
transactions["Date"] = pd.to_datetime(
    transactions["Date"],
    format="mixed",
    dayfirst=True
)
transactions["Month"] = transactions["Date"].dt.to_period("M")

# Load recorded income for retrospective evaluation
original = pd.read_csv(
    "data/Daily Household Transactions.csv"
)
original["Date"] = pd.to_datetime(
    original["Date"],
    format="mixed",
    dayfirst=True
)
original["Month"] = original["Date"].dt.to_period("M")

income_data = (
    original[original["Income/Expense"] == "Income"]
    .groupby("Month")["Amount"]
    .sum()
)

results = []

test_months = monthly[
    (monthly["Month"] >= "2018-01-01") &
    (monthly["Month"] <= "2018-08-01")
]

for _, row in test_months.iterrows():
    month = row["Month"].to_period("M")
    income = income_data.get(month, float("nan"))

    if pd.isna(income) or income <= 0:
        continue

    actual_consumption = row["Amount"]

    # Historical category shares: no future spending used
    history = transactions[
        (transactions["Month"] < month) &
        (transactions["Budget_Type"] != "Excluded")
    ]

    category_totals = history.groupby(
        "Budget_Type"
    )["Amount"].sum()

    shares = category_totals / category_totals.sum()

    # Actual recorded Needs spending in the test month
    actual = transactions[
        (transactions["Month"] == month) &
        (transactions["Budget_Type"] != "Excluded")
    ]

    actual_needs = actual.loc[
        actual["Budget_Type"] == "Needs", "Amount"
    ].sum()

    # Evaluate both forecast-based methods
    for method, forecast in [
        ("Moving Average", row["MA_Forecast"]),
        ("SES", row["SES_Forecast"])
    ]:
        spending_budget = min(
            max(0, forecast),
            income * (1 - SAVINGS_RATE)
        )

        needs_budget = (
            spending_budget * shares.get("Needs", 0)
        )

        results.append({
            "Month": str(month),
            "Method": method,
            "Forecast": forecast,
            "Income": income,
            "Actual_Consumption": actual_consumption,
            "Consumption_Budget": spending_budget,
            "Needs_Budget": needs_budget,
            "Savings_Allocation": income - spending_budget,
            "Budget_Overrun": max(
                0, actual_consumption - spending_budget
            ),
            "Needs_Covered": actual_needs <= needs_budget
        })

    # Traditional 50/30/20 baseline
    baseline_spending = income * 0.80
    baseline_needs = income * 0.50

    results.append({
        "Month": str(month),
        "Method": "50/30/20",
        "Forecast": float("nan"),
        "Income": income,
        "Actual_Consumption": actual_consumption,
        "Consumption_Budget": baseline_spending,
        "Needs_Budget": baseline_needs,
        "Savings_Allocation": income * 0.20,
        "Budget_Overrun": max(
            0, actual_consumption - baseline_spending
        ),
        "Needs_Covered": actual_needs <= baseline_needs
    })

results_df = pd.DataFrame(results)

# Save monthly results
results_df.to_csv(
    "results/forecast_budget_comparison.csv",
    index=False
)

# Summarize performance by method
summary = (
    results_df.groupby("Method")
    .agg(
        Months=("Month", "count"),
        Average_Savings=("Savings_Allocation", "mean"),
        Average_Overrun=("Budget_Overrun", "mean"),
        Needs_Coverage=("Needs_Covered", "mean"),
        Months_With_Overrun=(
            "Budget_Overrun",
            lambda x: (x > 0).sum()
        )
    )
    .reset_index()
)

summary.to_csv(
    "results/forecast_budget_summary.csv",
    index=False
)

print("\nFORECAST-BASED BUDGET COMPARISON")
print(
    results_df[[
        "Month",
        "Method",
        "Forecast",
        "Consumption_Budget",
        "Savings_Allocation",
        "Budget_Overrun"
    ]].round(2).to_string(index=False)
)

print("\nSUMMARY BY METHOD")
print(summary.round(2).to_string(index=False))

print("\nResults saved:")
print("results/forecast_budget_comparison.csv")
print("results/forecast_budget_summary.csv")
