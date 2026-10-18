#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_DIR"

export TZ=Europe/Madrid
TODAY=$(date +%Y%m%d)
NOW=$(date '+%F %T %Z')

STATE_DIR="$HOME/.config/elecciones29n"
STATE_LOG_DIR="$HOME/.local/state/elecciones29n"
mkdir -p "$STATE_DIR" "$STATE_LOG_DIR"

echo "[run_daily] $NOW"

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -q --upgrade pip
  pip install -q -r requirements.txt
else
  source .venv/bin/activate
fi

STAGE="web_tmp"

# Se parte de la última versión buena: si algo falla, no se toca web/.
rm -rf "$STAGE" web_prev
cp -a web "$STAGE"

# 1) Ingesta (un fallo de red no rompe: se conserva el histórico)
PYTHONPATH="$REPO_DIR" python3 -m ingest.electomania || echo "[run_daily] aviso: ingesta sin novedades o falló"
PYTHONPATH="$REPO_DIR" python3 -m ingest.ondacero || echo "[run_daily] aviso: Onda Cero sin novedades o falló"

# 1b) Censo (estático; solo si falta o tiene más de 30 días)
if [ ! -f data/censo_2026.json ] || [ -n "$(find data/censo_2026.json -mtime +30 2>/dev/null)" ]; then
  PYTHONPATH="$REPO_DIR" python3 -m ingest.censo || echo "[run_daily] aviso: censo no actualizado"
fi

# 1c) Participación histórica (estática; solo si falta o >30 días)
if [ ! -f data/participacion.json ] || [ -n "$(find data/participacion.json -mtime +30 2>/dev/null)" ]; then
  PYTHONPATH="$REPO_DIR" python3 -m ingest.participacion || echo "[run_daily] aviso: participación no actualizada"
fi

# 1d) Escaños por provincia (estático; solo si falta o >30 días)
if [ ! -f data/escanos_2026.json ] || [ -n "$(find data/escanos_2026.json -mtime +30 2>/dev/null)" ]; then
  PYTHONPATH="$REPO_DIR" python3 -m ingest.escanos || echo "[run_daily] aviso: escaños no actualizados"
fi

# 2) Agregación (escribe en el staging)
PYTHONPATH="$REPO_DIR" python3 -m agg.aggregate --out "$STAGE/data"

# 3) Build estático en staging
PYTHONPATH="$REPO_DIR" python3 -m gen.build --out "$STAGE"

# 4) OG (PIL del sistema; best-effort)
if /usr/bin/python3 -c "import PIL" 2>/dev/null; then
  /usr/bin/python3 gen/gen_og.py --out "$STAGE/og.png" || echo "[run_daily] aviso: og.png no generado"
fi

# 5) Validación: si falla, NO se publica y se conserva la última versión
if ! /usr/bin/python3 scripts/validate_site.py "$STAGE" > "$STATE_LOG_DIR/validate.log" 2>&1; then
  echo "[run_daily] VALIDACIÓN FALLIDA — no se publica"
  cat "$STATE_LOG_DIR/validate.log"
  date '+%F %T' > "$STATE_DIR/last_error"
  cat "$STATE_LOG_DIR/validate.log" >> "$STATE_DIR/last_error"
  if command -v notify-send >/dev/null; then
    notify-send -u critical "Elecciones29N" "Build no válido: se mantiene la última versión publicada. Ver ~/.local/state/elecciones29n/validate.log"
  fi
  exit 1
fi
echo "[run_daily] $(tail -1 "$STATE_LOG_DIR/validate.log")"

# 6) Swap atómico (se conserva web_prev para revertir a mano)
mv web web_prev
mv "$STAGE" web

# 7) Publicar
bash "$REPO_DIR/scripts/rsync_push.sh" || echo "[run_daily] aviso: rsync falló"

# 8) Canario en vivo: detecta que el despliegue no muestra el gráfico
sleep 3
if ! /usr/bin/python3 scripts/canary_live.py > "$STATE_LOG_DIR/canary.log" 2>&1; then
  echo "[run_daily] CANARIO FALLIDO"
  cat "$STATE_LOG_DIR/canary.log"
  date '+%F %T' > "$STATE_DIR/last_error"
  cat "$STATE_LOG_DIR/canary.log" >> "$STATE_DIR/last_error"
  if command -v notify-send >/dev/null; then
    notify-send -u critical "Elecciones29N" "El sitio publicado no supera el canario (gráfico/metadatos). Ver ~/.local/state/elecciones29n/canary.log"
  fi
  exit 1
fi

# 9) Avisar a buscadores y purgar edge (best-effort)
/usr/bin/python3 scripts/indexnow_push.py || echo "[run_daily] aviso: indexnow falló"
if [ -x /home/miguelc/Desktop/demo/cf_purge.sh ]; then
  bash /home/miguelc/Desktop/demo/cf_purge.sh pruebapublica || echo "[run_daily] aviso: purge CF falló"
fi

rm -f "$STATE_DIR/last_error"
touch "$STATE_DIR/last_run_$TODAY"
echo "[run_daily] OK"
