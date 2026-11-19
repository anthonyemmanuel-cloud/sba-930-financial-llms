"""All the prompts sent to the LLMs. Baseline prompts are simple, optimized prompts add the methods from Requirement 4."""

import math

ANALYST_SYSTEM = (
    "You are a careful quantitative financial analyst. Use only the data you are given. "
    "Do not invent news, events or numbers. When the data does not support a strong view, "
    "stay close to the most recent value and say so in your reasoning.")

PATH_FORMAT = ('{{"forecast": [one number per {unit}, {horizon} numbers], "low": number, "high": number, '
               '"direction": "up" or "down" or "flat", "confidence": number from 0 to 100, '
               '"reasoning": "one or two sentences"}}')

STOCK_FORMAT = ('{"change_pct": number, "low": number, "high": number, "direction": "up" or "down" or "flat", '
                '"confidence": number from 0 to 100, "drivers": ["short phrase", "short phrase"], '
                '"reasoning": "one or two sentences"}')


def number(value, decimals=2):
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "not published"
    return f"{value:,.{decimals}f}"


def masked_labels(count, future=False):
    """t-35 ... t0 for the past and t+1 ... for the future. Hides the real dates from the model."""
    if future:
        return [f"t+{i}" for i in range(1, count + 1)]
    return [f"t-{count - 1 - i}" for i in range(count - 1)] + ["t0"]


def data_rows(values, labels, decimals):
    return "\n".join(f"{label}: {number(v, decimals)}" for label, v in zip(labels, values))


def path_stats(values, step_names, decimals):
    """Simple numbers an analyst would calculate before forecasting (used by the optimized prompt)."""
    clean = [v for v in values if not math.isnan(v)]
    latest = clean[-1]
    lines = [f"- Latest value: {number(latest, decimals)}"]
    for steps, name in step_names:
        if len(clean) > steps:
            lines.append(f"- Change over the last {name}: {clean[-1] - clean[-1 - steps]:+.{decimals}f}")
    changes = [b - a for a, b in zip(clean, clean[1:])]
    mean = sum(clean) / len(clean)
    spread = (sum((c - sum(changes) / len(changes)) ** 2 for c in changes) / len(changes)) ** 0.5
    lines.append(f"- Average over the whole period shown: {number(mean, decimals)}")
    lines.append(f"- Typical size of one period's change (standard deviation): {spread:.{decimals}f}")
    lines.append(f"- Naive forecast (repeat the latest value every period): {number(latest, decimals)}")
    return "\n".join(lines)


def path_prompt(spec, values, past_labels, future_labels, variant):
    """Return (system message, user message) for a time series forecast."""
    horizon = len(future_labels)
    fmt = PATH_FORMAT.format(unit=spec["unit"], horizon=horizon)
    rows = data_rows(values, past_labels, spec["decimals"])
    ask = (f"Forecast the next {horizon} {spec['unit']}s ({future_labels[0]} to {future_labels[-1]}).")
    if variant != "optimized":
        user = (f"{spec['task']}\n\n{spec['description']}:\n{rows}\n\n{ask}\n"
                f"Reply with JSON only, in this format:\n{fmt}\n"
                f'"low" and "high" are the range you expect the value for {future_labels[-1]} to fall in.')
        return "", user
    stats = path_stats(values, spec["stat_steps"], spec["decimals"])
    user = (f"{spec['task']}\n\n{spec['description']}:\n{rows}\n\n"
            f"Statistics calculated from the data above:\n{stats}\n\n{ask}\n"
            "Work in three steps. 1) Start from the naive forecast. 2) Move away from it only when the trend, "
            "mean reversion or interest rate data gives a clear reason. 3) Set low and high so the actual "
            f"value for {future_labels[-1]} falls inside them about 8 times out of 10.\n"
            f"Reply with JSON only, in this format:\n{fmt}")
    return ANALYST_SYSTEM, user


