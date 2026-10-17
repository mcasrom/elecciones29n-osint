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

# Crear venv si no existe
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -q --upgrade pip
  pip install -q -r requirements.txt
else
  source .venv/bin/activate
fi

# Placeholder: aquí irá ingest + agg + build
# python3 -m ingest.electomania
# python3 -m agg.aggregate
# python3 -m gen.build

# Marcar ejecución OK
touch "$STATE_DIR/last_run_$TODAY"
echo "[run_daily] OK"
