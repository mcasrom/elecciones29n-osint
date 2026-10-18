#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STATE_DIR="$HOME/.config/elecciones29n"
mkdir -p "$STATE_DIR"
TODAY=$(date +%Y%m%d)
STATE="$STATE_DIR/last_run_$TODAY"
MISSED="$STATE.missed"
NOW_H=$(date +%H%M)

if [ ! -f "$STATE" ] && [ ! -f "$MISSED" ] && [ "$NOW_H" -ge 0805 ]; then
  if command -v notify-send >/dev/null; then
    notify-send -u normal "Elecciones29N" "No se ejecutó a 08:00 (portátil apagado). Ejecuta scripts/run_daily.sh manualmente o espera siguiente día."
  fi
  touch "$MISSED"
fi

if [ -x "$REPO_DIR/scripts/needs.py" ]; then
  /usr/bin/python3 "$REPO_DIR/scripts/needs.py" digest --if-due || true
fi
