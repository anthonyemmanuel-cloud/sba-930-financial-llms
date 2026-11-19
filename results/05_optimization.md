# Requirement 4: Optimization and enhancement

Methods tested. Optimized prompt = analyst role, calculated statistics, a step by step method that starts from the naive forecast, temperature 0 and JSON mode. Self-consistency = the optimized prompt asked 3 times at temperature 0.7, keeping the median. Ensemble = the average of both models' optimized forecasts.

## Accuracy by method

| Task | Method | Model | Readable answers | Avg error | Naive error | Skill vs naive | Direction right | Actual inside range |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Stock market (S&P 500, 6-month % change) | Baseline prompt | gpt-oss-20b | 6/6 | 8.95 | 10.55 | 15% | 67% | 0% |
| Stock market (S&P 500, 6-month % change) | Baseline prompt | gpt-oss-120b | 6/6 | 11.45 | 10.55 | -9% | 50% | 17% |
| Stock market (S&P 500, 6-month % change) | Optimized prompt | gpt-oss-20b | 6/6 | 10.05 | 10.55 | 5% | 50% | 17% |
| Stock market (S&P 500, 6-month % change) | Optimized prompt | gpt-oss-120b | 6/6 | 11.85 | 10.55 | -12% | 50% | 17% |
| Stock market (S&P 500, 6-month % change) | Ensemble of both models (optimized) | ensemble | 6/6 | 10.87 | 10.55 | -3% | 50% | 17% |
| Commodity (WTI oil, $ per barrel) | Baseline prompt | gpt-oss-20b | 6/6 | 19.87 | 15.94 | -25% | 33% | 17% |
| Commodity (WTI oil, $ per barrel) | Baseline prompt | gpt-oss-120b | 6/6 | 19.80 | 15.94 | -24% | 67% | 33% |
| Commodity (WTI oil, $ per barrel) | Optimized prompt | gpt-oss-20b | 6/6 | 18.75 | 15.94 | -18% | 67% | 33% |
| Commodity (WTI oil, $ per barrel) | Optimized prompt | gpt-oss-120b | 6/6 | 16.50 | 15.94 | -4% | 67% | 33% |
| Commodity (WTI oil, $ per barrel) | Optimized + self-consistency (median of 3) | gpt-oss-20b | 6/6 | 18.37 | 15.94 | -15% | 67% | 33% |
| Commodity (WTI oil, $ per barrel) | Optimized + self-consistency (median of 3) | gpt-oss-120b | 6/6 | 17.97 | 15.94 | -13% | 50% | 33% |
| Commodity (WTI oil, $ per barrel) | Ensemble of both models (optimized) | ensemble | 6/6 | 17.60 | 15.94 | -10% | 67% | 33% |
| CPI inflation (%) | Baseline prompt | gpt-oss-20b | 6/6 | 1.01 | 0.86 | -17% | 67% | 33% |
| CPI inflation (%) | Baseline prompt | gpt-oss-120b | 6/6 | 0.87 | 0.86 | -1% | 50% | 17% |
| CPI inflation (%) | Optimized prompt | gpt-oss-20b | 6/6 | 0.98 | 0.86 | -15% | 67% | 33% |
| CPI inflation (%) | Optimized prompt | gpt-oss-120b | 6/6 | 0.79 | 0.86 | 8% | 33% | 33% |
| CPI inflation (%) | Optimized + self-consistency (median of 3) | gpt-oss-20b | 6/6 | 0.69 | 0.86 | 20% | 50% | 33% |
| CPI inflation (%) | Optimized + self-consistency (median of 3) | gpt-oss-120b | 6/6 | 0.80 | 0.86 | 7% | 50% | 33% |
| CPI inflation (%) | Ensemble of both models (optimized) | ensemble | 6/6 | 0.85 | 0.86 | 1% | 50% | 33% |
| Real GDP growth (%) | Baseline prompt | gpt-oss-20b | 6/6 | 1.69 | 2.29 | 26% | 67% | 0% |
| Real GDP growth (%) | Baseline prompt | gpt-oss-120b | 5/6 | 1.47 | 1.64 | 10% | 60% | 0% |
| Real GDP growth (%) | Optimized prompt | gpt-oss-20b | 6/6 | 2.20 | 2.29 | 4% | 67% | 50% |
| Real GDP growth (%) | Optimized prompt | gpt-oss-120b | 6/6 | 2.18 | 2.29 | 5% | 33% | 50% |
| Real GDP growth (%) | Ensemble of both models (optimized) | ensemble | 6/6 | 2.16 | 2.29 | 6% | 50% | 50% |

