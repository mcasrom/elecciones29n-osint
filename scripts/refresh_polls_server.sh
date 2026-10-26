#!/usr/bin/env bash
# Refresco de sondeos en el servidor (14:15 y 20:15).
# Solo reconstruye/publica si cambia polls_history.csv. No carga tablas de
# prensa a medias: watch_sondeos.py deja candidatos para revisión.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
PY=".venv/bin/python"
[ -x "$PY" ] || PY="python3"
before=$(sha256sum data/polls_history.csv | cut -d' ' -f1)
PYTHONPATH=. "$PY" -m ingest.electomania || echo "[refresh-server] aviso: Electomania sin novedades"
PYTHONPATH=. "$PY" -m ingest.ondacero || echo "[refresh-server] aviso: Onda Cero sin novedades"
PYTHONPATH=. "$PY" scripts/watch_sondeos.py || echo "[refresh-server] aviso: watcher"
after=$(sha256sum data/polls_history.csv | cut -d' ' -f1)
if [ "$before" = "$after" ]; then
  echo "[refresh-server] sin sondeos nuevos; no se reconstruye"
  exit 0
fi
echo "[refresh-server] histórico cambiado; reconstruyendo y publicando"
exec bash scripts/run_daily_server.sh
