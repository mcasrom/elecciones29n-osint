# elecciones29n-osint

Media agregada de sondeos publicados para las Elecciones Generales 29N de 2026. Generación estática local → publicación en servidor.

## Propósito

Muestra tendencia y dispersión (rango min–máx) de sondeos públicos, no predice resultados ni calcula intención de voto directa. Transparente, reproducible y con cumplimiento del blackout electoral (24–28 nov 2026).

## Modelo

- **Local-first**: genera estático en portátil (16GB, CPU modesto). No requiere servidor 24/7.
- **Cron local**: `systemd --user` timer a 08:00 (cuando trabajas). Watchdog avisa si no corrió al primer login.
- **Estático**: sube a `https://elecciones29n.pruebapublica.com` vía `rsync` (solo nginx).
- **Honesto**: media móvil ponderada por antigüedad + rango min–máx. Nunca mezcla señales sociales con agregados.

## Uso

```bash
# 1) Entorno
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2) Ejecutar
bash scripts/run_daily.sh
bash scripts/rsync_push.sh
```

## Cron local (systemd user)

```bash
mkdir -p ~/.config/systemd/user
cp systemd/*.service systemd/*.timer ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now elecciones29n.timer
```

## Blackout electoral (LOREG/JEC)

Entre **24–28 nov 2026** (incluidos) no se publican nuevos sondeos. El generador mantiene la última agregación válida con su fecha.

## Licencia

AGPL-3.0. Ver `LICENSE`.
