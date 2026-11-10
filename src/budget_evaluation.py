
import pandas as pd

MIN_SAVINGS_RATE = 0.20

# Load monthly consumption and classified transactions
monthly = pd.read_csv("results/monthly_spending.csv")
monthly["Month"] = pd.to_datetime(monthly["Month"])

transactions = pd.read_csv("results/classified_transactions.csv")
transactions["Date"] = pd.to_datetime(
    transactions["Date"], format="mixed", dayfirst=True
)
transactions["Month"] = transactions["Date"].dt.to_period("M")

# Load monthly income from the original dataset
original = pd.read_csv("data/Daily Household Transactions.csv")
original["Date"] = pd.to_datetime(
    original["Date"], format="mixed", dayfirst=True
)
original["Month"] = original["Date"].dt.to_period("M")

income_data = original[
    original["Income/Expense"] == "Income"
].groupby("Month")["Amount"].sum()

# Recreate the selected 6-month Moving Average
monthly["Forecast"] = (
    monthly["Amount"].rolling(6).mean().shift(1)
)

results = []

# Evaluate the eight held-out test months
test_months = monthly[
    monthly["Month"] >= "2018-01-01"
]

for _, row in test_months.iterrows():

    month = row["Month"].to_period("M")
    forecast = row["Forecast"]
    actual_consumption = row["Amount"]

    income = income_data.get(month, float("nan"))

    if pd.isna(income) or income <= 0:
        continue

    # Only use spending history from before this month
    history = transactions[
        (transactions["Month"] < month) &
        (transactions["Budget_Type"] != "Excluded")
    ]

    category_totals = history.groupby(
        "Budget_Type"
    )["Amount"].sum()

    shares = category_totals / category_totals.sum()

    # Personalized recommendation
    spending_cap = income * (1 - MIN_SAVINGS_RATE)
    personal_spending = min(forecast, spending_cap)

    personal_needs = (
        personal_spending * shares.get("Needs", 0)
    )
    personal_wants = (
        personal_spending * shares.get("Wants", 0)
    )
    personal_unclassified = (
        personal_spending * shares.get("Unclassified", 0)
    )
    personal_savings = income - personal_spending

    # Traditional 50/30/20 recommendation
    baseline_needs = income * 0.50
    baseline_wants = income * 0.30
    baseline_savings = income * 0.20
    baseline_spending = baseline_needs + baseline_wants

    # Actual spending by category for the test month
    actual = transactions[
        (transactions["Month"] == month) &
        (transactions["Budget_Type"] != "Excluded")
    ]

    actual_totals = actual.groupby(
        "Budget_Type"
    )["Amount"].sum()

    actual_needs = actual_totals.get("Needs", 0)
    actual_unclassified = actual_totals.get(
        "Unclassified", 0
    )

    results.append({
        "Month": str(month),
        "Income": income,
        "Forecast": forecast,
        "Actual_Consumption": actual_consumption,
        "Actual_Needs": actual_needs,
        "Actual_Unclassified": actual_unclassified,

        "Personal_Consumption_Budget": personal_spending,
        "Baseline_Consumption_Budget": baseline_spending,

        "Personal_Needs_Budget": personal_needs,
        "Baseline_Needs_Budget": baseline_needs,

        "Personal_Wants_Budget": personal_wants,
        "Personal_Unclassified_Budget": personal_unclassified,

        "Personal_Savings": personal_savings,
        "Baseline_Savings": baseline_savings,

        "Personal_Overrun": max(
            0, actual_consumption - personal_spending
        ),
        "Baseline_Overrun": max(
            0, actual_consumption - baseline_spending
        ),

        "Personal_Needs_Covered": (
            actual_needs <= personal_needs
        ),
        "Baseline_Needs_Covered": (
            actual_needs <= baseline_needs
        )
    })

results_df = pd.DataFrame(results)

results_df.to_csv(
    "results/budget_evaluation.csv",
    index=False
)

print("\nMONTHLY BUDGET EVALUATION")
print(results_df[[
    "Month", "Income", "Actual_Consumption",
    "Personal_Consumption_Budget",
    "Baseline_Consumption_Budget",
    "Personal_Overrun", "Baseline_Overrun"
]].to_string(index=False))

print("\nEVALUATION SUMMARY")

print(
    "Personalized needs coverage:",
    f"{results_df['Personal_Needs_Covered'].mean():.2%}"
)
print(
    "Baseline needs coverage:",
    f"{results_df['Baseline_Needs_Covered'].mean():.2%}"
)

print(
    "Average personalized overrun: INR",
    f"{results_df['Personal_Overrun'].mean():,.2f}"
)
print(
    "Average baseline overrun: INR",
    f"{results_df['Baseline_Overrun'].mean():,.2f}"
)

print(
    "Average personalized savings allocation: INR",
    f"{results_df['Personal_Savings'].mean():,.2f}"
)
print(
    "Average baseline savings allocation: INR",
    f"{results_df['Baseline_Savings'].mean():,.2f}"
)

print(
    "Unclassified share of test consumption:",
    f"{results_df['Actual_Unclassified'].sum() / results_df['Actual_Consumption'].sum():.2%}"
)

print("\nSaved results/budget_evaluation.csv")
