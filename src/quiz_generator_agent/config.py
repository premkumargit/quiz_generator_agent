
"""Central config loader for the project."""

import os
import json
from pathlib import Path
from dotenv import load_dotenv
from .logging_utils import setup_logging
from google.genai import types


load_dotenv()
setup_logging()

CONFIG_JSON_PATH = Path(__file__).parent / "config.json"
if CONFIG_JSON_PATH.exists():
    try:
        with CONFIG_JSON_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
        for k, v in data.items():
            os.environ.setdefault(k, str(v))
    except Exception as e:
        print(f"Warning: could not load config.json: {e}")



RETRY_CONFIG = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise RuntimeError("GOOGLE_API_KEY is not set. Please set it in .env, env vars, or config.json.")
