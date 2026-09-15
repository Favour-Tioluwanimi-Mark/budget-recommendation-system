import pandas as pd
import matplotlib.pyplot as plt


# Load the dataset
df = pd.read_csv("data/Daily Household Transactions.csv")


# Convert Date column from text to datetime
df["Date"] = pd.to_datetime(
    df["Date"],
    format="mixed",
    dayfirst=True
)


# Separate transactions by type
expenses = df[df["Income/Expense"] == "Expense"].copy()
income = df[df["Income/Expense"] == "Income"].copy()
transfers = df[df["Income/Expense"] == "Transfer-Out"].copy()


# Categories that represent savings or investments rather than spending
savings_categories = [
    "Investment",
    "Recurring Deposit",
    "Public Provident Fund"
]


# Create clean spending data by excluding savings/investments
# and ambiguous money transfers
spending = expenses[
    ~expenses["Category"].isin(
        savings_categories + ["Money transfer"]
    )
].copy()


# Create a month column for each spending transaction
spending["Month"] = spending["Date"].dt.to_period("M")


# Calculate total spending for each month
monthly_spending = (
    spending.groupby("Month")["Amount"]
    .sum()
    .reset_index()
)


# Calculate monthly spending for each category
monthly_by_category = spending.pivot_table(
    index="Month",
    columns="Category",
    values="Amount",
    aggfunc="sum",
    fill_value=0
)


# Convert Month to a timestamp for plotting
monthly_spending["Month"] = monthly_spending["Month"].dt.to_timestamp()

# Remove September 2018 because it is an incomplete month
complete_monthly_spending = monthly_spending[
    monthly_spending["Month"] < "2018-09-01"
].copy()

# Save the complete monthly spending data for forecasting
complete_monthly_spending.to_csv(
    "results/monthly_spending.csv",
    index=False
)

print(
    f"Saved {len(complete_monthly_spending)} complete months "
    "for forecasting."
)


# Create a line graph of monthly spending
plt.figure(figsize=(10, 5))

plt.plot(
    monthly_spending["Month"],
    monthly_spending["Amount"],
    marker="o"
)

plt.title("Monthly Spending Over Time")
plt.xlabel("Month")
plt.ylabel("Total Spending (INR)")

plt.xticks(rotation=45)
plt.tight_layout()

plt.savefig("results/monthly_spending.png")
plt.show()