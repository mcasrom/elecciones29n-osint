#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_DIR"

export TZ=Europe/Madrid
TODAY=$(date +%Y%m%d)
NOW=$(date '+%F %T %Z')

STATE_DIR="$HOME/.config/elecciones29n"
mkdir -p "$STATE_DIR"

echo "[run_daily] $NOW"

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -q --upgrade pip
  pip install -q -r requirements.txt
else
  source .venv/bin/activate
fi

# Ingest + agregación + build
PYTHONPATH="$REPO_DIR" python3 -m agg.aggregate
PYTHONPATH="$REPO_DIR" python3 -m gen.build

touch "$STATE_DIR/last_run_$TODAY"
echo "[run_daily] OK"
