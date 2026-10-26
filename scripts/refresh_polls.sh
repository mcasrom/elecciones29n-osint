#!/usr/bin/env bash
# Refresco de sondeos (14:00 y 20:00): solo publica si cambió el histórico.
# Las fuentes estructuradas son Electomania y Onda Cero; los medios que solo
# publican tablas en HTML/imagen se revisan con watch_sondeos.py + entrada manual.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."

PY=".venv/bin/python"
[ -x "$PY" ] || PY="python3"
before=$(sha256sum data/polls_history.csv | cut -d' ' -f1)

PYTHONPATH=. "$PY" -m ingest.electomania || echo "[refresh] aviso: Electomania sin novedades"
PYTHONPATH=. "$PY" -m ingest.ondacero || echo "[refresh] aviso: Onda Cero sin novedades"
PYTHONPATH=. "$PY" scripts/watch_sondeos.py || echo "[refresh] aviso: watcher de prensa"

after=$(sha256sum data/polls_history.csv | cut -d' ' -f1)
if [ "$before" = "$after" ]; then
  echo "[refresh] sin sondeos nuevos; no se reconstruye"
  exit 0
fi
echo "[refresh] histórico cambiado; reconstruyendo y publicando"
exec bash scripts/run_daily.sh
