import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import mean_absolute_error, root_mean_squared_error


# Load the monthly spending data
monthly_spending = pd.read_csv(
    "results/monthly_spending.csv"
)


# Convert Month back to datetime
monthly_spending["Month"] = pd.to_datetime(
    monthly_spending["Month"]
)


# Create a 3-month moving average prediction
monthly_spending["MA_3"] = (
    monthly_spending["Amount"]
    .rolling(window=3)
    .mean()
    .shift(1)
)

# Create a 6-month moving average prediction
monthly_spending["MA_6"] = (
    monthly_spending["Amount"]
    .rolling(window=6)
    .mean()
    .shift(1)
)


# Create a 12-month moving average prediction
monthly_spending["MA_12"] = (
    monthly_spending["Amount"]
    .rolling(window=12)
    .mean()
    .shift(1)
)

# Create validation period
validation = monthly_spending[
    (monthly_spending["Month"] >= "2017-07-01") &
    (monthly_spending["Month"] <= "2017-12-01")
].copy()

# Create test period
test = monthly_spending[
    (monthly_spending["Month"] >= "2018-01-01") &
    (monthly_spending["Month"] <= "2018-08-01")
].copy()

# print("\nVALIDATION DATA:")
# print(validation)

# print("\nTEST DATA:")
# print(test)


# Evaluate each moving average window on the validation data
windows = ["MA_3", "MA_6", "MA_12"]

print("\nVALIDATION RESULTS:")

for window in windows:
    mae = mean_absolute_error(
        validation["Amount"],
        validation[window]
    )

    rmse = root_mean_squared_error(
        validation["Amount"],
        validation[window]
    )

    print(
        f"{window}: "
        f"MAE = {mae:.2f}, "
        f"RMSE = {rmse:.2f}"
    )

# Evaluate the selected 6-month moving average on the test data
test_mae = mean_absolute_error(
    test["Amount"],
    test["MA_6"]
)

test_rmse = root_mean_squared_error(
    test["Amount"],
    test["MA_6"]
)

print("\nTEST RESULTS:")
print("Selected model: 6-month Moving Average")
print(f"MAE = {test_mae:.2f}")
print(f"RMSE = {test_rmse:.2f}")

# Plot actual spending and the selected moving average model
plt.figure(figsize=(10, 5))

plt.plot(
    monthly_spending["Month"],
    monthly_spending["Amount"],
    marker="o",
    label="Actual Spending"
)

plt.plot(
    monthly_spending["Month"],
    monthly_spending["MA_6"],
    marker="o",
    label="6-Month Moving Average"
)

plt.title("Actual Spending vs 6-Month Moving Average")
plt.xlabel("Month")
plt.ylabel("Spending (INR)")

plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()

# Save the graph
plt.savefig("results/moving_average_forecast.png")

# Display the graph
plt.show()

# print(monthly_spending.head(15))