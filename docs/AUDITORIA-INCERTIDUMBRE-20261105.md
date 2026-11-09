# Auditoría de incertidumbre y Monte Carlo — 29N

**Fecha de ejecución:** 9-nov-2026  
**Sprint:** `docs/SPRINT-MEJORA-ESCENARIOS-20261105.md` · **E0**  
**Alcance:** auditar los datos de entrada y el escenario; no cambiar el modelo.

## Conclusión

El pipeline de la media está limpio: los `average` están excluidos, no hay duplicados exactos y la media usa 13 sondeos recientes. El problema está en el **escenario de escaños**: está congelado el 5-nov con 12 sondeos y 8 casas, su código (`seat_model.py`/`backtest.py`) no está en el repositorio actual y no se puede auditar ni recalcular el Monte Carlo. No debe presentarse como una foto actual.

## 1. Universo de datos

| Comprobación | Resultado |
|---|---:|
| Filas de `polls_history.csv` | 959 |
| Rango temporal | 2025-09-01 → 2026-11-09 |
| Filas `tracking` | 933 |
| Filas `average` | 26 |
| Sondeos únicos `tracking` (`date` + `pollster`) | 128 |
| Sondeos únicos `average` | 3 |
| Casas en el histórico | 21 |
| Casas en `tracking` | 20 |

Los tres `average` son de **ElectoPromedio**: 2026-09-30, 2026-10-19 y 2026-11-02. Están excluidos de la media y aparecen en `excluded_averages`.

## 2. Duplicados

- Claves `(date, pollster, party)` duplicadas: **0**.
- `load_polls()` deduplica por `(party, date, pollster)`; no se detectaron colisiones.
- No se observa doble conteo por fila de partido.

## 3. Cobertura de `sample`

| Ámbito | Filas con `sample` | Cobertura |
|---|---:|---:|
| Histórico total | 168 / 959 | **17,5 %** |
| `tracking` | 168 / 933 | **18,0 %** |
| `average` | 0 / 26 | 0 % |
| Media de 14 días | 0 / 13 sondeos | **0 %** |

Casas con `sample`: Ateneo del Dato, CIS, ElectoPanel, NC Report, Sigma Dos y Sociométrica.

Consecuencia: en la ventana actual **no se puede usar `√n`** ni modelar error de muestreo. La ponderación efectiva es solo por recencia, y la incertidumbre debe apoyarse en la dispersión entre sondeos/casas, no en un error de muestreo inventado.

## 4. Universo de la media actual

| Dato | Valor |
|---|---:|
| Sondeos en la media | 13 |
| Casas | 9 |
| Ventana | 2026-11-01 → 2026-11-09 |
| Último sondeo | 2026-11-09 |
| `weights.total_polls` | 13 |
| Casa con más peso | NC Report · 15,3 % |
| Fuente con más peso | Electomanía · 71,3 % |
| Casas efectivas | 8,24 |
| Fuentes efectivas | 1,69 |
| IQR de dispersión | 2,4 pp |
| Candidatos pendientes | 19 |

La media y el escenario **no usan el mismo universo**: 13 sondeos/9 casas (9-nov) frente a 12 sondeos/8 casas (5-nov).

## 5. Trackings excluidos

- `ElectoPanel`: 110 filas; fuera de la media.
- `SW Demoscopia`: 11 filas; fuera de la media.
- Se conservan como contexto de evolución, no como observaciones independientes.

## 6. Escenario de escaños

`data/escenarios.json`:

| Campo | Valor |
|---|---:|
| Corte | 2026-11-05 |
| Sondeos | 12 |
| Casas | 8 |
| Iteraciones | 5.000 |
| Congelado | Sí |

Rangos p10–p90:

| Partido | p10 | p50 | p90 | Amplitud |
|---|---:|---:|---:|---:|
| PP | 132 | 136 | 139 | 7 |
| PSOE | 107 | 110 | 114 | 7 |
| VOX | 65 | 66 | 67 | 2 |
| SUMAR | 8 | 8 | 10 | 2 |

Bloques:

| Bloque | p10 | p50 | p90 | Amplitud |
|---|---:|---:|---:|---:|
| PP + VOX | 198 | 202 | 205 | 7 |
| PSOE + SUMAR | 115 | 118 | 122 | 7 |
| PSOE + SUMAR + territoriales | 144 | 147 | 151 | 7 |

La página muestra el corte del 5-nov y no afirma que sea una foto actual. Aun así, el escenario queda **desfasado** respecto a la media del 9-nov.

## 7. Bloqueo técnico

En el repositorio actual:

- **No existe `seat_model.py`.**
- **No existe `backtest.py`.**
- El Monte Carlo no es reproducible desde el código versionado.
- `data/escenarios.json` es la única fuente del escenario, pero no su generador.

Por tanto, no se puede verificar si:

- `ElectoPromedio` entra o no en el remuestreo del escenario;
- el escenario determinista y el Monte Carlo usan las mismas 12 observaciones;
- el rango p10–p90 incorpora dispersión entre casas o solo ruido de remuestreo;
- el backtest de 2019 se reproduce con los parámetros actuales.

## 8. Lectura honesta

- La media es una **media de sondeos**, no un pronóstico.
- El rango p10–p90 del escenario **no es un intervalo de confianza**.
- El escenario no incorpora error de muestreo porque el 100 % de la ventana actual no declara `n`.
- El backtest de 2019 (MAE 1 escaño, 4 partidos) prueba el mecanismo, no la calidad de los sondeos de 2026.
- No se deben mezclar los 13 sondeos de la media con los 12 del escenario congelado.

## 9. Decisión

**No cambiar el escenario ni publicar una foto nueva** hasta recuperar o reescribir el generador con tests y backtest reproducible.

Antes de E1/E2:

1. Recuperar `seat_model.py`/`backtest.py` o reimplementarlos.
2. Fijar el universo exacto del Monte Carlo.
3. Declarar que no hay error de muestreo en la ventana actual.
4. Comparar rango viejo vs nuevo y no elegir el más estrecho.
5. Mantener visible el corte del 5-nov mientras el escenario no se regenere.

## 10. Estado del sprint

- **E0:** ejecutado; hallazgo bloqueante: falta el código del modelo.
- **E1:** no iniciado.
- **E2:** no iniciado.
- **E3/E4:** no iniciados.
- **E5:** no iniciado.

No se toca scoring, media ni escenario en esta auditoría.
