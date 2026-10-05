import pandas as pd
from statsmodels.tsa.holtwinters import SimpleExpSmoothing
from sklearn.metrics import mean_absolute_error, root_mean_squared_error

# Load the same monthly spending data used for Moving Average
monthly_spending = pd.read_csv("results/monthly_spending.csv")

monthly_spending["Month"] = pd.to_datetime(monthly_spending["Month"])

print(monthly_spending.head())
print(f"\nNumber of months: {len(monthly_spending)}")

# Same chronological split used for the Moving Average experiment
training = monthly_spending[
    monthly_spending["Month"] < "2017-07-01"
].copy()

validation = monthly_spending[
    (monthly_spending["Month"] >= "2017-07-01")
    & (monthly_spending["Month"] <= "2017-12-01")
].copy()

test = monthly_spending[
    monthly_spending["Month"] >= "2018-01-01"
].copy()

print("\nTraining months:", len(training))
print("Validation months:", len(validation))
print("Test months:", len(test))

alpha_values = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]

results = []

for alpha in alpha_values:

    model = SimpleExpSmoothing(
        training["Amount"],
        initialization_method="estimated"
    ).fit(
        smoothing_level=alpha,
        optimized=False
    )

    predictions = model.forecast(len(validation))

    mae = mean_absolute_error(
        validation["Amount"],
        predictions
    )

    rmse = root_mean_squared_error(
        validation["Amount"],
        predictions
    )

    results.append({
        "Alpha": alpha,
        "MAE": mae,
        "RMSE": rmse
    })

results_df = pd.DataFrame(results)

print("\nExponential Smoothing Validation Results:")
print(results_df)

# Select the best alpha based on validation performance
best_alpha = 0.5


history = monthly_spending[
    monthly_spending["Month"] < "2018-01-01"
]["Amount"].tolist()

rolling_predictions = []

for actual in test["Amount"]:

    model = SimpleExpSmoothing(
        history,
        initialization_method="estimated"
    ).fit(
        smoothing_level=best_alpha,
        optimized=False
    )

    # Predict the next month
    prediction = model.forecast(1)[0]
    rolling_predictions.append(prediction)

    # Add the actual month's spending before predicting the next month
    history.append(actual)

test_mae = mean_absolute_error(
    test["Amount"],
    rolling_predictions
)

test_rmse = root_mean_squared_error(
    test["Amount"],
    rolling_predictions
)

print("\nSelected Alpha:", best_alpha)
print(f"Rolling Test MAE: {test_mae:.2f}")
print(f"Rolling Test RMSE: {test_rmse:.2f}")

comparison = pd.DataFrame({
    "Month": test["Month"].values,
    "Actual": test["Amount"].values,
    "SES_Prediction": rolling_predictions
})

print("\nRolling Test Predictions:")
print(comparison)

import matplotlib.pyplot as plt

# Get the Moving Average predictions for the test period
monthly_spending["MA_6"] = (
    monthly_spending["Amount"]
    .rolling(window=6)
    .mean()
    .shift(1)
)

test_comparison = monthly_spending[
    monthly_spending["Month"] >= "2018-01-01"
].copy()

test_comparison["SES"] = rolling_predictions

plt.figure(figsize=(10, 5))

plt.plot(
    test_comparison["Month"],
    test_comparison["Amount"],
    marker="o",
    label="Actual Spending"
)

plt.plot(
    test_comparison["Month"],
    test_comparison["MA_6"],
    marker="o",
    label="6-Month Moving Average"
)

plt.plot(
    test_comparison["Month"],
    test_comparison["SES"],
    marker="o",
    label="Exponential Smoothing"
)

plt.title("Forecasting Method Comparison")
plt.xlabel("Month")
plt.ylabel("Spending (INR)")
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()

plt.savefig("results/forecasting_comparison.png")
plt.show()