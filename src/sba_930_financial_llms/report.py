"""Turn the results into Markdown tables saved in the results folder."""

import json

import pandas as pd

from . import data, experiments, llm

MODEL_NAMES = list(llm.MODELS)
TASK_TITLES = {"stock": "Stock market (S&P 500, 6-month % change)", "oil": "Commodity (WTI oil, $ per barrel)",
               "inflation": "CPI inflation (%)", "gdp": "Real GDP growth (%)"}
VARIANT_TITLES = {"baseline": "Baseline prompt", "optimized": "Optimized prompt",
                  "self_consistency": "Optimized + self-consistency (median of 3)",
                  "ensemble": "Ensemble of both models (optimized)", "masked": "Dates hidden"}


def fmt(value, decimals=2, percent=False):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return "n/a"
    return f"{value * 100:.0f}%" if percent else f"{value:,.{decimals}f}"


def table(header, rows):
    lines = ["| " + " | ".join(header) + " |", "| " + " | ".join("---" for _ in header) + " |"]
    lines += ["| " + " | ".join(str(c) for c in row) + " |" for row in rows]
    return "\n".join(lines)


def save(results_folder, name, text):
    path = results_folder / name
    path.write_text(text.strip() + "\n")
    print(f"Saved: {path}")


def datasets_report(monthly, gdp):
    series = [(sid, "1. Economic indicators", d) for sid, d in data.ECONOMIC_SERIES.items()]
    series += [(sid, "2. Market and commodity prices", d) for sid, d in data.MARKET_SERIES.items()]
    summary = data.dataset_summary(monthly, gdp)
    models = [(name, company, mid, cutoff) for name, (mid, company, cutoff) in llm.MODELS.items()]
    return "\n\n".join([
        "# Datasets and models",
        "## FRED series downloaded",
        table(["Series ID", "Dataset", "Description"], series),
        "## Prepared columns",
        table(["Column", "First", "Last", "Values", "Missing inside range"],
              [[r.column, r.first.date(), r.last.date(), r.values, r.missing_inside] for r in summary.itertuples()]),
        "## Models",
        table(["Short name", "Company", "Groq model id", "Training data cutoff"], models),
        "## Forecast windows",
        f"Seen windows (both models may remember these years): {', '.join(data.SEEN_MONTHS)} "
        f"and {', '.join(data.SEEN_QUARTERS)}.",
        f"Unseen windows (after both training cutoffs): {', '.join(data.UNSEEN_MONTHS)} "
        f"and {', '.join(data.UNSEEN_QUARTERS)}.",
    ])


def summary_table(summary, tasks, variants, models=MODEL_NAMES):
    rows = []
    for task in tasks:
        for variant in variants:
            for model in models:
                o = experiments.overall(summary, task, model, variant)
                if o:
                    rows.append([TASK_TITLES[task], VARIANT_TITLES[variant], model, f"{o['readable']}/{o['windows']}",
                                 fmt(o["mae"]), fmt(o["naive_mae"]), fmt(o["skill"], percent=True),
                                 fmt(o["direction"], percent=True), fmt(o["coverage"], percent=True)])
    return table(["Task", "Method", "Model", "Readable answers", "Avg error", "Naive error",
                  "Skill vs naive", "Direction right", "Actual inside range"], rows)


def period_table(summary, tasks, variant):
    rows = []
    for r in summary[(summary.variant == variant) & summary.task.isin(tasks)].itertuples():
        rows.append([TASK_TITLES[r.task], r.model, r.period, fmt(r.mae), fmt(r.naive_mae),
                     fmt(r.skill, percent=True), fmt(r.direction, percent=True)])
    return table(["Task", "Model", "Windows", "Avg error", "Naive error", "Skill vs naive", "Direction right"], rows)


