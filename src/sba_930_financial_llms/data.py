"""Download the two financial datasets from FRED and cut them into test windows."""

import os
import subprocess
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()

DATA_FOLDER = Path(os.environ.get("SBA930_DATA_DIR", "data"))
FRED_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={}"

# Dataset 1: economic indicators
ECONOMIC_SERIES = {
    "CPIAUCSL": "Consumer Price Index for all urban consumers (monthly)",
    "GDPC1": "Real GDP in billions of chained 2017 dollars (quarterly), turned into annualized growth %",
    "UNRATE": "Unemployment rate, percent (monthly)",
    "FEDFUNDS": "Federal funds interest rate, percent (monthly)",
    "DGS10": "10-year Treasury yield, percent (daily)",
    "T10Y2Y": "10-year minus 2-year Treasury yield spread (daily)",
}

# Dataset 2: market and commodity prices
MARKET_SERIES = {
    "SP500": "S&P 500 stock index (daily)",
    "MCOILWTICO": "WTI crude oil price, dollars per barrel (monthly)",
    "VIXCLS": "VIX stock market volatility index (daily)",
    "BAA10Y": "Baa corporate bond yield minus 10-year Treasury yield (daily)",
    "NFCI": "Chicago Fed National Financial Conditions Index (weekly)",
}

# Forecast windows. "Seen" windows end before both models' training cutoffs,
# so the models may remember what happened. "Unseen" windows are after both.
SEEN_MONTHS = ["2021-12", "2022-06", "2022-12"]
UNSEEN_MONTHS = ["2024-12", "2025-06", "2025-12"]
SEEN_QUARTERS = ["2021Q4", "2022Q2", "2022Q4"]
UNSEEN_QUARTERS = ["2024Q2", "2024Q4", "2025Q2"]

# Dates for the risk analysis, chosen to include calm and stressed markets
RISK_DATES = ["2008-10", "2017-06", "2020-03", "2022-09", "2023-03", "2025-04"]


BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
                  "(KHTML, like Gecko) Version/18.0 Safari/605.1.15",
    "Accept": "text/csv,text/plain,*/*",
    "Accept-Language": "en-US,en;q=0.9",
}


def looks_like_csv(text, series_id):
    return bool(text) and series_id in text.splitlines()[0]


def get_with_requests(series_id):
    response = requests.get(FRED_URL.format(series_id), headers=BROWSER_HEADERS, timeout=(10, 30))
    response.raise_for_status()
    return response.text


def get_with_curl(series_id):
    """macOS comes with curl. FRED sometimes answers curl when it ignores Python."""
    result = subprocess.run(["curl", "-sSL", "--max-time", "60", "-A", BROWSER_HEADERS["User-Agent"],
                             FRED_URL.format(series_id)], capture_output=True, text=True, check=True)
    return result.stdout


def get_with_api(series_id):
    """Official FRED API. Needs a free key saved as FRED_API_KEY in .env."""
    key = os.environ.get("FRED_API_KEY")
    if not key:
        raise RuntimeError("no FRED_API_KEY in .env")
    response = requests.get("https://api.stlouisfed.org/fred/series/observations", timeout=(10, 60),
                            params={"series_id": series_id, "api_key": key, "file_type": "json"})
    response.raise_for_status()
    rows = [f"{o['date']},{o['value']}" for o in response.json()["observations"]]
    return "\n".join([f"observation_date,{series_id}"] + rows) + "\n"


def download(series_id, force=False):
    """Save one FRED series as data/<id>.csv the first time, then reuse the file.
    Tries three ways, because FRED sometimes ignores requests from Python."""
    DATA_FOLDER.mkdir(parents=True, exist_ok=True)
    path = DATA_FOLDER / f"{series_id}.csv"
    if path.exists() and not force:
        return path
    print(f"   Downloading {series_id} from FRED...")
    for name, method in [("Python", get_with_requests), ("curl", get_with_curl), ("FRED API", get_with_api)]:
        try:
            text = method(series_id)
            if looks_like_csv(text, series_id):
                path.write_text(text)
                return path
            print(f"      {name}: FRED sent something that is not the data file")
        except Exception as error:   # try the next method
            print(f"      {name} did not work ({type(error).__name__})")
    raise SystemExit(
        f"\nCould not download {series_id}. Open this link in Safari, which downloads {series_id}.csv:\n"
        f"   {FRED_URL.format(series_id)}\n"
        f"Then move that file into the folder: {DATA_FOLDER.resolve()}\n"
        "and run the same command again. Files already in the data folder are reused.")


def read_series(series_id):
    """Read a FRED csv into a pandas Series indexed by date. Blank values are dropped."""
    df = pd.read_csv(download(series_id))
    values = pd.to_numeric(df.iloc[:, 1], errors="coerce")
    values.index = pd.to_datetime(df.iloc[:, 0])
    return values.dropna().rename(series_id)


def to_monthly(series, how="mean"):
    grouped = series.resample("MS")
    return grouped.last() if how == "last" else grouped.max() if how == "max" else grouped.mean()


def load_data():
    """Return (monthly table, quarterly GDP growth series)."""
    cpi = to_monthly(read_series("CPIAUCSL"))
    vix = read_series("VIXCLS")
    monthly = pd.DataFrame({
        "inflation": cpi.pct_change(12, fill_method=None) * 100,
        "fed_funds": to_monthly(read_series("FEDFUNDS")),
        "unemployment": to_monthly(read_series("UNRATE")),
        "treasury_10y": to_monthly(read_series("DGS10")),
        "yield_curve": to_monthly(read_series("T10Y2Y")),
        "sp500": to_monthly(read_series("SP500"), "last"),
        "oil": to_monthly(read_series("MCOILWTICO")),
        "vix": to_monthly(vix),
        "vix_max": to_monthly(vix, "max"),
        "credit_spread": to_monthly(read_series("BAA10Y")),
        "nfci": to_monthly(read_series("NFCI")),
    }).round(2)
    real_gdp = read_series("GDPC1")
    # Annualized growth from the previous quarter, the same formula the BEA uses for its headline number
    gdp = (((real_gdp / real_gdp.shift(1)) ** 4 - 1) * 100).dropna().round(1).rename("gdp")
    return monthly, gdp


def month_label(date):
    return date.strftime("%Y-%m")


def quarter_label(date):
    return f"{date.year}Q{(date.month - 1) // 3 + 1}"


def month_window(series, cutoff, history, horizon):
    """History up to and including the cutoff month, plus the actual values after it."""
    end = pd.Period(cutoff, "M").to_timestamp()
    past = series.loc[:end].iloc[-history:]
    future = pd.date_range(end + pd.offsets.MonthBegin(1), periods=horizon, freq="MS")
    return past, series.reindex(future)


def quarter_window(series, cutoff, history, horizon):
    period = pd.Period(cutoff, "Q")
    past = series.loc[:period.start_time].iloc[-history:]
    future = [(period + i).start_time for i in range(1, horizon + 1)]
    return past, series.reindex(future)


def dataset_summary(monthly, gdp):
    """One row per series for the report."""
    rows = []
    for name, series in list(monthly.items()) + [("gdp", gdp)]:
        s = series.dropna()
        rows.append({"column": name, "first": s.index.min(), "last": s.index.max(),
                     "values": len(s), "missing_inside": int(series.loc[s.index.min():s.index.max()].isna().sum())})
    return pd.DataFrame(rows)