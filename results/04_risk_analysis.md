# Requirement 3: Risk identification and mitigation

Levels are shown as market volatility / credit / liquidity. The reference levels come from simple rules (VIX under 20 Low, 20 to 30 Medium, over 30 High; Baa spread under 2.5 Low, 2.5 to 3.5 Medium, over 3.5 High; NFCI under -0.3 Low, -0.3 to 0 Medium, over 0 High).

| Month | VIX | Credit spread | NFCI | Rule reference | gpt-oss-20b | gpt-oss-120b |
| --- | --- | --- | --- | --- | --- | --- |
| 2008-10 | 61.2 | 5.06 | 2.51 | High / High / High | None / None / None (0/3) | High / High / Medium (2/3) |
| 2017-06 | 10.5 | 2.18 | -0.56 | Low / Low / Low | Low / Low / Medium (2/3) | Low / Low / Low (3/3) |
| 2020-03 | 57.7 | 3.42 | 0.09 | High / Medium / High | High / Medium / Low (2/3) | High / High / Medium (1/3) |
| 2022-09 | 27.3 | 2.17 | -0.14 | Medium / Low / Medium | High / Medium / Low (0/3) | High / Low / Medium (2/3) |
| 2023-03 | 21.6 | 2.05 | -0.18 | Medium / Low / Medium | Medium / Medium / Medium (2/3) | Medium / Low / Medium (3/3) |
| 2025-04 | 32.0 | 1.90 | -0.39 | High / Low / Low | High / Low / Medium (2/3) | High / Low / Medium (2/3) |

## Agreement with the rule reference

| Model | Levels matching |
| --- | --- |
| gpt-oss-20b | 8/18 (44%) |
| gpt-oss-120b | 13/18 (72%) |

## gpt-oss-20b, 2008-10

- **Market Volatility: None.** None Mitigation: 

- **Credit: None.** None Mitigation: 

- **Liquidity: None.** None Mitigation: 

## gpt-oss-20b, 2017-06

- **Market Volatility: Low.** The VIX average of 10.5 is well below its long‑run average of 19.5 and the highest daily level only reached 11.5, indicating subdued volatility. Mitigation: Use options or VIX‑linked ETFs to hedge against sudden spikes Maintain a diversified asset mix with low‑correlation assets

- **Credit: Low.** The Baa spread of 2.18pp is slightly below the long‑run average of 2.35pp, and the 10‑yr/2‑yr spread of 0.84pp remains within typical ranges, suggesting stable credit conditions. Mitigation: Implement dynamic credit limits and monitor Baa spreads regularly Use credit default swaps to transfer downside exposure

- **Liquidity: Medium.** The Chicago Fed National Financial Conditions Index at -0.56 (negative indicates slightly looser conditions) combined with a modest 3‑month S&P gain and low unemployment implies liquidity is adequate but could tighten if conditions shift. Mitigation: Maintain higher cash reserves and short‑term liquid assets Enter into central bank liquidity lines or repo agreements for contingency

## gpt-oss-20b, 2020-03

- **Market Volatility: High.** VIX average 57.7 far above long‑run 19.3, peak 82.7, and S&P 500 fell 20% in 3 months Mitigation: Implement dynamic VaR limits and stress testing; use hedging instruments such as VIX futures or equity options Maintain diversified asset allocation to reduce concentration risk

- **Credit: Medium.** Baa spread 3.42pp above long‑run 2.33pp, but Treasury spread 0.42pp indicates modest yield curve steepening Mitigation: Use credit default swaps or collateralized debt obligations to transfer credit exposure; conduct regular covenant monitoring of Baa issuers Diversify across sectors and geographies to spread credit risk

- **Liquidity: Low.** Chicago Fed NFCI at 0.09 (close to average 0) and Fed funds rate 0.65% suggest normal liquidity conditions Mitigation: Maintain higher cash reserves and liquid securities to meet short‑term obligations; establish a liquidity contingency plan Engage in liquidity coverage ratio (LCR) compliance and regular stress‑test scenarios

## gpt-oss-20b, 2022-09

- **Market Volatility: High.** VIX monthly average 27.3 is above the long‑run average of 19.6, and the S&P 500 fell 5.3% over the last three months, indicating heightened market uncertainty. Mitigation: Use dynamic asset‑allocation strategies to adjust equity‑to‑fixed income weighting during volatile periods Implement volatility‑based hedging (e.g., VIX futures or options) to protect downside exposure

- **Credit: Medium.** The Baa spread over the 10‑year Treasury is 2.17 ppt, slightly below the long‑run average of 2.32 ppt, and the 10‑year minus 2‑year Treasury spread is negative, signalling a flattening curve and moderate credit‑risk concerns. Mitigation: Maintain diversified credit exposure across sectors and ratings to reduce concentration risk Regularly monitor and update credit risk limits using forward‑looking macro‑economic indicators

