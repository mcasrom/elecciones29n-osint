#!/usr/bin/env bash
set -euo pipefail
cd /home/deploy/elecciones29n-osint
export TZ=Europe/Madrid

echo "[reactivar-29n] $(date '+%F %T %Z')"

# 1) Reactivar los crons pausados para el archivo congelado.
python3 - <<'PY'
import subprocess
current = subprocess.check_output(["crontab", "-l"], text=True)
lines = current.splitlines()
out = []
for line in lines:
    if "REACTIVAR-29N-2026" in line:
        continue
    out.append(line.replace("# [ARCHIVO CONGELADO 2026-11-24] ", "", 1))
subprocess.run(["crontab", "-"], input="\n".join(out) + "\n", text=True, check=True)
print("[reactivar-29n] crons reactivados")
PY

# 2) Reconstruir y publicar el sitio normal (blackout ya terminado).
./scripts/run_daily_server.sh

# 3) Verificar que el banner de archivo congelado ha desaparecido.
python3 - <<'PY'
from pathlib import Path
root = Path("/var/www/elecciones29n")
bad = [p for p in root.rglob("*.html") if 'id="archive-banner"' in p.read_text(errors="ignore")]
if bad:
    for p in bad:
        s = p.read_text(errors="ignore")
        start = s.find('<div id="archive-banner"')
        if start != -1:
            end = s.find('</div>', start)
            if end != -1:
                p.write_text(s[:start] + s[end+6:], encoding="utf-8")
    print(f"[reactivar-29n] retirado banner de {len(bad)} páginas")
else:
    print("[reactivar-29n] sin banner")
PY

# 4) Refrescar los datos de sondeos y el agregado normal.
./scripts/refresh_polls_server.sh || true
./scripts/run_daily_server.sh

echo "[reactivar-29n] OK $(date '+%F %T %Z')"
