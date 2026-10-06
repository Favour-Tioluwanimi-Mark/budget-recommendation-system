import pandas as pd

# Load dataset
df = pd.read_csv("data/Daily Household Transactions.csv")

# Keep only expenses
expenses = df[df["Income/Expense"] == "Expense"].copy()

# Count transactions and total spending by category and subcategory
category_summary = (
    expenses.groupby(["Category", "Subcategory"], dropna=False)
    .agg(
        Transaction_Count=("Amount", "count"),
        Total_Amount=("Amount", "sum")
    )
    .reset_index()
)

# Sort so related categories stay together
category_summary = category_summary.sort_values(
    by=["Category", "Total_Amount"],
    ascending=[True, False]
)

print("\nEXPENSE CATEGORY AND SUBCATEGORY SUMMARY\n")
print(category_summary.to_string(index=False))

# Save results for later classification into Needs/Wants/Savings
category_summary.to_csv(
    "results/category_subcategory_summary.csv",
    index=False
)

print(
    "\nSaved category analysis to "
    "results/category_subcategory_summary.csv"
)