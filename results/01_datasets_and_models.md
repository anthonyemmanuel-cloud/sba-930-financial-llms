# Datasets and models

## FRED series downloaded

| Series ID | Dataset | Description |
| --- | --- | --- |
| CPIAUCSL | 1. Economic indicators | Consumer Price Index for all urban consumers (monthly) |
| GDPC1 | 1. Economic indicators | Real GDP in billions of chained 2017 dollars (quarterly), turned into annualized growth % |
| UNRATE | 1. Economic indicators | Unemployment rate, percent (monthly) |
| FEDFUNDS | 1. Economic indicators | Federal funds interest rate, percent (monthly) |
| DGS10 | 1. Economic indicators | 10-year Treasury yield, percent (daily) |
| T10Y2Y | 1. Economic indicators | 10-year minus 2-year Treasury yield spread (daily) |
| SP500 | 2. Market and commodity prices | S&P 500 stock index (daily) |
| MCOILWTICO | 2. Market and commodity prices | WTI crude oil price, dollars per barrel (monthly) |
| VIXCLS | 2. Market and commodity prices | VIX stock market volatility index (daily) |
| BAA10Y | 2. Market and commodity prices | Baa corporate bond yield minus 10-year Treasury yield (daily) |
| NFCI | 2. Market and commodity prices | Chicago Fed National Financial Conditions Index (weekly) |

## Prepared columns

| Column | First | Last | Values | Missing inside range |
| --- | --- | --- | --- | --- |
| inflation | 1948-01-01 | 2026-09-01 | 944 | 1 |
| fed_funds | 1954-07-01 | 2026-10-01 | 868 | 0 |
| unemployment | 1948-01-01 | 2026-10-01 | 945 | 1 |
| treasury_10y | 1962-01-01 | 2026-11-01 | 779 | 0 |
| yield_curve | 1976-06-01 | 2026-11-01 | 606 | 0 |
| sp500 | 2016-11-01 | 2026-11-01 | 121 | 0 |
| oil | 1986-01-01 | 2026-10-01 | 490 | 0 |
| vix | 1990-01-01 | 2026-11-01 | 443 | 0 |
| vix_max | 1990-01-01 | 2026-11-01 | 443 | 0 |
| credit_spread | 1986-01-01 | 2026-11-01 | 491 | 0 |
| nfci | 1971-01-01 | 2026-11-01 | 671 | 0 |
| gdp | 1947-04-01 | 2026-07-01 | 318 | 0 |

## Models

| Short name | Company | Groq model id | Training data cutoff |
| --- | --- | --- | --- |
| gpt-oss-20b | OpenAI | openai/gpt-oss-20b | 2024-06 |
| gpt-oss-120b | OpenAI | openai/gpt-oss-120b | 2024-06 |

## Forecast windows

Seen windows (both models may remember these years): 2021-12, 2022-06, 2022-12 and 2021Q4, 2022Q2, 2022Q4.

Unseen windows (after both training cutoffs): 2024-12, 2025-06, 2025-12 and 2024Q2, 2024Q4, 2025Q2.
