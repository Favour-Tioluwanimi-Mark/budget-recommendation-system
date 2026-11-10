import pandas as pd

# Load the original dataset
df = pd.read_csv("data/Daily Household Transactions.csv")

df["Date"] = pd.to_datetime(
    df["Date"],
    format="mixed",
    dayfirst=True
)

df["Month"] = df["Date"].dt.to_period("M")

# Calculate recorded income for each month
income = df[df["Income/Expense"] == "Income"]

monthly_income = (
    income.groupby("Month")["Amount"]
    .sum()
    .reset_index(name="Income")
)

# Load the same consumption spending used in forecasting
monthly_spending = pd.read_csv("results/monthly_spending.csv")

monthly_spending["Month"] = (
    pd.to_datetime(monthly_spending["Month"])
    .dt.to_period("M")
)

monthly_spending = monthly_spending.rename(
    columns={"Amount": "Consumption"}
)

# Combine income and consumption by month
analysis = pd.merge(
    monthly_spending[["Month", "Consumption"]],
    monthly_income,
    on="Month",
    how="left"
)

# Calculate the amount remaining after consumption
analysis["Savings_Capacity"] = (
    analysis["Income"] - analysis["Consumption"]
)

# Calculate the percentage of income remaining
analysis["Savings_Capacity_Rate"] = (
    analysis["Savings_Capacity"] / analysis["Income"]
)

# Identify months where consumption exceeded income
analysis["Overspending"] = (
    analysis["Savings_Capacity"] < 0
)

print("\nMONTHLY SAVINGS CAPACITY")
print(analysis.to_string(index=False))

print("\nSUMMARY")
print("Months analyzed:", len(analysis))
print("Months without recorded income:", analysis["Income"].isna().sum())
print("Months spending exceeded income:", analysis["Overspending"].sum())

print(
    "Median savings capacity rate:",
    analysis["Savings_Capacity_Rate"].median()
)

print(
    "Average savings capacity rate:",
    analysis["Savings_Capacity_Rate"].mean()
)

# Save the results
analysis.to_csv(
    "results/savings_capacity.csv",
    index=False
)

print("\nSaved results/savings_capacity.csv")