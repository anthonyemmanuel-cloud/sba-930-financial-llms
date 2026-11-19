# Requirement 2: Economic trend forecasting

## Summary

| Task | Method | Model | Readable answers | Avg error | Naive error | Skill vs naive | Direction right | Actual inside range |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CPI inflation (%) | Baseline prompt | gpt-oss-20b | 6/6 | 1.01 | 0.86 | -17% | 67% | 33% |
| CPI inflation (%) | Baseline prompt | gpt-oss-120b | 6/6 | 0.87 | 0.86 | -1% | 50% | 17% |
| Real GDP growth (%) | Baseline prompt | gpt-oss-20b | 6/6 | 1.69 | 2.29 | 26% | 67% | 0% |
| Real GDP growth (%) | Baseline prompt | gpt-oss-120b | 5/6 | 1.47 | 1.64 | 10% | 60% | 0% |

## Seen and unseen windows

| Task | Model | Windows | Avg error | Naive error | Skill vs naive | Direction right |
| --- | --- | --- | --- | --- | --- | --- |
| CPI inflation (%) | gpt-oss-20b | seen | 1.46 | 1.31 | -11% | 67% |
| CPI inflation (%) | gpt-oss-20b | unseen | 0.55 | 0.41 | -35% | 67% |
| Real GDP growth (%) | gpt-oss-20b | seen | 1.84 | 2.89 | 36% | 67% |
| Real GDP growth (%) | gpt-oss-20b | unseen | 1.54 | 1.69 | 9% | 67% |
| CPI inflation (%) | gpt-oss-120b | seen | 1.23 | 1.31 | 6% | 67% |
| CPI inflation (%) | gpt-oss-120b | unseen | 0.51 | 0.41 | -25% | 33% |
| Real GDP growth (%) | gpt-oss-120b | seen | 1.48 | 1.56 | 6% | 50% |
| Real GDP growth (%) | gpt-oss-120b | unseen | 1.47 | 1.69 | 13% | 67% |

## Inflation forecasts compared with actual data

| Cutoff | Model | Actual values | Forecast values | Avg error |
| --- | --- | --- | --- | --- |
| 2021-12 | gpt-oss-20b | 7.6, 7.9, 8.6, 8.2, 8.5, 9.0 | 6.0, 5.8, 5.5, 5.3, 5.1, 5.0 | 2.85 |
| 2022-06 | gpt-oss-20b | 8.5, 8.2, 8.2, 7.8, 7.1, 6.4 | 8.5, 8.0, 7.5, 7.0, 6.5, 6.0 | 0.45 |
| 2022-12 | gpt-oss-20b | 6.3, 6.0, 4.9, 5.0, 4.1, 3.1 | 4.5, 4.3, 4.0, 3.8, 3.6, 3.4 | 1.07 |
| 2024-12 | gpt-oss-20b | 3.0, 2.8, 2.4, 2.3, 2.4, 2.7 | 2.5, 2.4, 2.3, 2.2, 2.1, 2.0 | 0.34 |
| 2025-06 | gpt-oss-20b | 2.7, 2.9, 3.0, n/a, 2.7, 2.6 | 2.5, 2.4, 2.3, 2.3, 2.3, 2.4 | 0.43 |
| 2025-12 | gpt-oss-20b | 2.4, 2.4, 3.3, 3.8, 4.2, 3.5 | 2.6, 2.6, 2.5, 2.5, 2.4, 2.4 | 0.88 |
| 2021-12 | gpt-oss-120b | 7.6, 7.9, 8.6, 8.2, 8.5, 9.0 | 6.8, 6.4, 6.0, 5.6, 5.2, 4.8 | 2.50 |
| 2022-06 | gpt-oss-120b | 8.5, 8.2, 8.2, 7.8, 7.1, 6.4 | 8.7, 8.6, 8.5, 8.4, 8.3, 8.2 | 0.76 |
| 2022-12 | gpt-oss-120b | 6.3, 6.0, 4.9, 5.0, 4.1, 3.1 | 6.1, 5.8, 5.4, 5.0, 4.6, 4.2 | 0.42 |
| 2024-12 | gpt-oss-120b | 3.0, 2.8, 2.4, 2.3, 2.4, 2.7 | 2.8, 2.6, 2.5, 2.5, 2.4, 2.4 | 0.16 |
| 2025-06 | gpt-oss-120b | 2.7, 2.9, 3.0, n/a, 2.7, 2.6 | 2.9, 3.1, 3.2, 3.3, 3.5, 3.6 | 0.45 |
| 2025-12 | gpt-oss-120b | 2.4, 2.4, 3.3, 3.8, 4.2, 3.5 | 2.5, 2.5, 2.4, 2.4, 2.3, 2.3 | 0.91 |