def window_table(rows, task, variant):
    """Forecast for the last period of each window next to the real value."""
    found = [r for r in rows if r["task"] == task and r["variant"] == variant]
    out = []
    for cutoff in dict.fromkeys(r["cutoff"] for r in found):
        group = {r["model"]: r for r in found if r["cutoff"] == cutoff}
        first = next(iter(group.values()))
        actual = [a for a in first["actual"] if a is not None]
        line = [cutoff, first["period"]] + ([] if task == "stock" else [fmt(first["last"])])
        line.append(fmt(actual[-1] if actual else None))
        for model in MODEL_NAMES:
            r = group.get(model)
            line.append("no answer" if not r or not r["valid"] else
                        f"{fmt(r['forecast'][-1])} (range {fmt(r['low'])} to {fmt(r['high'])}, error {fmt(r.get('mae'))})")
        out.append(line)
    header = ["Cutoff", "Window", "Actual 6-month change %"] if task == "stock" else \
        ["Cutoff", "Window", "Last value before forecast", "Actual (final period)"]
    return table(header + [f"{m} forecast" for m in MODEL_NAMES], out)


def reasoning_examples(rows, task, variant="baseline"):
    lines = []
    for r in rows:
        if r["task"] == task and r["variant"] == variant and r["valid"] and r["cutoff"] in (
                data.UNSEEN_MONTHS[-1], data.UNSEEN_QUARTERS[-1], data.SEEN_MONTHS[0], data.SEEN_QUARTERS[0]):
            extra = f" Drivers: {', '.join(map(str, r.get('drivers') or []))}." if r.get("drivers") else ""
            lines.append(f"- **{r['model']}, {r['cutoff']}** (confidence {fmt(r.get('confidence'), 0)}): "
                         f"{r.get('reasoning', '')}{extra}")
    return "\n".join(lines)


def forecasting_report(rows, summary):
    return "\n\n".join([
        "# Requirement 1: LLM evaluation for financial forecasting",
        "Avg error is the mean absolute error (percentage points for the stock change, dollars for oil). "
        "Naive error is the error of simply assuming no change. Skill vs naive above 0% means the LLM beat "
        "the naive forecast. Actual inside range shows how often the real value fell inside the model's own low to high range.",
        "## Summary",
        summary_table(summary, ["stock", "oil"], ["baseline"]),
        "## Seen and unseen windows",
        period_table(summary, ["stock", "oil"], "baseline"),
        "## Scenario 1. Impact of economic policy on the stock market",
        window_table(rows, "stock", "baseline"),
        "### Example reasoning", reasoning_examples(rows, "stock"),
        "## Scenario 2. Commodity price trends (WTI oil)",
        window_table(rows, "oil", "baseline"),
        "### Example reasoning", reasoning_examples(rows, "oil"),
    ])


def path_detail(rows, task, variant="baseline"):
    out = []
    for r in rows:
        if r["task"] == task and r["variant"] == variant:
            out.append([r["cutoff"], r["model"], ", ".join(fmt(a, 1) for a in r["actual"]),
                        ", ".join(fmt(f, 1) for f in r["forecast"]) if r["valid"] else "no answer",
                        fmt(r.get("mae"))])
    return table(["Cutoff", "Model", "Actual values", "Forecast values", "Avg error"], out)


def economy_report(rows, summary):
    return "\n\n".join([
        "# Requirement 2: Economic trend forecasting",
        "## Summary", summary_table(summary, ["inflation", "gdp"], ["baseline"]),
        "## Seen and unseen windows", period_table(summary, ["inflation", "gdp"], "baseline"),
        "## Inflation forecasts compared with actual data", path_detail(rows, "inflation"),
        "### Example reasoning", reasoning_examples(rows, "inflation"),
        "## GDP growth forecasts compared with actual data", path_detail(rows, "gdp"),
        "### Example reasoning", reasoning_examples(rows, "gdp"),
    ])


