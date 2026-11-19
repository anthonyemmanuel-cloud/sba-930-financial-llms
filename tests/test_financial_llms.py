import re

import numpy as np
import pandas as pd
import pytest

from sba_930_financial_llms import data, experiments, llm, prompts


def write_fake_fred(folder):
    """Small made-up FRED files so the tests never need the internet or an API key."""
    rng = np.random.default_rng(0)

    def save(sid, dates, values):
        pd.DataFrame({"observation_date": dates.strftime("%Y-%m-%d"), sid: values}).to_csv(folder / f"{sid}.csv", index=False)

    months = pd.date_range("2005-01-01", "2026-10-01", freq="MS")
    cpi = [f"{v:.3f}" for v in 200 * np.exp(np.cumsum(rng.normal(0.002, 0.001, len(months))))]
    cpi[list(months).index(pd.Timestamp("2025-10-01"))] = "."          # a month that was never published
    save("CPIAUCSL", months, cpi)
    for sid, base in [("UNRATE", 5), ("FEDFUNDS", 2), ("MCOILWTICO", 70)]:
        save(sid, months, base + rng.normal(0, 1, len(months)).cumsum() * 0.1)
    quarters = pd.date_range("2005-01-01", "2026-07-01", freq="QS")
    save("GDPC1", quarters, 15000 * np.exp(np.cumsum(rng.normal(0.005, 0.005, len(quarters)))))
    days = pd.bdate_range("2005-01-03", "2026-11-13")
    for sid, base in [("DGS10", 3), ("T10Y2Y", 0.5), ("BAA10Y", 2.5), ("VIXCLS", 18)]:
        save(sid, days, base + np.sin(np.arange(len(days)) / 400))
    sp_days = days[days >= "2016-11-18"]
    save("SP500", sp_days, 2200 * np.exp(np.cumsum(rng.normal(0.0004, 0.01, len(sp_days)))))
    weeks = pd.date_range("2005-01-07", "2026-11-13", freq="W-FRI")
    save("NFCI", weeks, np.sin(np.arange(len(weeks)) / 100) * 0.5 - 0.3)


@pytest.fixture
def offline(tmp_path, monkeypatch):
    data_folder = tmp_path / "data"
    data_folder.mkdir()
    write_fake_fred(data_folder)
    monkeypatch.setattr(data, "DATA_FOLDER", data_folder)
    monkeypatch.setattr(llm, "RESULTS_FOLDER", tmp_path / "results")
    monkeypatch.setattr(llm, "FAKE", True)
    return data.load_data()


def test_inflation_is_percent_change_from_a_year_earlier(offline):
    monthly, _ = offline
    cpi = data.to_monthly(data.read_series("CPIAUCSL"))
    expected = (cpi["2024-06-01"] / cpi["2023-06-01"] - 1) * 100
    assert monthly.loc["2024-06-01", "inflation"] == pytest.approx(expected, abs=0.01)


def test_unpublished_month_stays_missing(offline):
    monthly, _ = offline
    assert pd.isna(monthly.loc["2025-10-01", "inflation"])


def test_month_window_never_shows_the_future(offline):
    monthly, _ = offline
    past, actual = data.month_window(monthly["oil"], "2022-06", 36, 6)
    assert len(past) == 36 and past.index[-1] == pd.Timestamp("2022-06-01")
    assert list(actual.index) == list(pd.date_range("2022-07-01", periods=6, freq="MS"))


def test_gdp_growth_is_annualized_from_real_gdp(offline):
    _, gdp = offline
    real = data.read_series("GDPC1")
    expected = ((real["2024-04-01"] / real["2024-01-01"]) ** 4 - 1) * 100
    assert gdp["2024-04-01"] == pytest.approx(expected, abs=0.05)


def test_quarter_window_labels(offline):
    _, gdp = offline
    past, actual = data.quarter_window(gdp, "2024Q4", 12, 4)
    assert data.quarter_label(past.index[-1]) == "2024Q4"
    assert [data.quarter_label(d) for d in actual.index] == ["2025Q1", "2025Q2", "2025Q3", "2025Q4"]


def test_masked_prompt_has_no_years():
    spec = experiments.PATH_TASKS["inflation"]
    _, user = prompts.path_prompt(spec, [3.0] * 36, prompts.masked_labels(36),
                                  prompts.masked_labels(6, future=True), "baseline")
    assert not re.search(r"\b(19|20)\d\d\b", user)
    assert "t-35: 3.0" in user and "t0: 3.0" in user and "t+6" in user


def test_missing_values_are_labelled_not_published():
    spec = experiments.PATH_TASKS["inflation"]
    _, user = prompts.path_prompt(spec, [3.0, float("nan"), 2.9], ["a", "b", "c"], ["d"], "optimized")
    assert "b: not published" in user and "Latest value: 2.9" in user


@pytest.mark.parametrize("text, expected", [
    ('{"forecast": [1, 2]}', {"forecast": [1, 2]}),
    ('Sure!\n```json\n{"change_pct": 4.5}\n```\nGood luck.', {"change_pct": 4.5}),
    ("I cannot forecast this.", None),
    ('{"broken": ', None),
])
def test_parse_json(text, expected):
    assert llm.parse_json(text) == expected


def test_score_path_against_naive():
    score = experiments.score_path([11, 12], [10, 14], last=10, low=9, high=15)
    assert score["mae"] == pytest.approx(1.5)          # |11-10| and |12-14|
    assert score["naive_mae"] == pytest.approx(2.0)    # |10-10| and |10-14|
    assert score["dir_hit"] is True and score["covered"] is True


def test_self_consistency_uses_the_median():
    answers = [{"forecast": [1, 10]}, {"forecast": [2, 20]}, {"forecast": [9, 30]}, {"forecast": [5]}]
    combined = experiments.combine(answers, 2)
    assert combined["forecast"] == [2, 20] and combined["samples"] == 3


def test_reference_risk_levels():
    levels = experiments.reference_levels({"vix": 35, "credit_spread": 2.0, "nfci": -0.1})
    assert levels == {"market_volatility": "High", "credit": "Low", "liquidity": "Medium"}


def test_answers_are_cached(offline):
    first = llm.ask("gpt-oss-120b", "", "hello", meta={"kind": "stock"})
    second = llm.ask("gpt-oss-120b", "", "hello", meta={"kind": "stock"})
    llm.ask("gpt-oss-120b", "", "hello", sample=1, meta={"kind": "stock"})
    assert first == second
    assert len(list((llm.RESULTS_FOLDER / "cache" / "gpt-oss-120b").glob("*.json"))) == 2


def test_full_run_offline(offline):
    monthly, gdp = offline
    rows = []
    for model in llm.MODELS:
        rows += experiments.run_stock(model, "baseline", monthly)
        rows += experiments.run_path("gdp", model, "optimized", monthly, gdp)
        rows += experiments.run_path("inflation", model, "masked", monthly, gdp)
    rows += experiments.ensemble(rows)
    assert all(r["valid"] for r in rows)
    assert {r["period"] for r in rows} == {"seen", "unseen"}
    assert any(r["model"] == "ensemble" for r in rows)
    summary = experiments.summarize(rows)
    assert experiments.overall(summary, "gdp", "ensemble", "ensemble")["readable"] == 6
    risk = experiments.run_risk("gpt-oss-20b", monthly)
    assert len(risk) == len(data.RISK_DATES) and all(r["levels"]["credit"] for r in risk)