### Example reasoning

- **gpt-oss-20b, 2021-12** (confidence 70): CPI peaked in 2021 at ~7.2% and has been declining steadily, suggesting a continued downward trend into early 2022.
- **gpt-oss-20b, 2025-12** (confidence 70): CPI inflation has been steadily falling over the past 18 months and is likely to remain near 2.5-2.6 in the short term.
- **gpt-oss-120b, 2021-12** (confidence 70): After a peak of 7.2% in Dec 2021, inflation has been trending lower as supply chain pressures ease and monetary policy tightens, suggesting a gradual decline over the next six months.
- **gpt-oss-120b, 2025-12** (confidence 70): After a gradual decline from 2023 peaks to around 2.6% in late 2024, inflation has stabilized near the 2.5‑3.0% range, suggesting a modest further decrease over the next six months.

## GDP growth forecasts compared with actual data

| Cutoff | Model | Actual values | Forecast values | Avg error |
| --- | --- | --- | --- | --- |
| 2021Q4 | gpt-oss-20b | -1.0, 0.6, 2.7, 2.7 | 3.5, 2.8, 2.0, 1.5 | 2.15 |
| 2022Q2 | gpt-oss-20b | 2.7, 2.7, 3.4, 2.2 | 0.8, 1.5, 1.2, 0.9 | 1.65 |
| 2022Q4 | gpt-oss-20b | 3.4, 2.2, 4.5, 3.6 | 2.0, 1.8, 1.6, 1.4 | 1.73 |
| 2024Q2 | gpt-oss-20b | 3.2, 2.4, 0.1, 4.0 | 2.5, 2.0, 1.5, 1.0 | 1.38 |
| 2024Q4 | gpt-oss-20b | 0.1, 4.0, 3.9, 0.2 | 2.0, 1.8, 1.6, 1.4 | 1.90 |
| 2025Q2 | gpt-oss-20b | 3.9, 0.2, 2.5, 2.2 | 3.0, 2.5, 1.5, 1.0 | 1.35 |
| 2021Q4 | gpt-oss-120b | -1.0, 0.6, 2.7, 2.7 | no answer | n/a |
| 2022Q2 | gpt-oss-120b | 2.7, 2.7, 3.4, 2.2 | 1.2, 1.5, 1.7, 1.8 | 1.20 |
| 2022Q4 | gpt-oss-120b | 3.4, 2.2, 4.5, 3.6 | 2.1, 1.8, 1.5, 1.3 | 1.75 |
| 2024Q2 | gpt-oss-120b | 3.2, 2.4, 0.1, 4.0 | 2.5, 2.8, 2.6, 2.7 | 1.23 |
| 2024Q4 | gpt-oss-120b | 0.1, 4.0, 3.9, 0.2 | 2.2, 2.5, 2.3, 2.4 | 1.85 |
| 2025Q2 | gpt-oss-120b | 3.9, 0.2, 2.5, 2.2 | 2.0, 2.5, 2.8, 3.0 | 1.32 |

### Example reasoning

- **gpt-oss-20b, 2021Q4** (confidence 70): Recent high growth in 2021 has tapered; a modest but consistent decline is expected over 2022.
- **gpt-oss-20b, 2025Q2** (confidence 60): Recent volatility suggests a rebound in late 2025 followed by a gradual slowdown into 2026; the 2026 second quarter is likely to be modest, with a range reflecting uncertainty.
- **gpt-oss-120b, 2025Q2** (confidence 70): After a weak start in early 2025, recent quarterly data show a rebound, suggesting continued moderate acceleration into 2026.
