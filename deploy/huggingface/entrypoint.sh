#!/usr/bin/env bash
# Generates config.toml from Space secrets, then starts the Streamlit UI.
set -euo pipefail
cd "$(dirname "$0")/../.."
python deploy/huggingface/bootstrap_config.py
exec streamlit run ./webui/Main.py --server.enableCORS=true