- **Liquidity: Low.** The Chicago Fed National Financial Conditions Index is near zero at –0.14, unemployment is low at 3.5 %, and no significant stress indicators are present, suggesting generally normal liquidity conditions. Mitigation: Hold a sufficient pool of high‑quality liquid assets (e.g., Treasury bills) to meet short‑term obligations Implement robust liquidity monitoring tools and stress‑testing scenarios to ensure adequate cash buffers

## gpt-oss-20b, 2023-03

- **Market Volatility: Medium.** VIX average at 21.6 is above its long‑run average of 19.7 and the VIX spike to 26.5 indicates heightened market uncertainty. Mitigation: Implement dynamic hedging of equity and volatility exposure using VIX futures or options Maintain diversified asset allocation to reduce concentration in high‑volatility sectors

- **Credit: Medium.** Baa spread narrowed to 2.05 from a long‑run average of 2.32, suggesting easing credit conditions but still above the risk‑free Treasury. Mitigation: Enhance credit risk monitoring with tighter covenant oversight and stress testing Diversify funding sources to mitigate reliance on single high‑risk issuers

- **Liquidity: Medium.** The 10‑year minus 2‑year Treasury spread is negative (-0.64), indicating a steepening yield curve and potential liquidity constraints in short‑term funding. Mitigation: Build higher liquidity reserves and maintain a diversified mix of funding maturities Engage in contingency funding plans and establish credit lines with banks

## gpt-oss-20b, 2025-04

- **Market Volatility: High.** The VIX monthly average of 32.0 and a peak of 52.3 far exceed the long‑run average of 19.5, indicating sharp market volatility. Mitigation: Use volatility hedging strategies such as VIX futures or options to protect equity exposure. Implement dynamic asset‑allocation shifts to reduce concentration in highly volatile sectors.

- **Credit: Low.** Baa corporate bond spread of 1.90% is below the long‑run average of 2.29%, and the 10‑year minus 2‑year Treasury spread of 0.50% suggests limited credit tightening. Mitigation: Maintain higher quality credit buffers by holding a larger proportion of investment‑grade bonds. Diversify loan portfolios across sectors and geographies to mitigate concentration risk.

- **Liquidity: Medium.** The Chicago Fed National Financial Conditions Index of -0.39 signals slightly tighter conditions, and a -7.8% decline in the S&P 500 over three months indicates moderate stress on liquidity. Mitigation: Increase cash reserves and maintain strong liquidity coverage ratios to absorb market shocks. Establish counterparty credit limits and regularly stress test liquidity under adverse market scenarios.

## gpt-oss-120b, 2008-10

- **Market Volatility: High.** The VIX averaged 61.2 in October 2008, far above its long‑run average of 19.4, indicating extreme market turbulence. Mitigation: Implement dynamic hedging programs (e.g., VIX futures, options, or delta‑neutral equity strategies) to offset sudden price swings. Adopt stricter position limits and stop‑loss controls to cap exposure during periods of heightened volatility.

- **Credit: High.** The Baa corporate bond spread was 5.06 pp, more than double its historical average of 2.11 pp, signaling stressed credit conditions. Mitigation: Increase credit quality filters and reduce exposure to lower‑rated issuers; shift portfolio weight toward investment‑grade and government securities. Utilize credit default swaps or other credit‑derivative protection to hedge against default risk on high‑spread corporate exposures.

- **Liquidity: Medium.** The Chicago Fed NFCC index of 2.51 shows tighter‑than‑average financial conditions, while the policy rate is near zero, suggesting moderate but not catastrophic liquidity strain. Mitigation: Maintain higher cash and high‑quality liquid asset buffers (e.g., Treasury bills) to meet short‑term funding needs. Establish diversified funding sources, including committed lines of credit and repo arrangements, to reduce reliance on volatile market funding.

## gpt-oss-120b, 2017-06

- **Market Volatility: Low.** VIX monthly average 10.5 and peak 11.5 are well below the long‑run average of 19.5, indicating subdued market turbulence. Mitigation: Maintain a diversified portfolio of assets with low‑correlation to equities to dampen any unexpected spikes in volatility. Use options or variance swaps to hedge against sudden VIX spikes, even though current risk is low.

- **Credit: Low.** Baa corporate bond spread is 2.18 pp, tighter than the long‑run average of 2.35 pp, suggesting relatively low credit stress. Mitigation: Implement a dynamic credit scoring model that continuously monitors spread movements and counterparty ratings. Set exposure limits for Baa‑rated issuers and increase reliance on higher‑quality (Aa/AAA) securities as a precaution.

- **Liquidity: Low.** Fed funds rate at 1.04% with a negative Chicago Fed Financial Conditions Index (-0.56) and a narrow 10y‑2y Treasury spread (0.84 pp) point to ample liquidity and easy financing conditions. Mitigation: Keep a buffer of high‑quality liquid assets (e.g., Treasury bills) equal to at least 15‑20% of short‑term liabilities. Establish committed credit lines with multiple banks to ensure funding access if market conditions tighten suddenly.

## gpt-oss-120b, 2020-03

