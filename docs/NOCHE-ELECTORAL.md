# Noche electoral 29N · fuentes y plan

## Prueba de acceso (18-oct-2026)

| Fuente | Portátil | Servidor | Nota |
|---|---|---|---|
| JEC (`juntaelectoralcentral.es`) | 200 | 200 | accesible |
| Congreso (`congreso.es`) | 200 | — | accesible, no resultados en vivo |
| Interior (`interior.gob.es`) | 403 | 403 | Cloudflare |
| `infoelectoral.interior.gob.es` | timeout | timeout | no accesible |
| `resultados.elecciones.gob.es` | 000 | 000 | sin respuesta |
| `elecciones.mir.es` | timeout | timeout | no accesible |
| `api2.rtve.es` | 200 | — | API de medio, no oficial |
| `resultados.elpais.com` | 403 | — | bloqueado |

**Conclusión**: el dato oficial (Interior/MIR) **no es accesible por HTTP** desde
el portátil ni el servidor. La JEC sí, pero no publica resultados en vivo propios.

## Plan

1. **Fuente primaria**: Interior/JEC, si en la jornada responde.
2. **Fallback fiable**: **entrada manual** desde el navegador del dueño (que sí
   puede abrir la web oficial) en `data/entrada_resultados.csv` y
   `python scripts/import_resultados.py`.
3. **Nunca**: sondeos a pie de urna como resultados, ni proyecciones sin fuente.
4. **Medios** (RTVE/El País): solo como contraste, etiquetados como «dato de
   medio», nunca como oficial.

## Entrada manual

```
tipo,clave,valor,fuente_url
participacion,,66.50,https://…
diputados,PP,137,https://…
votos,PP,8160837,https://…
```

- `tipo`: `participacion`, `diputados` o `votos`.
- Validación: participación 0–100; escaños 0–350 y suma ≤350; partido conocido;
  **fuente obligatoria**.
- Salida: `data/resultados_29n.json` → bloque de resultados en
  `/noche-electoral.html` (participación, escaños y fuente).
- Si no hay fuente, **no se publica**.

## Qué se publica y cuándo

- 14:00/18:00: avances de participación (si hay dato oficial).
- ~22:30: primeros resultados oficiales.
- Madrugada: escrutinio.
- La web se regenera y valida; si el dato no cuadra, conserva la última versión.

## Comandos

```bash
.venv/bin/python scripts/import_resultados.py
bash scripts/run_daily.sh
.venv/bin/python scripts/canary_live.py
```