def stock_prompt(table, labels, end_label, variant):
    """Scenario 1. table has columns fed_funds, treasury_10y, inflation, sp500 for the last 24 months."""
    rows = "\n".join(
        f"{label}: fed funds {number(r.fed_funds)}%, 10-year yield {number(r.treasury_10y)}%, "
        f"inflation {number(r.inflation, 1)}%, S&P 500 {number(r.sp500, 0)}"
        for label, r in zip(labels, table.itertuples()))
    first, last = table.iloc[-13], table.iloc[-1]
    policy = (f"Over the last 12 months the federal funds rate moved from {number(first.fed_funds)}% to "
              f"{number(last.fed_funds)}%, and the 10-year Treasury yield moved from "
              f"{number(first.treasury_10y)}% to {number(last.treasury_10y)}%.")
    ask = f"Forecast the percent change of the S&P 500 over the next 6 months (from {labels[-1]} to {end_label})."
    head = ("Forecast the potential impact of recent economic policies on the stock market.\n\n"
            f"Monthly US data:\n{rows}\n\nPolicy summary: {policy}\n\n{ask}\n")
    if variant != "optimized":
        return "", head + f"Reply with JSON only, in this format:\n{STOCK_FORMAT}"
    sp = table["sp500"].tolist()
    six_month = [(b / a - 1) * 100 for a, b in zip(sp, sp[6:])]
    stats = (f"- S&P 500 change over the last 3 months: {(sp[-1] / sp[-4] - 1) * 100:+.1f}%\n"
             f"- S&P 500 change over the last 12 months: {(sp[-1] / sp[-13] - 1) * 100:+.1f}%\n"
             f"- Average 6-month change in the period shown: {sum(six_month) / len(six_month):+.1f}%\n"
             f"- Smallest and largest 6-month change in the period shown: {min(six_month):+.1f}% and "
             f"{max(six_month):+.1f}%\n"
             "- Naive forecasts: 0% (no change), or about +4% (the long-run average 6-month gain for US stocks)")
    return ANALYST_SYSTEM, (
        head + f"\nStatistics calculated from the data above:\n{stats}\n\n"
        "Work in three steps. 1) Start from the naive forecasts. 2) Explain how the interest rate and inflation "
        "trend should move you away from them. 3) Set low and high so the actual change falls inside about "
        f"8 times out of 10.\nReply with JSON only, in this format:\n{STOCK_FORMAT}")


RISK_FORMAT = ('{"market_volatility": {"level": "Low" or "Medium" or "High", "evidence": "one sentence"}, '
               '"credit": {"level": ..., "evidence": ...}, "liquidity": {"level": ..., "evidence": ...}, '
               '"mitigation": {"market_volatility": ["strategy", "strategy"], "credit": ["strategy", "strategy"], '
               '"liquidity": ["strategy", "strategy"]}}')


def risk_prompt(month_label, snapshot, averages):
    lines = [
        f"- VIX volatility index: monthly average {number(snapshot['vix'], 1)}, highest day "
        f"{number(snapshot['vix_max'], 1)} (long-run average {averages['vix']:.1f})",
        f"- Baa corporate bond spread over the 10-year Treasury: {number(snapshot['credit_spread'])} "
        f"percentage points (long-run average {averages['credit_spread']:.2f})",
        f"- Chicago Fed National Financial Conditions Index: {number(snapshot['nfci'])} "
        "(0 is average, above 0 means tighter than average conditions)",
        f"- 10-year minus 2-year Treasury spread: {number(snapshot['yield_curve'])} percentage points",
        f"- Federal funds rate: {number(snapshot['fed_funds'])}%",
        f"- Unemployment rate: {number(snapshot['unemployment'], 1)}%",
        f"- S&P 500 change over the last 3 months: "
        + ("not available" if snapshot["sp500_3m"] is None else f"{snapshot['sp500_3m']:+.1f}%"),
    ]
    user = (f"You are a financial risk analyst. Using only the US market data below for {month_label}, "
            "identify the main financial risks.\n\n" + "\n".join(lines) + "\n\n"
            "Rate market volatility risk, credit risk and liquidity risk as Low, Medium or High, give the evidence "
            "from the data, and suggest two mitigation strategies for each risk that a financial services firm "
            f"could use.\nReply with JSON only, in this format:\n{RISK_FORMAT}")
    return "", user