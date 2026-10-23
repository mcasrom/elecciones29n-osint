# Auditoría de datos (18-oct-2026)

> **Resultado: 233 comprobaciones offline · 0 fallos críticos** (más 12 online con `--online`).
> Reproducible: `python scripts/audit_datos.py --online`.

## Qué se verifica

**Sondeos**
- Esquema y valores (0–100), fechas sin futuro, duplicados (partido, fecha, casa).
- **Suma por sondeo 90–110**; todos los sondeos pasan.
- `latest.json` recalculado con `agg.aggregate`: `n_polls`, encuestadoras, media/min/max/mediana/n, salud, media por casa, span y MA.
- La media está dentro del rango; `n_polls` = sondeos (fecha + casa), no fechas.
- MA 14 d y periodo real; etiquetas de UI.

**Censo**
- Total **38.728.356**; CER **35.958.711**; CERA **2.769.645**; CER+CERA.
- 52 provincias y 19 CCAA; sumas de provincia/CCAA/edad/sexo.
- Nuevos electores **1.615.127**; SHA-256 de los XLSX.

**Participación**
- 15 elecciones; **2023 66,59 %**; máximo **79,97** (1982); mínimo **66,23** (2019-N).
- Provincial: **16 × 52**, sumas de electores/votantes = nacional; 2023 = 66,59.
- Cruce con el XLSX del Interior (misma fuente de Congreso).

**Territorio**
- **350 escaños**, 52 circunscripciones, suma 350.
- Madrid 38, Barcelona 32, Teruel 3, Soria 2, Ceuta/Melilla 1.
- Electores por provincia = censo total.
- 2023: PP **137**, PSOE **121**, VOX **33**, SUMAR **31**; Gallagher **5,62**.

**M4 (CIS 3582)**
- Muestra **5.025**; 7 grupos de edad, 2 de sexo, 3 de ideología.
- **n<30 suprimido**; `suppressed == (n<30)`.
- Anclas: mujeres PSOE **49,1**, hombres PSOE **37,6**.
- Etiquetas: voto declarado, N ponderado, n<30.

**M5 (AEMET)**
- 16 fechas; 2023 con 52 provincias; cobertura menor en 1979/1982.
- n=**806**; 4 bins; coeficiente de precipitación con IC coherente; robustez 2004.
- Etiquetas: resultados, anexo meteorológico, no causalidad.

**Fuentes online**
- **Onda Cero**: se compara el histórico con los 95 sondeos de la página (valores/fechas/casas).
- **CIS 3582**: PDF de estimación contrastado con el histórico (PP 22,2, PSOE 34,0, VOX 17,1, SUMAR 6,1…).
- **Electomania**: panel del 11-oct contrastado con la API.
- Las comprobaciones online son **avisos** (la fuente puede cambiar); las offline son **críticas**.

## Qué NO se verifica

- El **trabajo de campo** de cada encuesta: se confía en la fuente publicada.
- El **indexado en Google/Bing**: no hay API de GSC configurada; se revisa a mano.
- Las **cifras derivadas de la fuente** (p. ej. estimación de voto del CIS): se contrastan con el PDF, no se recalculan.
- El **futuro**: el 29N no se predice.

## Ambigüedad: controles

- **`metrics.py`** es la fuente única de MA, resumen y span.
- Un **delta compara la misma base**; nunca último sondeo vs primero de otra casa.
- El **rango no es un IC**; la **suma de entrevistados no es una muestra única**; **«Otros»** es residual (en Onda Cero incluye ERC/Junts/Bildu/PNV, que van en tabla aparte y no se suman); **n ponderado**; **celdas n<30 suprimidas**.
- La ventana es de **14 días naturales** contando hoy; la auditoría exige **90–110** en la suma de cada sondeo tracking y comprueba que la **suma de la tabla principal** no duplique territoriales.
- **Tests + validador** fijan las etiquetas y recalculan MA/periodo.
- Regla 37 en `AGENTS.md`.

## Reproducir

```bash
python scripts/audit_datos.py            # offline (crítico)
python scripts/audit_datos.py --online   # + Onda Cero/CIS/Electomania
```

Salida: `data/audit_report.json` (no versionado) y resumen por consola.
