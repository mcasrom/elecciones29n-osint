#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_DIR"

export TZ=Europe/Madrid
TODAY=$(date +%Y%m%d)
NOW=$(date '+%F %T %Z')

STATE_DIR="$HOME/.config/elecciones29n"
mkdir -p "$STATE_DIR"

echo "[run_daily] $NOW"

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -q --upgrade pip
  pip install -q -r requirements.txt
else
  source .venv/bin/activate
fi

# 1) Ingesta (fallo de red no rompe: se conserva el histórico)
PYTHONPATH="$REPO_DIR" python3 -m ingest.electomania || echo "[run_daily] aviso: ingesta sin novedades o falló"

# 2) Agregación
PYTHONPATH="$REPO_DIR" python3 -m agg.aggregate

# 3) Build estático
PYTHONPATH="$REPO_DIR" python3 -m gen.build

# 4) OG image (PIL del sistema; best-effort)
if /usr/bin/python3 -c "import PIL" 2>/dev/null; then
  /usr/bin/python3 gen/gen_og.py || echo "[run_daily] aviso: og.png no generado"
fi

# 5) IndexNow (best-effort)
/usr/bin/python3 scripts/indexnow_push.py || echo "[run_daily] aviso: indexnow falló"

touch "$STATE_DIR/last_run_$TODAY"
echo "[run_daily] OK"
