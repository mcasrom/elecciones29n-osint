#!/usr/bin/env bash
set -euo pipefail
cd /home/deploy/elecciones29n-osint
export TZ=Europe/Madrid

echo "[noche-29n] $(date '+%F %T %Z')"
if [ ! -s data/entrada_resultados.csv ]; then
  echo "[noche-29n] falta data/entrada_resultados.csv" >&2
  exit 1
fi
if [ -f data/blackout.json ]; then
  echo "[noche-29n] blackout activo: no se publican resultados" >&2
  exit 1
fi

# 1) Validar e importar la entrada manual (fuente obligatoria).
.venv/bin/python scripts/import_resultados.py

# 2) Reconstruir y publicar el sitio normal.
./scripts/run_daily_server.sh

# 3) Verificar la página pública y los datos.
.venv/bin/python scripts/canary_live.py

# 4) Purga explícita por si run_daily no la hizo.
if [ -x /home/deploy/scripts/cf_purge.sh ]; then
  /home/deploy/scripts/cf_purge.sh pruebapublica
fi

echo "[noche-29n] OK $(date '+%F %T %Z')"
