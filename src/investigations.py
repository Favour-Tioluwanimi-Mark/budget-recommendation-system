from data_processing import df, expenses, transfers, spending


# -----------------------------------
# Dataset structure investigation
# -----------------------------------

print("\nFIRST FIVE ROWS:")
print(df.head())

print("\nDATASET SIZE:")
print(df.shape)

print("\nCOLUMNS:")
print(df.columns.tolist())

print("\nDATASET INFO:")
df.info()


# -----------------------------------
# Transaction type investigation
# -----------------------------------

print("\nTRANSACTION TYPES:")
print(df["Income/Expense"].value_counts())


# -----------------------------------
# Transfer-Out investigation
# -----------------------------------

print("\nTRANSFER-OUT TRANSACTIONS:")
print(
    transfers[
        ["Date", "Category", "Subcategory", "Amount"]
    ].head(20)
)


# -----------------------------------
# Expense category investigation
# -----------------------------------

print("\nEXPENSE CATEGORIES:")
print(expenses["Category"].value_counts())


# -----------------------------------
# Questionable expense investigation
# -----------------------------------

questionable_categories = [
    "Investment",
    "Recurring Deposit",
    "Public Provident Fund",
    "Money transfer"
]

questionable_expenses = expenses[
    expenses["Category"].isin(questionable_categories)
]

print("\nQUESTIONABLE EXPENSE CATEGORIES:")
print(
    questionable_expenses[
        ["Date", "Category", "Subcategory", "Note", "Amount"]
    ].to_string(index=False)
)


# -----------------------------------
# High-spending month investigation
# -----------------------------------

high_spending_months = spending[
    spending["Month"].isin([
        "2017-08",
        "2018-01"
    ])
]

print("\nTRANSACTIONS IN HIGH-SPENDING MONTHS:")
print(
    high_spending_months[
        ["Date", "Category", "Subcategory", "Note", "Amount"]
    ]
    .sort_values("Amount", ascending=False)
    .to_string(index=False)
)