## Memory test: real dates compared with hidden dates (seen windows only)

If the error rises a lot when the dates are hidden, the model was probably remembering history instead of forecasting from the data.

| Task | Model | Error with real dates | Error with dates hidden | Naive error |
| --- | --- | --- | --- | --- |
| Commodity (WTI oil, $ per barrel) | gpt-oss-20b | 26.51 | 29.16 | 19.98 |
| Commodity (WTI oil, $ per barrel) | gpt-oss-120b | 25.72 | 29.26 | 19.98 |
| CPI inflation (%) | gpt-oss-20b | 1.46 | 1.36 | 1.31 |
| CPI inflation (%) | gpt-oss-120b | 1.23 | 1.05 | 1.31 |
| Real GDP growth (%) | gpt-oss-20b | 1.84 | 2.00 | 2.89 |
| Real GDP growth (%) | gpt-oss-120b | 1.48 | 2.29 | 1.56 |
| Stock market (S&P 500, 6-month % change) | gpt-oss-20b | 13.14 | 17.07 | 12.64 |
| Stock market (S&P 500, 6-month % change) | gpt-oss-120b | 18.84 | 18.01 | 12.64 |

## Consistency of repeated answers (self-consistency samples)

Spread is the standard deviation of the final forecast across the 3 samples. Lower means more consistent.

| Model | Task | Cutoff | Spread |
| --- | --- | --- | --- |
| gpt-oss-20b | Commodity (WTI oil, $ per barrel) | 2021-12 | 0.92 |
| gpt-oss-20b | Commodity (WTI oil, $ per barrel) | 2022-06 | 13.19 |
| gpt-oss-20b | Commodity (WTI oil, $ per barrel) | 2022-12 | 5.14 |
| gpt-oss-20b | Commodity (WTI oil, $ per barrel) | 2024-12 | 0.80 |
| gpt-oss-20b | Commodity (WTI oil, $ per barrel) | 2025-06 | 0.76 |
| gpt-oss-20b | Commodity (WTI oil, $ per barrel) | 2025-12 | 1.43 |
| gpt-oss-20b | CPI inflation (%) | 2021-12 | 0.59 |
| gpt-oss-20b | CPI inflation (%) | 2022-06 | 0.12 |
| gpt-oss-20b | CPI inflation (%) | 2022-12 | 0.72 |
| gpt-oss-20b | CPI inflation (%) | 2024-12 | 0.17 |
| gpt-oss-20b | CPI inflation (%) | 2025-06 | 0.08 |
| gpt-oss-20b | CPI inflation (%) | 2025-12 | 0.25 |
| gpt-oss-120b | Commodity (WTI oil, $ per barrel) | 2021-12 | 1.25 |
| gpt-oss-120b | Commodity (WTI oil, $ per barrel) | 2022-06 | 4.28 |
| gpt-oss-120b | Commodity (WTI oil, $ per barrel) | 2022-12 | 0.85 |
| gpt-oss-120b | Commodity (WTI oil, $ per barrel) | 2024-12 | 2.14 |
| gpt-oss-120b | Commodity (WTI oil, $ per barrel) | 2025-06 | 1.54 |
| gpt-oss-120b | Commodity (WTI oil, $ per barrel) | 2025-12 | 0.85 |
| gpt-oss-120b | CPI inflation (%) | 2021-12 | 0.29 |
| gpt-oss-120b | CPI inflation (%) | 2022-06 | 0.08 |
| gpt-oss-120b | CPI inflation (%) | 2022-12 | 0.00 |
| gpt-oss-120b | CPI inflation (%) | 2024-12 | 0.28 |
| gpt-oss-120b | CPI inflation (%) | 2025-06 | 0.17 |
| gpt-oss-120b | CPI inflation (%) | 2025-12 | 0.21 |
