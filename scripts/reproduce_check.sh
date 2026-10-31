#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="/tmp/e29n-repro-check"
cd "$ROOT"
bash scripts/reproduce.sh "$OUT" >/tmp/e29n-repro-check.log 2>&1
PYTHONPATH="$ROOT" python3 - "$ROOT/web/data/latest.json" "$OUT/data/latest.json" "$ROOT/web/data/robustez.json" "$OUT/data/robustez.json" <<'PY'
import json
import sys

def norm(path):
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    for key in ("updated_at", "updated_at_iso", "generado", "generated_at", "build_ts", "build_date", "build_commit"):
        data.pop(key, None)
    return data

pairs = [(sys.argv[1], sys.argv[2]), (sys.argv[3], sys.argv[4])]
for left, right in pairs:
    if norm(left) != norm(right):
        print("DIFERENCIA de reconstrucción:", left)
        raise SystemExit(1)
print("reconstrucción OK: latest.json y robustez.json coinciden salvo timestamps")
PY
rm -rf "$OUT"
