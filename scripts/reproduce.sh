#!/usr/bin/env bash
set -euo pipefail
# Reconstruye el sitio con el código y el data/polls_history.csv actuales.
# Para un build histórico, congela antes el CSV y los JSON de entrada.
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="${1:-/tmp/e29n-repro}"
PY="$ROOT/.venv/bin/python"
[ -x "$PY" ] || PY="python3"
cd "$ROOT"
rm -rf "$OUT"
cp -a "$ROOT/web" "$OUT"
PYTHONPATH="$ROOT" "$PY" -m agg.aggregate --out "$OUT/data"
PYTHONPATH="$ROOT" "$PY" -m gen.build --out "$OUT"
echo "== hashes =="
sha256sum "$OUT/data/latest.json" "$OUT/data/robustez.json" "$OUT/data/status.json"
echo "== contrato =="
echo "schema: $OUT/data/v1/schema.json"
echo "changelog: $OUT/data/changelog.json"
echo "repro: $OUT"
