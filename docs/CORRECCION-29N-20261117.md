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
- 2 discrepancias de valor entre compiladores: Sociométrica (4,4 vs 5,9) y GAD3 (7,5 vs 6,9). En Sociométrica, el titular de El Español apunta a 5 escaños y respalda el 4,4 % de Electomanía; Onda Cero publica 5,9 %. En GAD3 sigue la discrepancia 7,5/6,9 y ABC no es accesible desde el servidor. Se conserva Electomanía y no se agrega.
- 0/15 publican muestra en la fuente usada.
- La media anterior no se republica con la etiqueta corregida: primero se resuelven discrepancias.

## Qué no se toca

- Resultados oficiales de 2023: siguen diciendo Sumar.
- `pre_registro.json`: métricas y reglas congeladas.
- No se modifica el histórico para “hacerlo coincidir” con la etiqueta actual.

## Trackings del 16-N

`data/auditoria_trackings_20261117.csv`: 3 trackings (40dB, Sigma Dos tracking y SW Demoscopia). Usan **Frente Amplio** y quedan **fuera de la media**, solo como contexto de evolución. La media sigue en 15 sondeos; el último sondeo incorporado es el 15-N.

## Serie histórica

`data/series_breaks.json`: la etiqueta **Sumar** no se reutiliza como **Frente Amplio** para toda la serie. La comparabilidad no está acreditada antes del cambio de denominación; por eso no se publica una línea larga de Frente Amplio ni se reescribe el histórico.

## Decisión sobre el agregado

**No vuelve el agregado de Frente Amplio** mientras GAD3 no se resuelva con la fuente primaria. La serie actual queda en observaciones individuales auditadas. Esta decisión no cambia el pre-registro ni la foto congelada.

## GAD3

GAD3 queda **excluida de una futura media de Frente Amplio** mientras no se resuelva la discrepancia **7,5 % / 6,9 %** con fuente primaria. Se mantiene como observación individual auditada. El agregado actual sigue retirado.
