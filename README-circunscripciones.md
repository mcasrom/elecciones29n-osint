# Microsolución: fichas provinciales y calculadora D'Hondt

Esta pieza convierte los resultados oficiales del Congreso en **52 fichas
provinciales** navegables, con histórico 2019/2023, escaño marginal y una
calculadora D'Hondt que funciona en el navegador.

- Índice: <https://elecciones29n.pruebapublica.com/circunscripciones.html>
- Ficha tipo: <https://elecciones29n.pruebapublica.com/circunscripcion/madrid.html>
- Dato bruto: <https://elecciones29n.pruebapublica.com/data/congreso-oficial.json>

## Qué resuelve

Antes, `/territorio.html` daba los escaños por provincia y los votos↔escaños de
2023, pero no permitía responder preguntas concretas por circunscripción:

- ¿Cuántos diputados reparte mi provincia en 2026 y cuántos electores hay por escaño?
- ¿Cómo quedaron los votos y los escaños en 2023 y en 2019, con las etiquetas oficiales?
- ¿Qué candidatura se quedó en el último escaño y cuánto le faltó a la siguiente?
- ¿Qué pasa si cambio los votos o los escaños? ¿Cómo se reparten con D'Hondt?

Las fichas responden a eso sin mezclar sondeos ni inventar un escenario.

## Qué publica

Cada `/circunscripcion/<slug>.html` incluye:

- escaños y electores de 2026, y electores por escaño;
- participación, votos válidos, nulos, blancos y CERA de 2023 y 2019;
- resultados por candidatura, con **etiqueta oficial** y acrónimo;
- **escaño marginal**: último escaño, primera candidatura fuera, cociente y
  votos aproximados que necesitaría con el resto constante;
- **calculadora D'Hondt**: carga los votos de 2023 o 2019, permite editar votos,
  añadir candidaturas y fijar escaños y blancos;
- navegación anterior/siguiente y enlace a los límites del sitio.

El índice `/circunscripciones.html` ordena las 52 provincias y enlaza cada ficha.

Acceso: enlace **Circunscripciones** en la nav principal y pestaña/CTA en la
portada (`/territorio.html` mantiene su enlace a las fichas).

## Datos y fuente

Fuente primaria: **Ministerio del Interior · Infoelectoral, Datos Abiertos**.

```
https://descargas.interior.gob.es/datasets/resultados_electorales/Elecciones-Congreso.xlsx
```

- Licencia: **CC BY 4.0**.
- Copia de trabajo: `data/raw/elecciones-congreso.xlsx`.
- SHA-256: `dba3394f1812f338067231bce68acf56af1e13ddf8cfb709a814bcc46357ebc2`.
- La descarga oficial y la copia local coinciden byte a byte (1.151.199 bytes).
- Solo se publican `2019-11-10` y `2023-07-23`.

`ingest/congreso_oficial.py` lee el XLSX y escribe
`data/congreso-oficial.json`. No usa `ingest/congreso.py` para las fichas:
esa capa agrupa coaliciones por familias y convertiría coaliciones de 2019 en
`SUMAR`, lo que falsearía la comparación histórica.

### Dos trampas del XLSX

1. **Etiquetas repetidas**: algunas etiquetas aparecen en varias filas con
   provincias disjuntas (`FRENTE OBRERO - FO`, `CAMINANDO JUNTOS - CJ`,
   `PARTIDO COMUNISTA DE LOS TRABAJADORES DE ESPAÑA - PCTE`). El ingestor
   **acumula por provincia**; sobrescribir por etiqueta perdía filas.
2. **CERA**: los votos publicados ya incluyen CERA. Las filas
   `Votos CERA (etiqueta)` son un **subconjunto** y no se suman aparte. Además,
   hay una etiqueta `Votos (TERCERA EDAD EN ACCIÓN - 3e)` que contiene “CERA”
   pero no es CERA: se parsea solo el prefijo exacto `Votos CERA (`.

