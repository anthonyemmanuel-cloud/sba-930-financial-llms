# SBA 930: Evaluating LLMs for Financial Forecasting and Risk Analysis

This project compares two large language models, OpenAI's **gpt-oss-20b** (20 billion parameters) and the much larger **gpt-oss-120b** (120 billion parameters)
(both run through Groq), on real financial data from FRED, the Federal Reserve Bank of St. Louis.

## What it does

| Part | Requirement | What happens |
| --- | --- | --- |
| `--part data` | Data sources | Downloads 11 FRED series into two datasets (economic indicators, market and commodity prices) |
| `--part forecast` | 1. Financial forecasting | Both models forecast the S&P 500 after policy changes and the price of WTI oil |
| `--part economy` | 2. Economic trends | Both models forecast CPI inflation and GDP growth, scored against what really happened |
| `--part risk` | 3. Risk analysis | Both models rate market volatility, credit and liquidity risk on 6 dates and suggest mitigation |
| `--part optimize` | 4. Optimization | Tests an optimized prompt, self-consistency, an ensemble of both models and a hidden-dates memory test |

Every forecast is compared with the actual data and with a naive "no change" forecast. Forecast windows
are split into **seen** windows (2022 and 2023, which the models may remember from training) and
**unseen** windows (2025 and 2026, after both models' training cutoffs).

## Setup

1. Install [uv](https://docs.astral.sh/uv/).
2. Create a free Groq API key at https://console.groq.com/keys.
3. Copy `.env.example` to `.env` and paste your key after `GROQ_API_KEY=`. Never commit `.env`.
4. Run the tests (no API key or internet needed):

```bash
uv run pytest
```

## Run

```bash
uv run sba-930-financial-llms --part data
uv run sba-930-financial-llms --part forecast
uv run sba-930-financial-llms --part economy
uv run sba-930-financial-llms --part risk
uv run sba-930-financial-llms --part optimize
```

Results are saved as Markdown tables in `results/`. Every answer from the models is saved in
`results/cache/`, so running a part again does not call the API again. The data download is not
committed; it is created the first time you run the project.

The free Groq plan has daily token limits. If a run stops with a daily limit message, wait and run
the same command again. It continues where it stopped.