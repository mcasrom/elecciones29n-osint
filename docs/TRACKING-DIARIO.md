# Tracking diario 29N · 13–27 nov 2026

**Regla:** verificar cada día, importar solo fuentes completas y no publicar estimaciones durante el blackout (24–28 nov).  
**Corte actual de la media:** 9-nov. Las encuestas de hoy **no están importadas**.

## Fuentes a revisar cada mañana

- **40dB** (tracking diario; El País/AS).
- **Sigma Dos** (tracking diario; El Mundo).
- **SW Demoscopia** (tracking diario; Demócrata).
- **GAD3** (ABC; barómetro y provincial cuando publique).
- **Electomanía / Onda Cero** (compilaciones).
- **CIS** (solo cuando publique; no diario).

## Checklist diario

1. ¿Hay sondeo nuevo? Fecha de publicación y **fecha de campo**.
2. Casa, fuente, muestra y método.
3. Partidos y porcentajes; suma 90–110 %.
4. ¿Es tracking diario o media de casa? No mezclar `tracking` con `average`.
5. ¿Duplicado de una fila ya existente? No reimportar.
6. Añadir a `polls_history.csv` con URL y `sample` si consta.
7. Recalcular media; comprobar que no cambia scoring/bandas.
8. Anotar en la tabla de abajo.
9. **24–28 nov:** verificar internamente, no publicar estimaciones.

## Calendario

| Fecha | Día | Fuentes | Nuevo | Estado |
|---|---|---|---|---|
| 13-nov | 1 | 40dB, Sigma Dos, SW, GAD3 | Sí, trackings | Pendiente de verificar e importar |
| 14-nov | 2 | 40dB, Sigma Dos, SW | — | — |
| 15-nov | 3 | 40dB, Sigma Dos, SW | — | — |
| 16-nov | 4 | 40dB, Sigma Dos, SW | — | — |
| 17-nov | 5 | 40dB, Sigma Dos, SW | — | — |
| 18-nov | 6 | 40dB, Sigma Dos, SW | — | — |
| 19-nov | 7 | 40dB, Sigma Dos, SW | — | — |
| 20-nov | 8 | 40dB, Sigma Dos, SW | — | — |
| 21-nov | 9 | 40dB, Sigma Dos, SW | — | — |
| 22-nov | 10 | 40dB, Sigma Dos, SW | — | — |
| 23-nov | 11 | 40dB, Sigma Dos, SW | — | — |
| 24-nov | 12 | blackout | No publicar | Solo verificación interna |
| 25-nov | 13 | blackout | No publicar | Solo verificación interna |
| 26-nov | 14 | blackout | No publicar | Solo verificación interna |
| 27-nov | 15 | blackout | No publicar | Solo verificación interna |
| 28-nov | — | blackout | No publicar | Cierre |
| 29-nov | — | jornada | Resultado | No tracking |

## Decisión

No importar automáticamente los trackings de hoy: primero verificar ficha, campo, muestra y URL. La media actual sigue con **15 sondeos / 10 casas** (último incorporado, 9-N).

## 40dB del 13-N (tracking)

- **Fuente primaria:** [El País, 14-nov-2026](https://elpais.com/espana/elecciones-generales/2026-11-14/la-diferencia-entre-pp-y-psoe-se-estrecha-segun-el-tracking-diario-de-40db.html), campo **10–13 nov**, **1.500** entrevistas, CAWI, error ±2,2 %.
- **Estimación publicada:** PP **31,1 %**, PSOE **29,8 %**, Vox **18,5 %**, Frente Amplio **5,2 %**, SALF **1,6 %**, Podemos **1,3 %**.
- **No importado todavía:** es un *tracking* con días solapados con el 40dB del 12-N; la cola de revisión contiene valores contradictorios (`31,5/29,4` del 12-N y `28,4/31,5`, que no cuadra). No se mezclan.
- El ZIP de El País incluye **microdatos individuales**; no se usan para la media ni se copian. Solo se usa la tabla agregada y la ficha.
- Decisión: **no entra en la media** hasta resolver duplicados y tener la tabla completa; no se toca el escenario.

## Automatización preparada

- Script: `scripts/watch_tracking.py`.
- Cron de campaña: **0 6 13-27 nov** (07:00 CET), con `flock` y log en `logs/tracking_watch.log`.
- Consulta 40dB, Sigma Dos, SW Demoscopia, GAD3, CIS y GAD3 provincial.
- **No importa nada**: avisa por Telegram y conserva estado para no repetir.
- Revisa también enlaces de microdatos/`.zip` del CIS 3584; hoy no hay.
- Primera ejecución con `--seed`: 100 artículos vistos; siguiente alerta solo con novedad.
- `--test` enviado correctamente al dueño.
- Para inspección manual: `python3 scripts/watch_tracking.py --dry`.