- **Market Volatility: High.** The VIX monthly average of 57.7 and a peak of 82.7 are far above the long‑run average of 19.3, indicating extreme market turbulence. Mitigation: Increase use of option overlays (e.g., protective puts or collars) to hedge equity exposure during periods of elevated VIX. Diversify into low‑beta or non‑correlated asset classes such as short‑duration government bonds or commodities to reduce portfolio sensitivity to market swings.

- **Credit: High.** The Baa corporate bond spread is 3.42 ppt, notably above its long‑run average of 2.33 ppt, signaling heightened credit risk in the corporate sector. Mitigation: Tighten credit underwriting standards and raise minimum credit quality thresholds for new loan commitments. Shift portfolio weight toward higher‑rated securities and increase holdings of investment‑grade corporate bonds or loan participation with strong covenants.

- **Liquidity: Medium.** The Chicago Fed Financial Conditions Index is slightly positive (0.09) and the 10‑year/2‑year spread is compressed to 0.42 ppt, suggesting tighter financing conditions but not a full liquidity crunch. Mitigation: Maintain higher cash and high‑quality liquid asset buffers (e.g., Treasury bills) to meet short‑term funding needs. Secure committed lines of credit and diversify funding sources across repos, commercial paper, and unsecured borrowing to reduce reliance on any single market segment.

## gpt-oss-120b, 2022-09

- **Market Volatility: High.** The VIX monthly average of 27.3 and a peak of 32.6 are far above its long‑run average of 19.6, indicating elevated market turbulence. Mitigation: Increase the use of option overlays and dynamic hedges (e.g., VIX futures, variance swaps) to protect portfolio value during spikes in volatility. Implement stricter position‑size limits and real‑time VaR monitoring to curb exposure when volatility metrics breach predefined thresholds.

- **Credit: Low.** The Baa corporate bond spread is 2.17 pp, tighter than its long‑run average of 2.32 pp, suggesting relatively modest credit stress. Mitigation: Maintain a diversified credit portfolio with a focus on higher‑quality (AAA/AA) issuers and continuously monitor Baa spread trends for early signs of deterioration. Use credit default swaps (CDS) or total return swaps to hedge exposure to specific corporate bond positions that show widening spreads.

- **Liquidity: Medium.** An inverted 10‑yr/2‑yr spread of –0.34 pp, a modestly positive Fed Funds rate (2.56 %) and a slightly below‑average financial conditions index (‑0.14) point to emerging liquidity pressures despite generally normal conditions. Mitigation: Hold a higher proportion of high‑quality liquid assets (e.g., Treasury bills, overnight repos) to meet sudden funding demands. Establish committed credit lines and staggered funding maturities to reduce reliance on short‑term wholesale funding that could dry up in a tightening market.

## gpt-oss-120b, 2023-03

- **Market Volatility: Medium.** The VIX average of 21.6 is above its long‑run average of 19.7, indicating elevated but not extreme market turbulence. Mitigation: Increase use of option overlays and volatility swaps to hedge portfolio exposure to sudden spikes in the VIX. Diversify across asset classes and geographies to reduce concentration risk from U.S. equity market swings.

- **Credit: Low.** The Baa spread of 2.05 ppt is tighter than the long‑run average of 2.32 ppt, suggesting improving credit conditions. Mitigation: Maintain stricter underwriting standards and higher minimum credit quality thresholds for new loan originations. Allocate a larger portion of the investment portfolio to high‑quality sovereign and investment‑grade corporate bonds to cushion any potential credit deterioration.

- **Liquidity: Medium.** The Chicago Fed NFCCI at –0.18 (near neutral) combined with an inverted 10‑yr/2‑yr spread of –0.64 ppt points to modest funding strain without a full liquidity crunch. Mitigation: Hold a higher proportion of high‑quality liquid assets (e.g., Treasury bills, agency securities) to meet short‑term cash needs under tightening conditions. Establish committed credit lines and liquidity facilities with multiple counterparties to ensure access to funding if market stress intensifies.

## gpt-oss-120b, 2025-04

- **Market Volatility: High.** The VIX monthly average of 32.0 is well above its long‑run average of 19.5, and the peak of 52.3 signals extreme market turbulence. Mitigation: Increase use of options and variance swaps to hedge portfolio exposure to large price swings. Diversify assets across low‑beta sectors and non‑correlated alternative investments to reduce overall volatility sensitivity.

- **Credit: Low.** The Baa corporate bond spread is 1.90 ppt, tighter than the long‑run average of 2.29 ppt, indicating reduced default risk perception. Mitigation: Maintain a conservative credit quality mix, emphasizing investment‑grade issuers and reducing exposure to high‑yield names. Implement dynamic credit monitoring with forward‑looking metrics (e.g., CDS spreads, earnings trends) to adjust limits proactively.

- **Liquidity: Medium.** The Chicago Fed National Financial Conditions Index at –0.39 and a flattened 10‑year/2‑year Treasury spread of 0.50 ppt point to modestly tighter funding conditions. Mitigation: Hold a higher proportion of high‑quality liquid assets (e.g., Treasury bills, overnight repos) to meet short‑term cash needs. Establish committed credit lines and staggered funding maturities to smooth out potential roll‑over pressures.
