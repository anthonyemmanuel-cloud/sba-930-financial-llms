# Requirement 1: LLM evaluation for financial forecasting

Avg error is the mean absolute error (percentage points for the stock change, dollars for oil). Naive error is the error of simply assuming no change. Skill vs naive above 0% means the LLM beat the naive forecast. Actual inside range shows how often the real value fell inside the model's own low to high range.

## Summary

| Task | Method | Model | Readable answers | Avg error | Naive error | Skill vs naive | Direction right | Actual inside range |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Stock market (S&P 500, 6-month % change) | Baseline prompt | gpt-oss-20b | 6/6 | 8.95 | 10.55 | 15% | 67% | 0% |
| Stock market (S&P 500, 6-month % change) | Baseline prompt | gpt-oss-120b | 6/6 | 11.45 | 10.55 | -9% | 50% | 17% |
| Commodity (WTI oil, $ per barrel) | Baseline prompt | gpt-oss-20b | 6/6 | 19.87 | 15.94 | -25% | 33% | 17% |
| Commodity (WTI oil, $ per barrel) | Baseline prompt | gpt-oss-120b | 6/6 | 19.80 | 15.94 | -24% | 67% | 33% |

## Seen and unseen windows

| Task | Model | Windows | Avg error | Naive error | Skill vs naive | Direction right |
| --- | --- | --- | --- | --- | --- | --- |
| Stock market (S&P 500, 6-month % change) | gpt-oss-20b | seen | 13.14 | 12.64 | -4% | 33% |
| Stock market (S&P 500, 6-month % change) | gpt-oss-20b | unseen | 4.76 | 8.46 | 44% | 100% |
| Commodity (WTI oil, $ per barrel) | gpt-oss-20b | seen | 26.51 | 19.98 | -33% | 33% |
| Commodity (WTI oil, $ per barrel) | gpt-oss-20b | unseen | 13.23 | 11.89 | -11% | 33% |
| Stock market (S&P 500, 6-month % change) | gpt-oss-120b | seen | 18.84 | 12.64 | -49% | 0% |
| Stock market (S&P 500, 6-month % change) | gpt-oss-120b | unseen | 4.06 | 8.46 | 52% | 100% |
| Commodity (WTI oil, $ per barrel) | gpt-oss-120b | seen | 25.72 | 19.98 | -29% | 67% |
| Commodity (WTI oil, $ per barrel) | gpt-oss-120b | unseen | 13.88 | 11.89 | -17% | 67% |

## Scenario 1. Impact of economic policy on the stock market

| Cutoff | Window | Actual 6-month change % | gpt-oss-20b forecast | gpt-oss-120b forecast |
| --- | --- | --- | --- | --- |
| 2021-12 | seen | -20.58 | -5.20 (range -8.00 to -2.40, error 15.38) | 5.20 (range 2.00 to 9.00, error 25.78) |
| 2022-06 | seen | 1.43 | -1.50 (range -3.00 to -0.50, error 2.93) | -7.20 (range -12.00 to -3.50, error 8.63) |
| 2022-12 | seen | 15.91 | -5.20 (range -8.50 to -2.00, error 21.11) | -6.20 (range -12.50 to -1.00, error 22.11) |
| 2024-12 | unseen | 5.50 | 3.00 (range 1.00 to 5.00, error 2.50) | 5.20 (range 3.80 to 6.60, error 0.30) |
| 2025-06 | unseen | 10.32 | 6.30 (range 4.00 to 8.00, error 4.02) | 4.80 (range 3.50 to 6.20, error 5.52) |
| 2025-12 | unseen | 9.55 | 1.80 (range 0.50 to 3.20, error 7.75) | 3.20 (range 2.50 to 4.00, error 6.35) |

### Example reasoning

- **gpt-oss-20b, 2021-12** (confidence 70): Recent yield rise and slight fed‑funds increase suggest a modest sell‑off in equity valuations, leading to a small downtrend in the S&P 500 over the next six months. Drivers: higher 10‑year yield, moderate fed‑funds tightening.
- **gpt-oss-20b, 2025-12** (confidence 78): Continued easing of rates and modest inflation support equity demand, likely driving a modest rise in the S&P 500 over the next six months. Drivers: Lower long-term yields, Stable inflation.
- **gpt-oss-120b, 2021-12** (confidence 70): With the Fed keeping rates low and the 10‑year yield still modestly higher, equity valuations remain attractive, though high inflation may temper enthusiasm, leading to modest upside over the next six months. Drivers: moderate monetary easing, persistent inflation pressures.
- **gpt-oss-120b, 2025-12** (confidence 78): The Fed has lowered rates to 3.72% and Treasury yields have slipped modestly, supporting equity valuations, while inflation remains near target, suggesting a bullish bias for the S&P 500 over the next six months. Drivers: continued easing of fed funds rate, moderate inflation keeping real yields attractive.

## Scenario 2. Commodity price trends (WTI oil)

| Cutoff | Window | Last value before forecast | Actual (final period) | gpt-oss-20b forecast | gpt-oss-120b forecast |
| --- | --- | --- | --- | --- | --- |
| 2021-12 | seen | 71.71 | 114.84 | 60.00 (range 55.00 to 65.00, error 37.84) | 84.20 (range 80.00 to 86.00, error 22.89) |
| 2022-06 | seen | 114.84 | 76.44 | 137.40 (range 125.00 to 145.00, error 40.01) | 141.00 (range 120.00 to 140.00, error 41.93) |
| 2022-12 | seen | 76.44 | 70.25 | 71.00 (range 70.00 to 73.00, error 1.67) | 55.70 (range 50.00 to 60.00, error 12.35) |
| 2024-12 | unseen | 70.12 | 68.17 | 77.50 (range 76.00 to 78.00, error 9.77) | 68.70 (range 66.00 to 70.00, error 3.70) |
| 2025-06 | unseen | 68.17 | 57.97 | 60.00 (range 58.00 to 62.00, error 2.31) | 57.00 (range 55.00 to 60.00, error 1.52) |
| 2025-12 | unseen | 57.97 | 84.81 | 55.00 (range 54.50 to 55.50, error 27.61) | 39.70 (range 38.00 to 42.00, error 36.41) |

### Example reasoning

- **gpt-oss-20b, 2021-12** (confidence 70): Recent 2021 prices show a clear decline from a peak in October; a modest downward trend is expected to continue into early 2022 with volatility narrowing around the low‑60s.
- **gpt-oss-20b, 2025-12** (confidence 70): Recent data show a steady decline and a linear trend predicts prices to continue falling modestly over the next six months.
- **gpt-oss-120b, 2021-12** (confidence 70): After a strong rebound in 2021 ending around $71.7 per barrel, the trend suggests continued moderate growth into early 2022, tempered by typical seasonal volatility.
- **gpt-oss-120b, 2025-12** (confidence 65): The series shows a clear downward trajectory in 2025, with prices falling from $75.74 to $57.97, suggesting continued decline into early 2026.