## Cómo se calcula

`agg/dhondt.py` implementa el reparto con `Fraction` para evitar errores de
redondeo:

- umbral: **3 % de los votos válidos** de la circunscripción;
- cociente: `votos / (escaños ya obtenidos + 1)`;
- desempate: más votos y, después, etiqueta;
- Ceuta y Melilla: con un escaño, gana la lista más votada que supere el umbral;
- blancos: se usan en el denominador del umbral, no compiten por escaños.

El **escaño marginal** se calcula por diferencia de cocientes del último escaño.
No es una previsión de transferencia de votos: es un escenario mecánico con el
resto de votos constante.

## Validación

La construcción falla si algo no cuadra; no publica una ficha a medias:

- 52 provincias y 350 escaños en cada elección;
- D'Hondt reproduce **52/52 provincias** en 2019 y 2023;
- suma de candidaturas + blancos = votos válidos en cada provincia;
- etiquetas oficiales conservadas y sin `SUMAR` en 2019;
- cifras de control: Madrid 37, Barcelona 32, Teruel 3; nacionales 2023:
  PP 137, PSOE 121, VOX 33, SUMAR 31.

Comprobaciones:

```bash
bash scripts/check.sh
```

El validador de publicación exige `/circunscripciones.html`, las 52 fichas y
`data/congreso-oficial.json`; el canario en vivo comprueba el índice y Madrid.
La auditoría de datos verifica el JSON oficial y los totales.

## Uso

```bash
# 1. Reingesta oficial (si cambia el XLSX)
.venv/bin/python -m ingest.congreso_oficial

# 2. Build completo en staging
bash scripts/run_daily_server.sh

# 3. Comprobaciones
bash scripts/check.sh
```

El build diario solo reingiere el XLSX si falta o si el fichero es más nuevo que
`data/congreso-oficial.json`.

## Límites

- **No es una previsión**: la calculadora usa votos que introduces tú y escaños
  2026; no incorpora encuestas, pactos ni transferencia de votos.
- **No hay proyección provincial desde sondeos**: no se reparten encuestas
  nacionales entre provincias.
- **Etiquetas**: se conservan las del Interior; una misma familia puede aparecer
  con varias etiquetas territoriales (PSOE, PSC, PSE-EE, PSdeG, etc.).
- **CERA**: está incluida en los votos; no se publica como un extra sumable.
- **Fuente**: la URL oficial existe, pero su cadena TLS puede requerir el
  intermedio de FNMT. Si se descarga con `curl -k`, hay que verificar el SHA-256
  antes de reemplazar el archivo.
- **Actualización**: si el Interior publica una nueva versión del XLSX, el SHA
  cambiará; hay que revisar el diff y actualizar la documentación antes de
  publicar.

## Archivos

| Fichero | Papel |
|---|---|
| `ingest/congreso_oficial.py` | XLSX oficial → `data/congreso-oficial.json` |
| `agg/dhondt.py` | reparto y escaño marginal |
| `gen/circunscripciones.py` | slugs, páginas, marginales y payload de la calculadora |
| `gen/templates/circunscripcion.html.j2` | ficha provincial |
| `gen/templates/circunscripciones.html.j2` | índice de las 52 fichas |
| `gen/build.py` | integración en build, sitemap y datos |
| `tests/test_congreso_oficial.py` | D'Hondt y totales oficiales |
| `tests/test_marginal.py` | reparto, umbral y marginal |
| `tests/test_circunscripciones.py` | 52 páginas, slugs y enlaces |
| `docs/DATOS-PROVINCIALES.md` | procedencia, SHA, CERA y etiquetas duplicadas |

## Estado

Desplegado el **22-oct-2026**, visible desde la nav y la portada. `check.sh`:
87 tests, validación y auditoría sin fallos. Las 52 fichas responden 200 en
producción.
