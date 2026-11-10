
import pandas as pd

# Categories excluded from consumption spending
EXCLUDED = {
    "investment",
    "recurring deposit",
    "public provident fund",
    "money transfer"
}

NEEDS_CATEGORIES = {
    "cook", "documents", "education", "health",
    "rent", "maid", "garbage disposal",
    "water (jar /tanker)"
}

WANTS_CATEGORIES = {
    "beauty", "culture", "festivals", "gift",
    "grooming", "self-development", "social life",
    "tourism"
}

SUBCATEGORY_RULES = {
    "food": {
        "needs": {
            "grocery", "milk", "fruits", "vegetables",
            "flour mill", "eggs", "bread", "water",
            "onions", "curd", "potato", "breakfast"
        },
        "wants": {
            "eating out", "ice cream", "sweets",
            "chocolate"
        }
    },
    "family": {
        "needs": {"exam fee", "medicine"},
        "wants": {"gift", "makeup"}
    },
    "household": {
        "needs": {"kirana", "toiletries", "kitchen"},
        "wants": {"home decor"}
    },
    "subscription": {
        "needs": {
            "mobile service provider",
            "wifi internet service",
            "mahanagar gas"
        },
        "wants": {
            "netflix", "amazon prime", "hotstar",
            "ott platform", "kindle unlimited",
            "audible", "cable tv", "tata sky"
        }
    },
    "transportation": {
        "needs": {
            "taxi", "train", "auto", "bus", "petrol"
        },
        "wants": {"ropeway"}
    },
    "apparel": {
        "needs": {"laundry"}
    }
}


def classify_transaction(category, subcategory):
    category = str(category).strip().lower()
    subcategory = (
        "" if pd.isna(subcategory)
        else str(subcategory).strip().lower()
    )

    if category in EXCLUDED:
        return "Excluded"

    if category in NEEDS_CATEGORIES:
        return "Needs"

    if category in WANTS_CATEGORIES:
        return "Wants"

    rules = SUBCATEGORY_RULES.get(category, {})

    if subcategory in rules.get("needs", set()):
        return "Needs"

    if subcategory in rules.get("wants", set()):
        return "Wants"

    return "Unclassified"


# Load original transactions
df = pd.read_csv("data/Daily Household Transactions.csv")

df["Date"] = pd.to_datetime(
    df["Date"], format="mixed", dayfirst=True
)

# Only complete months used in our forecasting experiment
df = df[
    (df["Date"] >= "2015-01-01") &
    (df["Date"] < "2018-09-01")
].copy()

# Keep expense transactions, not income or transfers
df = df[df["Income/Expense"] == "Expense"].copy()

# Classify each expense
df["Budget_Type"] = df.apply(
    lambda row: classify_transaction(
        row["Category"], row["Subcategory"]
    ),
    axis=1
)

# Save all classified expense transactions
df.to_csv(
    "results/classified_transactions.csv",
    index=False
)

print("\nCLASSIFICATION SUMMARY")
print(
    df.groupby("Budget_Type")["Amount"]
    .agg(["count", "sum"])
)

# Inspect ambiguous transactions
review = df[df["Budget_Type"] == "Unclassified"].copy()

review_summary = (
    review.groupby(
        ["Category", "Subcategory"],
        dropna=False
    )["Amount"]
    .agg(["count", "sum"])
    .reset_index()
    .sort_values("sum", ascending=False)
)

review_summary.to_csv(
    "results/classification_review.csv",
    index=False
)

print("\nTRANSACTIONS REQUIRING REVIEW")
print(review_summary.to_string(index=False))

# Check whether consumption totals match forecasting
monthly_spending = pd.read_csv(
    "results/monthly_spending.csv"
)

forecast_total = monthly_spending["Amount"].sum()

classified_consumption = df[
    df["Budget_Type"] != "Excluded"
]["Amount"].sum()

print("\nRECONCILIATION")
print(f"Forecast consumption total: INR {forecast_total:.2f}")
print(f"Classified consumption total: INR {classified_consumption:.2f}")
print(
    f"Difference: INR "
    f"{classified_consumption - forecast_total:.2f}"
)

print("\nSaved results/classified_transactions.csv")
print("Saved results/classification_review.csv")
