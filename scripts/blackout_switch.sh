#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_DIR"
export TZ=Europe/Madrid
STAGE="web_blackout"

MODE="live"
if [ "${1:-}" = "--dry-run" ]; then MODE="dry"; fi
if [ "${1:-}" = "--simulate" ]; then MODE="simulate"; fi
if [ "${1:-}" = "--simulate-dry" ]; then MODE="simulate-dry"; fi
if [ "$MODE" = "live" ]; then
  if ! /usr/bin/python3 -c 'from datetime import datetime; import pytz; from agg import blackout; raise SystemExit(0 if blackout.is_blackout(datetime.now(pytz.timezone("Europe/Madrid"))) else 1)'; then
    echo "[blackout] fuera de ventana: no se toca nada"
    exit 0
  fi
fi

exec 9>/tmp/e29n-blackout.lock
flock -n 9 || { echo "[blackout] otro proceso en curso"; exit 0; }

rm -rf "$STAGE"
cp -a web "$STAGE"

/usr/bin/python3 - "$STAGE" <<'PY'
import os
import sys
from datetime import datetime
import pytz
from gen import build

out = sys.argv[1]
build.OUT = out
build.write_blackout_site(
    datetime(2026, 11, 24, 0, 0, tzinfo=pytz.timezone("Europe/Madrid")),
    "202611240000", "2026-11-24", open("VERSION", encoding="utf-8").read().strip() or "0.0",
    "blackout-switch",
)
PY

test -f "$STAGE/index.html"
test ! -f "$STAGE/data/latest.json"
test ! -f "$STAGE/og.png"
if find "$STAGE" -maxdepth 1 -name 'og*.png' | grep -q .; then
  echo "[blackout] quedan OG en la raíz" >&2
  exit 1
fi
if ! grep -q "Blackout electoral" "$STAGE/index.html"; then
  echo "[blackout] falta la página de blackout" >&2
  exit 1
fi

if [ "$MODE" = "dry" ] || [ "$MODE" = "simulate-dry" ]; then
  echo "[blackout] staging OK: $STAGE (sin publicar)"
  rm -rf "$STAGE"
  exit 0
fi
if [ "$MODE" = "simulate" ]; then
  echo "[blackout] simulación OK: $STAGE (sin publicar)"
  rm -rf "$STAGE"
  exit 0
fi

rsync -a --delete "$STAGE/" /var/www/elecciones29n/
rm -rf "$STAGE"
echo "[blackout] publicado en /var/www/elecciones29n"

if [ -x /home/deploy/scripts/cf_purge.sh ]; then
  /home/deploy/scripts/cf_purge.sh pruebapublica || echo "[blackout] aviso: purge CF falló"
fi
