# Data Investigation Results

## Dataset Overview

The dataset contains 2,461 financial transactions across 8 columns.
The transactions span from January 2015 through September 2018 and include expense, income, and transfer-out transactions.

The main fields used for this project are Date, Category, Amount, and Income/Expense.

## Transaction Type Investigation

The dataset contains:

- 2,176 Expense transactions
- 160 Transfer-Out transactions
- 125 Income transactions

Transfer-Out transactions were investigated separately because money leaving an account does not necessarily represent consumption spending.

## Transfer-Out Investigation

Inspection of Transfer-Out transactions showed that many represented financial movements such as mutual fund contributions, Public Provident Fund contributions, savings account transfers, and share market investments.

Because these transactions generally represent savings investments, or transfers between accounts rather than consumption, they were not included as regular spending expenses.

## Expense Category Investigation

Some transactions labeled as Expense also represented financial
activities rather than consumption.

The following categories were identified:

- Investment
- Recurring Deposit
- Public Provident Fund
- Money transfer

Investment, Recurring Deposit, and Public Provident Fund were excluded from consumption spending because they represent savings or investment activities.

Money transfer transactions were also excluded from consumption
spending because their purpose could not be determined consistently.

After this preprocessing step, 2,000 transactions remained for the spending analysis.

## Monthly Aggregation

The cleaned spending transactions were grouped by month to create a monthly time series.

The dataset produced 45 monthly observations from January 2015 through September 2018.

Spending was also grouped by both month and category to preserve
information about how spending was distributed across categories.

## High-Spending Month Investigation

The monthly spending visualization revealed unusually high spending in August 2017 and January 2018.

The underlying transactions were investigated before deciding whether the observations should be treated as outliers.

August 2017 included a 43,000 INR tourism/travel expense along with other legitimate expenses.

January 2018 included two large two-wheeler installments of 50,000 INR and 43,000 INR.

Because these transactions represent legitimate recorded spending
rather than apparent data errors or misclassified financial transfers, the high-spending months were retained in the dataset.

## Incomplete Final Month

The dataset ends on September 20, 2018. Therefore, September 2018 does not represent a complete month of spending.

The month can remain in the original processed data, but it will not be treated as a complete monthly observation when evaluating forecasting models.

## Moving Average Forecasting Experiment

### Validation and Test Setup

The monthly spending dataset contained 44 complete months from
January 2015 through August 2018. Because this is time-series data, the observations were kept in chronological order rather than randomly shuffled.

The data was divided into the following periods:

- Training/history period: January 2015 - June 2017
- Validation period: July 2017 - December 2017
- Test period: January 2018 - August 2018

The validation period was used to compare different Moving Average window sizes and select the best-performing window. The test period was kept separate and was only used after the Moving Average window had been selected.

This approach prevents the test data from being used to choose the model and provides a more realistic evaluation of how the selected method performs on future unseen spending data.

### Moving Average Window Validation

Three Moving Average window sizes were compared: 3 months, 6 months, and 12 months. Each prediction was calculated using only spending from previous months.

| Window | Validation MAE (INR) | Validation RMSE (INR) |
|--------|---------------------:|----------------------:|
| 3-Month | 26,198.38 | 30,690.08 |
| 6-Month | 19,128.34 | 28,502.13 |
| 12-Month | 23,030.81 | 32,373.02 |

The 6-month Moving Average achieved the lowest MAE and RMSE during validation. Therefore, it was selected as the Moving Average model for testing.

The results suggest that the 3-month window may be more sensitive to short-term changes in spending, while the 12-month window may respond more slowly to recent spending behavior. For this dataset, the 6-month window provided the best validation performance.

### Moving Average Test Results

After selecting the 6-month Moving Average using the validation
period, it was evaluated on the held-out test period from January
2018 through August 2018.

The test results were:

- MAE: 24,013.52 INR
- RMSE: 31,665.27 INR

The higher test error indicates that forecasting spending becomes
more difficult when the test period contains large and irregular
expenses. For example, January 2018 contained unusually high but
legitimate vehicle-related spending.

This highlights an important limitation of Moving Average forecasting: it can adapt to recent historical spending patterns, but it cannot anticipate unexpected large expenses that are not reflected in the preceding months.

These results will later be compared with Exponential Smoothing to determine which forecasting approach provides more accurate budget predictions.