
import pandas as pd

MIN_SAVINGS_RATE = 0.20


def recommend_budget(income, forecast, spending_shares):
    """
    Recommend a budget using predicted spending,
    historical spending patterns, and a savings target.
    """

    if income <= 0:
        raise ValueError("Income must be greater than zero.")

    if forecast < 0:
        raise ValueError("Forecast cannot be negative.")

    # Reserve at least 20% of income for savings
    minimum_savings = income * MIN_SAVINGS_RATE

    # Maximum consumption allowed after reserving savings
    spending_limit = income - minimum_savings

    # Use the forecast, but do not exceed the spending limit
    recommended_spending = min(forecast, spending_limit)

    # Divide the spending budget using historical patterns
    needs = recommended_spending * spending_shares["Needs"]
    wants = recommended_spending * spending_shares["Wants"]
    unclassified = (
        recommended_spending * spending_shares["Unclassified"]
    )

    # Whatever is not allocated to spending goes to savings
    savings = income - recommended_spending

    return {
        "Needs": needs,
        "Wants": wants,
        "Unclassified": unclassified,
        "Savings": savings,
        "Total_Consumption": recommended_spending
    }


def rule_based_budget(income):
    """
    Traditional 50/30/20 budget.
    """

    return {
        "Needs": income * 0.50,
        "Wants": income * 0.30,
        "Savings": income * 0.20,
        "Total_Consumption": income * 0.80
    }


# Load classified historical transactions
transactions = pd.read_csv(
    "results/classified_transactions.csv"
)

transactions["Date"] = pd.to_datetime(
    transactions["Date"],
    format="mixed",
    dayfirst=True
)

# For this demonstration, use only transactions
# before January 2018 to calculate historical shares.
history = transactions[
    transactions["Date"] < "2018-01-01"
].copy()

history = history[
    history["Budget_Type"] != "Excluded"
]

category_totals = history.groupby(
    "Budget_Type"
)["Amount"].sum()

total = category_totals.sum()

spending_shares = {
    category: category_totals.get(category, 0) / total
    for category in ["Needs", "Wants", "Unclassified"]
}

print("\nHISTORICAL SPENDING SHARES")
for category, share in spending_shares.items():
    print(f"{category}: {share:.2%}")


# Example using January 2018
# Use only information available before January 2018.
income = 60000

# The January 2018 forecast from our selected
# 6-month Moving Average model
monthly = pd.read_csv("results/monthly_spending.csv")

monthly["Month"] = pd.to_datetime(monthly["Month"])

monthly["MA_6"] = (
    monthly["Amount"]
    .rolling(window=6)
    .mean()
    .shift(1)
)

forecast = monthly.loc[
    monthly["Month"] == "2018-01-01",
    "MA_6"
].iloc[0]

personalized = recommend_budget(
    income, forecast, spending_shares
)

baseline = rule_based_budget(income)

print("\nJANUARY 2018 BUDGET COMPARISON")
print(f"Assumed monthly income: INR {income:,.2f}")
print(f"Predicted spending: INR {forecast:,.2f}")

print("\nPersonalized Budget:")
for category, amount in personalized.items():
    print(f"{category}: INR {amount:,.2f}")

print("\n50/30/20 Budget:")
for category, amount in baseline.items():
    print(f"{category}: INR {amount:,.2f}")
