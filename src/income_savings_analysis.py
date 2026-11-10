import pandas as pd

# Load the original transaction dataset
df = pd.read_csv("data/Daily Household Transactions.csv")

# Convert the Date column
df["Date"] = pd.to_datetime(
    df["Date"],
    format="mixed",
    dayfirst=True
)

# Create a Month column
df["Month"] = df["Date"].dt.to_period("M")


# -----------------------------
# 1. Analyze monthly income
# -----------------------------

income = df[df["Income/Expense"] == "Income"].copy()

monthly_income = (
    income.groupby("Month")["Amount"]
    .sum()
    .reset_index(name="Income")
)

print("\nMONTHLY INCOME")
print(monthly_income.to_string(index=False))

print("\nNumber of months with recorded income:", len(monthly_income))


# -----------------------------
# 2. Analyze savings/investments
# -----------------------------

savings_categories = [
    "Investment",
    "Recurring Deposit",
    "Public Provident Fund",
    "Fixed Deposit",
    "Equity Mutual Fund A",
    "Equity Mutual Fund B",
    "Equity Mutual Fund C",
    "Equity Mutual Fund D",
    "Equity Mutual Fund E",
    "Equity Mutual Fund F",
    "Share Market",
    "Small cap fund 1",
    "Small Cap fund 2"
]

savings = df[
    df["Category"].isin(savings_categories)
].copy()

monthly_savings = (
    savings.groupby("Month")["Amount"]
    .sum()
    .reset_index(name="Savings")
)

print("\nMONTHLY SAVINGS / INVESTMENTS")
print(monthly_savings.to_string(index=False))

print("\nNumber of months with recorded savings:", len(monthly_savings))


# -----------------------------
# 3. Combine income and savings
# -----------------------------

income_savings = pd.merge(
    monthly_income,
    monthly_savings,
    on="Month",
    how="left"
)

income_savings["Savings"] = income_savings["Savings"].fillna(0)

income_savings["Savings_Rate"] = (
    income_savings["Savings"] / income_savings["Income"]
)

print("\nINCOME AND SAVINGS COMPARISON")
print(income_savings.to_string(index=False))

print(
    "\nAverage savings rate:",
    income_savings["Savings_Rate"].mean()
)

print(
    "Median savings rate:",
    income_savings["Savings_Rate"].median()
)

# Save results
income_savings.to_csv(
    "results/income_savings_analysis.csv",
    index=False
)

print(
    "\nSaved analysis to "
    "results/income_savings_analysis.csv"
)