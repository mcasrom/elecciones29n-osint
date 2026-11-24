# Noche electoral 29N — runbook

## Antes de publicar

- Comprobar que el blackout ha terminado.
- Usar fuente oficial: Interior, JEC o dato oficial publicado.
- No usar exit polls, medios ni proyecciones como resultado oficial.
- No publicar sin `fuente_url`.

## 1. Rellenar la entrada

Editar `data/entrada_resultados.csv`:

```csv
tipo,clave,valor,fuente_url
participacion,,66.50,https://…
validos,,24300000,https://…
diputados,PP,137,https://…
votos,PP,8160837,https://…
```

Reglas:

- `participacion`: 0–100.
- `validos`: votos válidos, obligatorio si hay `votos`.
- `diputados`: 0–350 y suma ≤350.
- `votos`: votos por partido.
- `fuente_url`: obligatoria; sin ella no se publica.

## 2. Importar y publicar

```bash
cd /home/deploy/elecciones29n-osint
.venv/bin/python scripts/import_resultados.py
./scripts/run_daily_server.sh
.venv/bin/python scripts/canary_live.py
/home/deploy/scripts/cf_purge.sh pruebapublica
```

O en un solo paso:

```bash
bash scripts/noche_electoral_run.sh
```

## 3. Comprobar

- `/noche-electoral.html` muestra participación, escaños y fuente.
- `/postelectoral.html` muestra la calibración si hay snapshot y resultados.
- `/data/resultados_29n.json` responde 200.
- Canario OK y Cloudflare purgado.

## Fuente automática

`scripts/probe_resultados_oficiales.py` comprueba el acceso a las fuentes candidatas. No escribe datos ni publica. La ingesta automática solo se activará cuando una fuente primaria oficial responda de forma estable y su formato esté validado.
