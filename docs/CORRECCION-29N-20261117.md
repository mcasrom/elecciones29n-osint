# Corrección 29N · 17-nov-2026

## Motivo

`SUMAR` era una clave interna y también aparecía como etiqueta visible en la media de 2026.
No es aceptable: en el 29N la candidatura es **Frente Amplio**; **Sumar** es el resultado
histórico de 2023 y una de las formaciones de la coalición.

## Decisión

- **No se publica agregado de Frente Amplio** hasta cerrar la auditoría.
- Se muestran observaciones individuales con casa, fecha, etiqueta original y fuente.
- Se conserva la serie histórica de 2023 como **Sumar**.
- Se conserva la foto y el pre-registro; esta corrección no reescribe el pasado.

## Auditoría

`data/auditoria_sondeos_20261117.csv`: 15 sondeos de la ventana de 14 días.

- 15/15 usan **Frente Amplio** como etiqueta original.
- 2 discrepancias de valor entre compiladores: Sociométrica (4,4 vs 5,9) y GAD3 (7,5 vs 6,9). Se conserva la pieza de Electomanía y se documenta la alternativa de Onda Cero; no se agrega.
- 0/15 publican muestra en la fuente usada.
- La media anterior no se republica con la etiqueta corregida: primero se resuelven discrepancias.

## Qué no se toca

- Resultados oficiales de 2023: siguen diciendo Sumar.
- `pre_registro.json`: métricas y reglas congeladas.
- No se modifica el histórico para “hacerlo coincidir” con la etiqueta actual.
