# Test 29N — protocolo

## Antes del 29-N

```bash
cd /home/deploy/elecciones29n-osint
.venv/bin/python -m unittest tests.test_noche_electoral -v
.venv/bin/python scripts/probe_resultados_oficiales.py
```

Objetivo: validar importación, rechazo sin fuente y accesibilidad de fuentes. No publica nada.

## 29-N

### 14:00 y 18:00

- Comprobar participación oficial.
- Si hay fuente, rellenar `data/entrada_resultados.csv` con `tipo=participacion`.
- No publicar si no hay `fuente_url`.

### 20:30 UTC / 21:30 CET

```bash
cd /home/deploy/elecciones29n-osint
bash scripts/reactivar_29n.sh
```

Verificar:

- banner retirado;
- crons restaurados;
- `/data/latest.json` y `/og.png` responden 200;
- build normal.

### Noche

Cuando haya resultados oficiales:

```bash
bash scripts/noche_electoral_run.sh
```

Comprueba:

- `/noche-electoral.html` con participación, escaños y fuente;
- `/data/resultados_29n.json` 200;
- canario y purga OK.

## Post 29-N

```bash
cd /home/deploy/elecciones29n-osint
.venv/bin/python scripts/import_resultados.py
./scripts/run_daily_server.sh
.venv/bin/python scripts/canary_live.py
```

Comprobar `/postelectoral.html`: calibración, MAE, sesgo y bloques.

## Regla

Sin fuente oficial: **no se publica**. Nunca usar exit polls ni proyecciones como resultado.
