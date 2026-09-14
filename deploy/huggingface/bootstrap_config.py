"""Write config.toml for a hosted demo from environment variables.

Runs before Streamlit starts. Every variable is optional; unset ones keep the
value from config.example.toml. Set them as Space secrets:

  LLM_PROVIDER        pollinations (default, keyless) | openai | deepseek | gemini | ...
  OPENAI_API_KEY / OPENAI_BASE_URL / OPENAI_MODEL_NAME
  DEEPSEEK_API_KEY / GEMINI_API_KEY / MOONSHOT_API_KEY / QWEN_API_KEY
  PEXELS_API_KEYS     comma-separated; free at https://www.pexels.com/api/
  PIXABAY_API_KEYS    comma-separated
  HIDE_CONFIG         true to hide the settings panel from visitors (default: true)
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path

import toml

root = Path(__file__).resolve().parents[2]
config_file = root / "config.toml"
example_file = root / "config.example.toml"

if not config_file.exists():
    shutil.copyfile(example_file, config_file)

cfg = toml.load(config_file)
app = cfg.setdefault("app", {})


def env(name: str) -> str | None:
    value = os.getenv(name, "").strip()
    return value or None


def csv(name: str) -> list[str] | None:
    value = env(name)
    return [v.strip() for v in value.split(",") if v.strip()] if value else None


app["llm_provider"] = env("LLM_PROVIDER") or "pollinations"
app["hide_config"] = (env("HIDE_CONFIG") or "true").lower() == "true"

for key in (
    "openai_api_key",
    "openai_base_url",
    "openai_model_name",
    "deepseek_api_key",
    "gemini_api_key",
    "moonshot_api_key",
    "qwen_api_key",
    "grok_api_key",
    "pollinations_api_key",
):
    value = env(key.upper())
    if value:
        app[key] = value

for key in ("pexels_api_keys", "pixabay_api_keys"):
    value = csv(key.upper())
    if value:
        app[key] = value

app["video_source"] = env("VIDEO_SOURCE") or app.get("video_source", "pexels")

config_file.write_text(toml.dumps(cfg), encoding="utf-8")
print(f"config.toml written: provider={app['llm_provider']}, source={app['video_source']}")