def risk_report(rows):
    out, agree = [], {m: [0, 0] for m in MODEL_NAMES}
    for month in data.RISK_DATES:
        group = {r["model"]: r for r in rows if r["month"] == month}
        first = next(iter(group.values()))
        s, ref = first["snapshot"], first["reference"]
        line = [month, fmt(s["vix"], 1), fmt(s["credit_spread"]), fmt(s["nfci"]),
                " / ".join(ref[n] for n in experiments.RISK_NAMES)]
        for model in MODEL_NAMES:
            r = group[model]
            line.append(" / ".join(str(r["levels"][n]) for n in experiments.RISK_NAMES) + f" ({r['matches']}/3)")
            agree[model][0] += r["matches"]
            agree[model][1] += 3
        out.append(line)
    parts = ["# Requirement 3: Risk identification and mitigation",
             "Levels are shown as market volatility / credit / liquidity. The reference levels come from simple "
             "rules (VIX under 20 Low, 20 to 30 Medium, over 30 High; Baa spread under 2.5 Low, 2.5 to 3.5 Medium, "
             "over 3.5 High; NFCI under -0.3 Low, -0.3 to 0 Medium, over 0 High).",
             table(["Month", "VIX", "Credit spread", "NFCI", "Rule reference"] + MODEL_NAMES, out),
             "## Agreement with the rule reference",
             table(["Model", "Levels matching"], [[m, f"{a}/{t} ({a / t:.0%})"] for m, (a, t) in agree.items()])]
    for r in rows:
        parts.append(f"## {r['model']}, {r['month']}")
        for name in experiments.RISK_NAMES:
            strategies = r["mitigation"].get(name) or []
            parts.append(f"- **{name.replace('_', ' ').title()}: {r['levels'][name]}.** {r['evidence'][name]} "
                         f"Mitigation: {' '.join(str(x) for x in strategies)}")
    return "\n\n".join(parts)


def optimization_report(rows, summary):
    masked = []
    for task in experiments.PATH_TASKS | {"stock": None}:
        for model in MODEL_NAMES:
            base = summary[(summary.task == task) & (summary.model == model) & (summary.variant == "baseline")
                           & (summary.period == "seen")]
            hidden = summary[(summary.task == task) & (summary.model == model) & (summary.variant == "masked")]
            if not base.empty and not hidden.empty:
                masked.append([TASK_TITLES[task], model, fmt(base.iloc[0].mae), fmt(hidden.iloc[0].mae),
                               fmt(base.iloc[0].naive_mae)])
    spreads = [[r["model"], TASK_TITLES[r["task"]], r["cutoff"], fmt(r.get("spread"))]
               for r in rows if r["variant"] == "self_consistency" and r.get("spread") is not None]
    return "\n\n".join([
        "# Requirement 4: Optimization and enhancement",
        "Methods tested. Optimized prompt = analyst role, calculated statistics, a step by step method that starts "
        "from the naive forecast, temperature 0 and JSON mode. Self-consistency = the optimized prompt asked 3 times "
        "at temperature 0.7, keeping the median. Ensemble = the average of both models' optimized forecasts.",
        "## Accuracy by method",
        summary_table(summary, ["stock", "oil", "inflation", "gdp"],
                      ["baseline", "optimized", "self_consistency", "ensemble"], MODEL_NAMES + ["ensemble"]),
        "## Memory test: real dates compared with hidden dates (seen windows only)",
        "If the error rises a lot when the dates are hidden, the model was probably remembering history "
        "instead of forecasting from the data.",
        table(["Task", "Model", "Error with real dates", "Error with dates hidden", "Naive error"], masked),
        "## Consistency of repeated answers (self-consistency samples)",
        "Spread is the standard deviation of the final forecast across the 3 samples. Lower means more consistent.",
        table(["Model", "Task", "Cutoff", "Spread"], spreads),
    ])


def save_rows(results_folder, name, rows):
    (results_folder / f"{name}.json").write_text(json.dumps(rows, indent=2, default=str))