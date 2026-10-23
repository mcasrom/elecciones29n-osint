# Métricas y bases (auditoría)

> Regla: **ninguna cifra derivada se calcula en una plantilla ni con una
> expresión ad hoc**. Cada métrica vive en **`metrics.py`** y se consume en el
> build, el validador y los tests. Un delta compara **la misma base**.

## Catálogo

| Métrica | Definición | Base |
|---|---|---|
| Media por sondeo | media de los sondeos de la ventana de 14 d | recencia (vida media 10 d) + √n si la fuente declara muestra |
| Media por casa | última encuesta de cada casa en 45 d, peso igual | una por casa; incluye CIS |
| Media móvil (MA) | media de los sondeos en ±7 d (14 d centrada) | por partido; línea de los gráficos |
| Delta de la tarjeta | **MA final − MA inicial** | nunca último sondeo vs primer sondeo de otra casa |
| `n_polls` | nº de sondeos (fecha + casa) | no nº de fechas |
| «Otros» | resto de partidos | residual; fuera de KPIs/gráficos/simulación |
| Hemiciclo | 350 escaños por D'Hondt nacional sobre la media de cada fecha | solo partidos estatales, umbral 3%; una entrada por sondeo + hoy; nunca proyección |
| M4 | voto declarado 2023 por grupo | N ponderado; celdas n<30 suprimidas |
| M5 | asociación meteorología-participación | observacional; sin causalidad |

## Incidente que motivó la auditoría (18-oct-2026)

La tarjeta «Variación de los sondeos» mostraba:
- **Cifra grande**: el **último sondeo** (CIS octubre: PP 22,2 / PSOE 34,0).
- **Delta**: ese sondeo **menos el primero del periodo** (DYM 23-jul, otra casa):
  PP −12,7 / PSOE +7,0.
- **Periodo**: 30-ago–14-oct, aunque el primer punto era 23-jul.

Era **real** pero **no era una variación de tendencia**: mezclaba casas y fechas.
Se sustituyó por MA 14 d: PP 31,1 / PSOE 27,2; delta MA −2,7 / +0,7; periodo
real 23-jul–14-oct. El CIS sigue visible como punto aislado.

## Controles

1. **`metrics.py`**: fuente única de `moving_average`, `spark_summary`,
   `series_span`.
2. **Tests** (`tests/test_metrics.py`): MA suaviza un outlier; la tarjeta usa
   la MA, no el último sondeo; el span es el real.
3. **Validador**: recalcula la MA de PP/PSOE desde `latest.json`, la compara con
   la cifra renderizada y comprueba que el periodo real está en la página.
4. **Canario**: exige la etiqueta «media móvil de 14 días».
5. **Etiqueta visible**: «cifra grande = MA; delta = cambio de la MA; puntos =
   sondeos individuales».

## Reglas

- Un delta solo es válido si ambos extremos están en la **misma base**.
- Un **último sondeo** no es una tendencia; si se muestra, se etiqueta.
- Un **outlier** se muestra, no se oculta, pero no define la línea.
- Si una métrica nueva no tiene definición, test y validación, **no se publica**.
