"""Run the forecasts and risk checks, then score them against what really happened."""

import math
import statistics

import pandas as pd

from . import data, llm, prompts

MONTH_STEPS = [(3, "3 months"), (6, "6 months"), (12, "12 months")]
PATH_TASKS = {
    "oil": {"column": "oil", "freq": "M", "history": 36, "horizon": 6, "unit": "month", "decimals": 2,
            "stat_steps": MONTH_STEPS,
            "task": "Analyze historical financial data to predict future trends in commodity prices.",
            "description": "Monthly average price of WTI crude oil, US dollars per barrel"},
    "inflation": {"column": "inflation", "freq": "M", "history": 36, "horizon": 6, "unit": "month",
                  "decimals": 1, "stat_steps": MONTH_STEPS,
                  "task": "Forecast US consumer price inflation for the next 6 months.",
                  "description": "US CPI inflation, percent change from the same month a year earlier"},
    "gdp": {"column": "gdp", "freq": "Q", "history": 12, "horizon": 4, "unit": "quarter", "decimals": 1,
            "stat_steps": [(1, "quarter"), (2, "2 quarters"), (4, "4 quarters")],
            "task": "Forecast US real GDP growth for the next 4 quarters.",
            "description": "US real GDP growth by quarter, annualized percent change from the previous quarter"},
}

# variant: (prompt style, temperature, JSON mode, number of samples)
VARIANTS = {
    "baseline": ("baseline", 1.0, False, 1),
    "masked": ("baseline", 1.0, False, 1),
    "optimized": ("optimized", 0.0, True, 1),
    "self_consistency": ("optimized", 0.7, True, 3),
}


def clean(value):
    return None if value is None or (isinstance(value, float) and math.isnan(value)) else value


def to_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def cutoffs_for(freq, variant):
    seen = data.SEEN_MONTHS if freq == "M" else data.SEEN_QUARTERS
    unseen = data.UNSEEN_MONTHS if freq == "M" else data.UNSEEN_QUARTERS
    windows = [(c, "seen") for c in seen]
    return windows if variant == "masked" else windows + [(c, "unseen") for c in unseen]


def ask_all(model, variant, system, user, meta):
    """Ask once, or several times for self-consistency, and return the parsed answers."""
    _, temperature, json_mode, samples = VARIANTS[variant]
    answers = [llm.parse_json(llm.ask(model, system, user, temperature, json_mode, s, meta)) for s in range(samples)]
    return [a for a in answers if a]


def score_path(forecast, actual, last, low, high):
    """Mean absolute error against reality, against a naive 'no change' forecast, plus direction and range checks."""
    pairs = [(f, a) for f, a in zip(forecast, actual) if a is not None]
    if not pairs:
        return {}
    end_f, end_a = pairs[-1]
    covered = None if low is None or high is None else min(low, high) <= end_a <= max(low, high)
    return {"mae": sum(abs(f - a) for f, a in pairs) / len(pairs),
            "naive_mae": sum(abs(last - a) for _, a in pairs) / len(pairs),
            "dir_hit": (end_f - last > 0) == (end_a - last > 0), "covered": covered}


def combine(answers, horizon):
    """Turn one or more JSON answers into one forecast. Several samples are combined with the median."""
    paths = []
    for a in answers:
        values = [to_float(v) for v in (a.get("forecast") or [])][:horizon]
        if len(values) == horizon and None not in values:
            paths.append((values, to_float(a.get("low")), to_float(a.get("high")), a))
    if not paths:
        return None
    forecast = [statistics.median(p[0][i] for p in paths) for i in range(horizon)]
    lows = [p[1] for p in paths if p[1] is not None]
    highs = [p[2] for p in paths if p[2] is not None]
    ends = [p[0][-1] for p in paths]
    first = paths[0][3]
    return {"forecast": forecast, "low": statistics.median(lows) if lows else None,
            "high": statistics.median(highs) if highs else None,
            "direction": first.get("direction"), "confidence": to_float(first.get("confidence")),
            "reasoning": str(first.get("reasoning", ""))[:400],
            "spread": statistics.pstdev(ends) if len(ends) > 1 else None, "samples": len(paths)}


