#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_DIR"

export TZ=Europe/Madrid
TODAY=$(date +%Y%m%d)
NOW=$(date '+%F %T %Z')

mkdir -p "$REPO_DIR/logs" "$HOME/.config/elecciones29n" "$HOME/.local/state/elecciones29n"

echo "[run_daily_server] $NOW"

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -q --upgrade pip
  pip install -q -r requirements.txt
else
  source .venv/bin/activate
fi

STAGE="web_tmp"
rm -rf "$STAGE" web_prev
cp -a web "$STAGE"

PYTHONPATH="$REPO_DIR" python3 -m ingest.electomania || echo "[run_daily_server] aviso: electomania sin novedades"
PYTHONPATH="$REPO_DIR" python3 -m ingest.ondacero || echo "[run_daily_server] aviso: ondacero sin novedades"

[ ! -f data/censo_2026.json ] || [ -n "$(find data/censo_2026.json -mtime +30 2>/dev/null)" ] && PYTHONPATH="$REPO_DIR" python3 -m ingest.censo || true
[ ! -f data/participacion.json ] || [ -n "$(find data/participacion.json -mtime +30 2>/dev/null)" ] && PYTHONPATH="$REPO_DIR" python3 -m ingest.participacion || true
[ ! -f data/escanos_2026.json ] || [ -n "$(find data/escanos_2026.json -mtime +30 2>/dev/null)" ] && PYTHONPATH="$REPO_DIR" python3 -m ingest.escanos || true
if [ ! -f data/congreso-oficial.json ] || [ data/raw/elecciones-congreso.xlsx -nt data/congreso-oficial.json ]; then
  PYTHONPATH="$REPO_DIR" python3 -m ingest.congreso_oficial || echo "[run_daily_server] aviso: resultados oficiales sin actualizar"
fi

PYTHONPATH="$REPO_DIR" python3 -m agg.aggregate --out "$STAGE/data"
PYTHONPATH="$REPO_DIR" python3 -m gen.build --out "$STAGE"
/usr/bin/python3 -c "import PIL" 2>/dev/null && /usr/bin/python3 gen/gen_og.py --out "$STAGE/og.png" || true
if [ ! -f "$STAGE/data/blackout.json" ]; then
  /usr/bin/python3 gen/gen_card_robustez.py --data "$STAGE/data/latest.json" --out "$STAGE/og-robustez.png" || true
fi
/usr/bin/python3 gen/gen_card_glosario.py --out "$STAGE/og-glosario.png" || true

if ! /usr/bin/python3 scripts/validate_site.py "$STAGE" > "$HOME/.local/state/elecciones29n/validate.log" 2>&1; then
  echo "[run_daily_server] VALIDACIÓN FALLIDA — no se publica"
  cat "$HOME/.local/state/elecciones29n/validate.log"
  exit 1
fi

[ -d web ] && mv web web_prev
mv "$STAGE" web

rsync -a --delete web/ /var/www/elecciones29n/
for _f in index.html glosario.html robustez.html como-leer.html circunscripciones.html circunscripcion/madrid.html privacidad.html; do
  [ -f "/var/www/elecciones29n/$_f" ] || { echo "[run_daily_server] falta $_f en /var/www"; exit 1; }
done

if [ -f data/subs.db ]; then
  _backup_dir="$HOME/backups/elecciones29n"
  _backup="$_backup_dir/subs-$TODAY.db"
  mkdir -p "$_backup_dir"
  if python3 - "$PWD/data/subs.db" "$_backup" <<'PY'
import os
import sqlite3
import sys

src = sqlite3.connect(sys.argv[1])
dst = sqlite3.connect(sys.argv[2])
with dst:
    src.backup(dst)
dst.close()
src.close()
os.chmod(sys.argv[2], 0o600)
PY
  then
    find "$_backup_dir" -name 'subs-*.db' -mtime +30 -delete
    echo "[run_daily_server] copia de suscriptores: $_backup"
  else
    rm -f "$_backup"
    echo "[run_daily_server] aviso: no se pudo copiar data/subs.db"
  fi
fi

sleep 3
/usr/bin/python3 scripts/canary_live.py > "$HOME/.local/state/elecciones29n/canary.log" 2>&1 || echo "[run_daily_server] canario con aviso"

/usr/bin/python3 scripts/indexnow_push.py 2>/dev/null || true
[ -x /home/deploy/scripts/cf_purge.sh ] && /home/deploy/scripts/cf_purge.sh pruebapublica 2>/dev/null || true

rm -f "$HOME/.config/elecciones29n/last_error"
touch "$HOME/.config/elecciones29n/last_run_$TODAY"
echo "[run_daily_server] OK $(date '+%F %T')"
