"""Command line entry point. Run one part at a time with --part."""

import argparse
import json

from . import experiments, llm, report
from .data import load_data

PARTS = ["data", "forecast", "economy", "risk", "optimize", "all"]


def run_forecast(monthly, gdp):
    print("\n=== Requirement 1: Financial forecasting (stock market and oil) ===")
    rows = []
    for model in llm.MODELS:
        rows += experiments.run_stock(model, "baseline", monthly)
        rows += experiments.run_path("oil", model, "baseline", monthly, gdp)
    return rows


def run_economy(monthly, gdp):
    print("\n=== Requirement 2: Economic trend forecasting (inflation and GDP) ===")
    rows = []
    for model in llm.MODELS:
        for task in ("inflation", "gdp"):
            rows += experiments.run_path(task, model, "baseline", monthly, gdp)
    return rows


def run_optimize(monthly, gdp):
    print("\n=== Requirement 4: Optimization ===")
    rows = run_forecast(monthly, gdp) + run_economy(monthly, gdp)   # baseline answers come from the cache
    for model in llm.MODELS:
        for variant in ("optimized", "masked"):
            rows += experiments.run_stock(model, variant, monthly)
            for task in experiments.PATH_TASKS:
                rows += experiments.run_path(task, model, variant, monthly, gdp)
        for task in ("oil", "inflation"):
            rows += experiments.run_path(task, model, "self_consistency", monthly, gdp)
    return rows + experiments.ensemble(rows)


def print_summary(summary, tasks, variants):
    for task in tasks:
        for variant in variants:
            for model in list(llm.MODELS) + ["ensemble"]:
                o = experiments.overall(summary, task, model, variant)
                if o:
                    print(f"{task:9} {variant:16} {model:14} error {o['mae']:8.2f} | naive {o['naive_mae']:8.2f} "
                          f"| skill {o['skill']:+.0%} | direction {o['direction']:.0%}")


def main():
    parser = argparse.ArgumentParser(description="SBA 930: Evaluating LLMs for financial forecasting and risk")
    parser.add_argument("--part", choices=PARTS, default="all")
    part = parser.parse_args().part
    monthly, gdp = load_data()
    folder = llm.RESULTS_FOLDER
    folder.mkdir(parents=True, exist_ok=True)
    print(f"Loaded {len(monthly)} months of market and economic data and {len(gdp)} quarters of GDP growth")
    try:
        if part in ("data", "all"):
            report.save(folder, "01_datasets_and_models.md", report.datasets_report(monthly, gdp))
        if part in ("forecast", "all"):
            rows = run_forecast(monthly, gdp)
            summary = experiments.summarize(rows)
            report.save_rows(folder, "forecast_rows", rows)
            report.save(folder, "02_financial_forecasting.md", report.forecasting_report(rows, summary))
            print_summary(summary, ["stock", "oil"], ["baseline"])
        if part in ("economy", "all"):
            rows = run_economy(monthly, gdp)
            summary = experiments.summarize(rows)
            report.save_rows(folder, "economy_rows", rows)
            report.save(folder, "03_economic_forecasts.md", report.economy_report(rows, summary))
            print_summary(summary, ["inflation", "gdp"], ["baseline"])
        if part in ("risk", "all"):
            print("\n=== Requirement 3: Risk identification and mitigation ===")
            rows = [r for model in llm.MODELS for r in experiments.run_risk(model, monthly)]
            report.save_rows(folder, "risk_rows", rows)
            report.save(folder, "04_risk_analysis.md", report.risk_report(rows))
            for model in llm.MODELS:
                matches = sum(r["matches"] for r in rows if r["model"] == model)
                print(f"{model:14} risk levels matching the rule reference: {matches}/{3 * len([r for r in rows if r['model'] == model])}")
        if part in ("optimize", "all"):
            rows = run_optimize(monthly, gdp)
            summary = experiments.summarize(rows)
            report.save_rows(folder, "optimization_rows", rows)
            summary.to_csv(folder / "summary_all_methods.csv", index=False)
            report.save(folder, "05_optimization.md", report.optimization_report(rows, summary))
            print_summary(summary, ["stock", "oil", "inflation", "gdp"],
                          ["baseline", "optimized", "self_consistency", "ensemble"])
    except llm.DailyLimitReached as error:
        print(f"\nStopped: {error}")
        raise SystemExit(1)