def run_path(task, model, variant, monthly, gdp):
    spec = PATH_TASKS[task]
    series = gdp if spec["freq"] == "Q" else monthly[spec["column"]]
    window = data.quarter_window if spec["freq"] == "Q" else data.month_window
    label = data.quarter_label if spec["freq"] == "Q" else data.month_label
    rows = []
    for cutoff, period in cutoffs_for(spec["freq"], variant):
        past, actual = window(series, cutoff, spec["history"], spec["horizon"])
        if len(past) < spec["history"] or label(past.index[-1]) != cutoff or actual.isna().all():
            print(f"   Skipping {task} {cutoff}: the data for this window is not available.")
            continue
        if variant == "masked":
            past_labels = prompts.masked_labels(len(past))
            future_labels = prompts.masked_labels(spec["horizon"], future=True)
        else:
            past_labels, future_labels = [label(d) for d in past.index], [label(d) for d in actual.index]
        style = VARIANTS[variant][0]
        system, user = prompts.path_prompt(spec, past.tolist(), past_labels, future_labels, style)
        last = float(past.dropna().iloc[-1])
        answer = combine(ask_all(model, variant, system, user,
                                 {"kind": "path", "last": last, "horizon": spec["horizon"]}), spec["horizon"])
        row = {"task": task, "model": model, "variant": variant, "cutoff": cutoff, "period": period,
               "last": last, "actual": [clean(v) for v in actual.tolist()], "valid": answer is not None}
        if answer:
            row.update(answer)
            row.update(score_path(answer["forecast"], row["actual"], last, answer["low"], answer["high"]))
        rows.append(row)
        print(f"   {model:14} {task:9} {variant:16} {cutoff}  {'ok' if answer else 'could not read answer'}")
    return rows


def run_stock(model, variant, monthly):
    columns = ["fed_funds", "treasury_10y", "inflation", "sp500"]
    rows = []
    for cutoff, period in cutoffs_for("M", variant):
        end = pd.Period(cutoff, "M").to_timestamp()
        table = monthly[columns].loc[:end].iloc[-24:]
        target = end + pd.DateOffset(months=6)
        if len(table) < 24 or pd.isna(table["sp500"]).any() or pd.isna(monthly["sp500"].get(target)):
            print(f"   Skipping stock {cutoff}: the data for this window is not available.")
            continue
        if variant == "masked":
            labels, end_label = prompts.masked_labels(24), "t+6"
        else:
            labels, end_label = [data.month_label(d) for d in table.index], data.month_label(target)
        system, user = prompts.stock_prompt(table, labels, end_label, VARIANTS[variant][0])
        answers = ask_all(model, variant, system, user, {"kind": "stock"})
        changes = [to_float(a.get("change_pct")) for a in answers]
        valid = [(c, a) for c, a in zip(changes, answers) if c is not None]
        actual = (monthly["sp500"][target] / table["sp500"].iloc[-1] - 1) * 100
        row = {"task": "stock", "model": model, "variant": variant, "cutoff": cutoff, "period": period,
               "last": 0.0, "actual": [round(actual, 2)], "valid": bool(valid)}
        if valid:
            first = valid[0][1]
            change = statistics.median(c for c, _ in valid)
            low, high = to_float(first.get("low")), to_float(first.get("high"))
            row.update({"forecast": [change], "low": low, "high": high, "direction": first.get("direction"),
                        "confidence": to_float(first.get("confidence")), "drivers": first.get("drivers"),
                        "reasoning": str(first.get("reasoning", ""))[:400],
                        "spread": statistics.pstdev([c for c, _ in valid]) if len(valid) > 1 else None})
            row.update(score_path([change], [actual], 0.0, low, high))
        rows.append(row)
        print(f"   {model:14} {'stock':9} {variant:16} {cutoff}  {'ok' if valid else 'could not read answer'}")
    return rows


def ensemble(rows):
    """Average the two models' optimized forecasts for the same window. No extra API calls."""
    out = []
    frame = [r for r in rows if r["variant"] == "optimized" and r["valid"]]
    for (task, cutoff) in sorted({(r["task"], r["cutoff"]) for r in frame}):
        pair = [r for r in frame if r["task"] == task and r["cutoff"] == cutoff]
        if len(pair) != len(llm.MODELS):
            continue
        forecast = [sum(vals) / len(vals) for vals in zip(*(r["forecast"] for r in pair))]
        lows = [r["low"] for r in pair if r["low"] is not None]
        highs = [r["high"] for r in pair if r["high"] is not None]
        low, high = (min(lows), max(highs)) if lows and highs else (None, None)
        row = {"task": task, "model": "ensemble", "variant": "ensemble", "cutoff": cutoff,
               "period": pair[0]["period"], "last": pair[0]["last"], "actual": pair[0]["actual"],
               "valid": True, "forecast": forecast, "low": low, "high": high}
        row.update(score_path(forecast, row["actual"], row["last"], low, high))
        out.append(row)
    return out


