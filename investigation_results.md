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

## Simple Exponential Smoothing Experiment

### Method

The second forecasting method evaluated was Simple Exponential Smoothing (SES). Unlike the Moving Average method, which calculates predictions using a fixed window of previous observations, Exponential Smoothing assigns greater weight to more recent observations.

The smoothing parameter, alpha, determines how strongly the forecast responds to recent spending. Rather than selecting an alpha value arbitrarily, alpha values from 0.1 through 0.9 were evaluated using the same validation period used for the Moving Average experiment.

### Alpha Validation Results

| Alpha | Validation MAE (INR) | Validation RMSE (INR) |
|------:|---------------------:|----------------------:|
| 0.1 | 31,232.10 | 37,832.65 |
| 0.2 | 27,361.42 | 34,706.09 |
| 0.3 | 25,756.74 | 33,114.68 |
| 0.4 | 25,271.46 | 32,561.64 |
| 0.5 | 25,163.66 | 32,439.73 |
| 0.6 | 25,218.01 | 32,501.16 |
| 0.7 | 25,376.31 | 32,680.56 |
| 0.8 | 25,650.85 | 32,993.42 |
| 0.9 | 26,083.87 | 33,491.24 |

Alpha = 0.5 produced the lowest validation MAE and RMSE and was therefore selected for the test evaluation.

### Rolling Test Evaluation

To make the comparison with Moving Average consistent, SES was evaluated using rolling one-step-ahead predictions. Each month was predicted using only information available before that month. After the actual spending for that month became available, it was added to the historical data before predicting the following month.

The selected SES model produced:

- Test MAE: 26,702.76 INR
- Test RMSE: 35,622.49 INR

## Preliminary Forecasting Comparison

| Method | Test MAE (INR) | Test RMSE (INR) |
|---|---:|---:|
| 6-Month Moving Average | 24,013.52 | 31,665.27 |
| Simple Exponential Smoothing (alpha = 0.5) | 26,702.76 | 35,622.49 |

Based on both evaluation metrics, the 6-month Moving Average performed better than Simple Exponential Smoothing on the current test period.

One important observation was the effect of irregular spending on the forecasts. January 2018 had actual spending of 112,080.90 INR, while SES predicted 44,419.04 INR. After observing this unusually high month, the SES prediction for February increased to 78,249.97 INR, while actual February spending fell to 16,218 INR.

This suggests that although Exponential Smoothing can respond more quickly to recent spending changes, this responsiveness can also reduce forecasting accuracy when a recent observation represents an unusual expense rather than a continuing change in spending behavior. In comparison, the 6-month Moving Average smooths changes across a longer period, which performed better on this dataset.

These findings are preliminary and are specific to the dataset and evaluation period used in this project.