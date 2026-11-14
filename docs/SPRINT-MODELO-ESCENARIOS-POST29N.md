# Sprint post-29N — modelo reproducible de escenarios

> **Creado:** 14-nov-2026 · **Ejecutar:** desde el 30-nov-2026, cuando pase el blackout.
> **Estado actual:** escenario congelado el **5-nov-2026** (12 sondeos · 8 casas). La media va al **9-nov** (15 sondeos · 10 casas). No se toca antes del 29N.
> **Página:** `https://elecciones29n.pruebapublica.com/escenarios.html`

## Decisión

**No actualizar la foto del escenario antes del 29N.** El escenario no es un pronóstico y ya está etiquetado como foto congelada. Lo que falta no son datos: es un **generador reproducible** con tests y backtest.

## Problema técnico

- `data/escenarios.json` está congelado y no tiene generador versionado.
- **No existen `seat_model.py` ni `backtest.py`**, tampoco en el historial de Git.
- No se puede verificar:
  - qué sondeos entraron;
  - si el Monte Carlo y el cálculo determinista usan el mismo universo;
  - si el p10–p90 incorpora dispersión entre casas;
  - si el backtest 2019 se reproduce con los parámetros actuales.
- No hay sondeos provinciales: el swing uniforme seguirá siendo una limitación declarada.

## Entradas

- `data/congreso.json` y `data/congreso-oficial.json`: resultados oficiales por provincia (2023; 2019 para el backtest).
- `data/escanos_2026.json`: 350 escaños y reparto por provincia.
- `data/polls_history.csv` y `web/data/latest.json`: sondeos y universo de la media.
- `data/fuentes_sondeos.csv`: casas, método y estado.
- Exclusiones que deben respetarse: `ElectoPanel`, `SW Demoscopia` y `ElectoPromedio` no entran como sondeos independientes.

## Regla de universo

El generador debe aceptar `--window-days` y **declarar la ventana usada en el JSON y en la página**. No mezclar:

- **14 días:** coherente con la media publicada; recomendable para la “foto” del escenario.
- **90 días:** más estable, pero cambia la definición actual y el rango.

Antes de implementar, comparar ambas salidas y documentar la decisión. Nunca sumar los 15 sondeos de la media con los 12 del escenario congelado.

## Modelo mínimo

1. **Cuotas nacionales** por partido a partir de los sondeos de la ventana.
2. **Swing uniforme** = cuota actual − resultado oficial 2023, por partido.
3. Aplicar el swing a cada provincia, normalizar a 100 y aplicar umbral del 3 %.
4. Reparto **D'Hondt provincial** con los escaños de `escanos_2026.json`.
5. **Monte Carlo:** muestrear sondeos con reemplazo, repetir 5.000 veces, calcular p10/p50/p90.
6. Semilla fija y resultado reproducible.
7. Si un partido no tiene etiqueta estable entre 2023 y 2026, documentar el mapeo; no inventar coaliciones.

## Backtest 2019

- Base: resultados oficiales del 28-abr-2019 por provincia.
- Objetivo: resultados oficiales del 10-nov-2019.
- Probar el **reparto provincial** con cuotas nacionales correctas; no es una prueba de los sondeos de 2026.
- Comparar MAE por partido y por bloque, no solo el total.
- Si el backtest no reproduce el MAE histórico, **no publicar** la nueva foto.

## Tests obligatorios

- [ ] D'Hondt con casos conocidos y umbral del 3 %.
- [ ] Reproducción de 2023 con cuotas oficiales: 350 escaños y reparto esperado.
- [ ] Backtest 2019 reproducible con semilla fija.
- [ ] Suma de escaños = 350; sin negativos; `p10 ≤ p50 ≤ p90`.
- [ ] Un sondeo `average` no duplica; trackings fuera.
- [ ] Dos ejecuciones con la misma semilla dan el mismo JSON.
- [ ] `validate_site` y `audit_datos` OK.

## salida y versionado

- `data/escenarios-20261105.json` se conserva como histórico.
- Nueva salida: `data/escenarios-YYYYMMDD.json` con:
  - `version`, `generated_at`, `cutoff`, `window_days`;
  - `n_polls`, `n_houses`, `seed`, `iterations`;
  - `model_version`, `source`, `sha256`.
- `web/data/escenarios.json` solo se actualiza desde el generador.
- La página debe leer fechas y contadores del JSON; no hardcodear “5 nov”.
- Mantener “foto congelada”, nunca “foto actual”.

## Interfaz

- Banner: foto congelada, fecha, ventana y diferencia con la media actual.
- Enlace a `robustez.html` y a la media.
- Si el escenario nuevo cambia la conclusión de bloques, explicarlo; no presentarlo como probabilidad.
- En blackout, la página se retira; no dejar enlaces rotos.

## Orden de ejecución

1. `seat_model.py`: swing, normalización y D'Hondt.
2. `backtest.py`: 2019 y reproducción de 2023.
3. Tests; no seguir si fallan.
4. Generador y JSON versionado.
5. Integración en `gen/build.py` y plantilla.
6. Staging, `validate_site`, `audit_datos`, móvil, purge.
7. Documentar diff y decisión de ventana.

## Criterio de cierre

- Modelo reproducible desde cero.
- Backtest 2019 y reproducción 2023 documentados.
- Nueva foto etiquetada con fecha, ventana y límites.
- Versión anterior conservada.
- Ninguna frase convierte el escenario en pronóstico o probabilidad.

## Si no se puede terminar

No publicar una foto nueva. Mantener la del 5-nov con el aviso actual. Una foto vieja y honesta es mejor que una actual y no reproducible.