def summarize(rows):
    """One line per task, model, variant and period with the main accuracy numbers."""
    groups = {}
    for r in rows:
        groups.setdefault((r["task"], r["model"], r["variant"], r["period"]), []).append(r)
    lines = []
    for (task, model, variant, period), group in groups.items():
        scored = [r for r in group if r.get("mae") is not None]
        covered = [r["covered"] for r in scored if r.get("covered") is not None]
        mae = sum(r["mae"] for r in scored) / len(scored) if scored else None
        naive = sum(r["naive_mae"] for r in scored) / len(scored) if scored else None
        lines.append({"task": task, "model": model, "variant": variant, "period": period,
                      "windows": len(group), "readable": sum(r["valid"] for r in group),
                      "mae": mae, "naive_mae": naive,
                      "skill": (1 - mae / naive) if scored and naive else None,
                      "direction": sum(r["dir_hit"] for r in scored) / len(scored) if scored else None,
                      "coverage": sum(covered) / len(covered) if covered else None})
    return pd.DataFrame(lines)


def overall(summary, task, model, variant):
    """Combine seen and unseen windows into one line."""
    part = summary[(summary.task == task) & (summary.model == model) & (summary.variant == variant)]
    if part.empty or part["mae"].isna().all():
        return None
    w = part["readable"]
    mae = (part["mae"] * w).sum() / w.sum()
    naive = (part["naive_mae"] * w).sum() / w.sum()
    cov = part.dropna(subset=["coverage"])
    return {"mae": mae, "naive_mae": naive, "skill": 1 - mae / naive if naive else None,
            "direction": (part["direction"] * w).sum() / w.sum(),
            "coverage": (cov["coverage"] * cov["readable"]).sum() / cov["readable"].sum() if not cov.empty else None,
            "readable": int(w.sum()), "windows": int(part["windows"].sum())}


# ---------------------------------------------------------------- risk analysis

RISK_NAMES = ["market_volatility", "credit", "liquidity"]


def reference_levels(snapshot):
    """Simple rule-based levels used as a yardstick for the LLMs' answers."""
    def level(value, low, high):
        return "Low" if value < low else "Medium" if value < high else "High"
    return {"market_volatility": level(snapshot["vix"], 20, 30),
            "credit": level(snapshot["credit_spread"], 2.5, 3.5),
            "liquidity": level(snapshot["nfci"], -0.3, 0.0)}


def risk_snapshot(monthly, month):
    date = pd.Period(month, "M").to_timestamp()
    row = monthly.loc[date].to_dict()
    sp_now, sp_before = monthly["sp500"].get(date), monthly["sp500"].get(date - pd.DateOffset(months=3))
    row["sp500_3m"] = None if pd.isna(sp_now) or pd.isna(sp_before) else (sp_now / sp_before - 1) * 100
    history = monthly.loc[:date]
    averages = {"vix": history["vix"].mean(), "credit_spread": history["credit_spread"].mean()}
    return row, averages


def run_risk(model, monthly):
    rows = []
    for month in data.RISK_DATES:
        snapshot, averages = risk_snapshot(monthly, month)
        system, user = prompts.risk_prompt(month, snapshot, averages)
        answer = llm.parse_json(llm.ask(model, system, user, 1.0, False, 0, {"kind": "risk"})) or {}
        reference = reference_levels(snapshot)
        levels, evidence = {}, {}
        for name in RISK_NAMES:
            part = answer.get(name) if isinstance(answer.get(name), dict) else {}
            levels[name] = str(part.get("level", "")).strip().title() or None
            evidence[name] = part.get("evidence")
        rows.append({"model": model, "month": month, "levels": levels, "reference": reference,
                     "evidence": evidence, "mitigation": answer.get("mitigation") or {},
                     "matches": sum(levels[n] == reference[n] for n in RISK_NAMES),
                     "snapshot": {k: clean(v) if isinstance(v, float) else v for k, v in snapshot.items()}})
        print(f"   {model:14} risk      {month}  {'ok' if answer else 'could not read answer'}")
    return rows