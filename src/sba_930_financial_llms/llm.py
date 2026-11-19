"""Ask the two LLMs through Groq. Every answer is saved, so nothing is paid for twice."""

import hashlib
import json
import os
import random
import re
import time
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Short name: (Groq model id, company, training data cutoff)
MODELS = {
    "gpt-oss-20b": ("openai/gpt-oss-20b", "OpenAI", "2024-06"),
    "gpt-oss-120b": ("openai/gpt-oss-120b", "OpenAI", "2024-06"),
}

RESULTS_FOLDER = Path(os.environ.get("SBA930_RESULTS_DIR", "results"))
FAKE = os.environ.get("SBA930_FAKE") == "1"   # used by the tests, never calls the API
_client = None


class DailyLimitReached(Exception):
    pass


def cache_path(model, system, user, temperature, json_mode, sample):
    key = json.dumps([model, system, user, temperature, json_mode, sample])
    digest = hashlib.sha256(key.encode()).hexdigest()[:16]
    return RESULTS_FOLDER / "cache" / model / f"{digest}.json"


def ask(model, system, user, temperature=1.0, json_mode=False, sample=0, meta=None):
    """Return the model's text answer, from the cache if we already asked this exact prompt."""
    path = cache_path(model, system, user, temperature, json_mode, sample)
    if path.exists():
        return json.loads(path.read_text())["answer"]
    if FAKE:
        answer = fake_answer(model, meta or {}, sample)
    else:
        answer = call_groq(MODELS[model][0], system, user, temperature, json_mode)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"model": model, "temperature": temperature, "json_mode": json_mode,
                                "sample": sample, "system": system, "user": user,
                                "answer": answer}, indent=2))
    return answer


def call_groq(model_id, system, user, temperature, json_mode):
    global _client
    import groq
    if _client is None:
        if not os.environ.get("GROQ_API_KEY"):
            raise SystemExit("GROQ_API_KEY is missing. Put it in your .env file.")
        _client = groq.Groq()
    messages = [{"role": "user", "content": user}]
    if system:
        messages.insert(0, {"role": "system", "content": system})
    options = {"model": model_id, "messages": messages, "temperature": temperature,
               "max_completion_tokens": 1200}
    if model_id.startswith("openai/gpt-oss"):
        options["reasoning_effort"] = "low"
    if json_mode:
        options["response_format"] = {"type": "json_object"}
    for attempt in range(8):
        try:
            response = _client.chat.completions.create(**options)
            return response.choices[0].message.content or ""
        except groq.RateLimitError as error:
            wait = float(error.response.headers.get("retry-after", 20 * (attempt + 1)))
            if wait > 120:
                raise DailyLimitReached(
                    f"Groq's daily limit for {model_id} is used up (try again in about "
                    f"{wait / 60:.0f} minutes). Answers so far are saved, so just run the same command later.")
            print(f"   Rate limit reached, waiting {wait:.0f} seconds...")
            time.sleep(wait + 1)
        except groq.BadRequestError:
            if "response_format" not in options:
                raise
            options.pop("response_format")   # the model's JSON failed Groq's check, so ask again without JSON mode
        except (groq.APIConnectionError, groq.InternalServerError):
            print("   Connection problem, trying again in 10 seconds...")
            time.sleep(10)
    raise RuntimeError(f"Could not get an answer from {model_id} after several tries.")


def parse_json(text):
    """Pull the JSON object out of an answer, even if the model wrapped it in other text."""
    if not text:
        return None
    text = re.sub(r"```(?:json)?", "", text)
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end <= start:
        return None
    try:
        value = json.loads(text[start:end + 1])
    except json.JSONDecodeError:
        return None
    return value if isinstance(value, dict) else None


def fake_answer(model, meta, sample):
    """A made-up but well formed answer, so the whole pipeline can be tested offline."""
    rng = random.Random(f"{model}{json.dumps(meta, sort_keys=True)}{sample}")
    kind = meta.get("kind")
    if kind == "path":
        last, horizon = meta["last"], meta["horizon"]
        step = rng.uniform(-0.02, 0.02) * (abs(last) + 1)
        path = [round(last + step * (i + 1), 2) for i in range(horizon)]
        return json.dumps({"forecast": path, "low": round(path[-1] - abs(step) * 4 - 1, 2),
                           "high": round(path[-1] + abs(step) * 4 + 1, 2),
                           "direction": "up" if step > 0 else "down", "confidence": 60,
                           "reasoning": "Fake answer for testing."})
    if kind == "stock":
        change = round(rng.uniform(-8, 12), 1)
        return json.dumps({"change_pct": change, "low": change - 10, "high": change + 10,
                           "direction": "up" if change > 0 else "down", "confidence": 55,
                           "drivers": ["interest rates"], "reasoning": "Fake answer for testing."})
    if kind == "risk":
        levels = ["Low", "Medium", "High"]
        risk = {name: {"level": rng.choice(levels), "evidence": "Fake evidence."}
                for name in ("market_volatility", "credit", "liquidity")}
        risk["mitigation"] = {name: ["Fake strategy one.", "Fake strategy two."]
                              for name in ("market_volatility", "credit", "liquidity")}
        return "Here is my answer:\n```json\n" + json.dumps(risk) + "\n```"
    return "{}"