#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."

PY=".venv/bin/python"
[ -x "$PY" ] || PY="python3"

echo "[check] compilando"
$PY -m compileall -q agg gen ingest scripts tests

echo "[check] tests"
PYTHONPATH=. $PY -m unittest discover -s tests

echo "[check] validando sitio publicado local (web/)"
$PY scripts/validate_site.py web

echo "[check] auditoría de datos"
PYTHONPATH=. $PY scripts/audit_datos.py

echo "[check] OK"
