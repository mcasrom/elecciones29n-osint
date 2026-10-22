# Participación y resultados provinciales · FUENTE ENCONTRADA (18-oct-2026)

## Estado 22-oct-2026: capa oficial y fichas

Ya existe una capa de datos **con etiquetas oficiales** para 2019 y 2023:

- `ingest/congreso_oficial.py` lee el XLSX y escribe `data/congreso-oficial.json`.
- Solo publica `2019-11-10` y `2023-07-23`; no mezcla coaliciones de 2019 con
  `SUMAR` (el `data/congreso.json` anterior sí lo hacía por `family()`).
- Conserva `etiqueta` y `acronimo` de cada candidatura, votos, escaños y CERA.
- Valida 52 provincias y 350 escaños por elección.
- SHA-256 del XLSX: `dba3394f1812f338067231bce68acf56af1e13ddf8cfb709a814bcc46357ebc2`.
- **Fuente HTTP recomendada**: `https://descargas.interior.gob.es/datasets/resultados_electorales/Elecciones-Congreso.xlsx`
  (Infoelectoral · Datos Abiertos, Ministerio del Interior). Es el mismo fichero
  que `data/raw/elecciones-congreso.xlsx`: mismo tamaño (1.151.199 bytes) y mismo
  SHA-256. Licencia **CC BY 4.0**; última actualización de la distribución:
  **2024-01-01**; `Last-Modified` del servidor: **2026-06-26**.

**CERA (importante)**: las filas `Votos CERA (etiqueta)` son un **subconjunto**
de los votos de cada candidatura; no se suman aparte. Los votos publicados
incluyen CERA. El parseo usa solo el prefijo `Votos CERA (`: hay una etiqueta
`Votos (TERCERA EDAD EN ACCIÓN - 3e)` que contiene “CERA” y **no** es CERA.
En 2019 hay 112 filas CERA y en 2023, 92.

**Etiquetas duplicadas (importante)**: el XLSX repite algunas etiquetas en filas
con provincias distintas (por ejemplo `FRENTE OBRERO - FO`, `CAMINANDO JUNTOS
- CJ` o `PARTIDO COMUNISTA DE LOS TRABAJADORES DE ESPAÑA - PCTE`). El ingestor
**acumula por provincia**; sobrescribir por etiqueta perdía filas y descuadraba
la suma de candidaturas frente a los votos válidos.

**Fichas**: `gen/circunscripciones.py` genera
`/circunscripcion/<slug>.html` y `/circunscripciones.html` con censo/escaños
2026, resultados oficiales 2019/2023, escaño marginal y calculadora D'Hondt
cliente. La calculadora es un escenario, no una previsión.

## Fuente encontrada

`demo/Elecciones-Congreso.xlsx` (facilitado por el dueño; open data del
Ministerio del Interior). Copiado a **`data/raw/elecciones-congreso.xlsx`**;
SHA-256 en `data/congreso.json`.

- 16 elecciones generales (1977–2023), 52 provincias.
- Por provincia: electores, votantes, votos válidos/nulos/blancos, escaños y
  votos/escaños por partido (familias).
- **Validación**: 2023 participación 66,59 %; 350 escaños; PP 137, PSOE 121,
  VOX 33, SUMAR 31; Madrid 37. Gallagher 5,62.
- **Aviso**: los votos incluyen CERA (PP 8.160.837 aquí vs 8.091.840 en tablas
  que excluyen el voto exterior). Los escaños y la participación coinciden.
- La capa oficial (`congreso-oficial.json`) conserva etiquetas; `congreso.json`
  sigue siendo la serie por familias y **no** debe usarse para fichas.

## Objetivo

Desbloquear dos módulos:

- **M5 Meteorología × participación**: requiere participación por provincia.
- **Votos↔escaños provinciales 2023**: requiere votos y escaños por provincia.

## Intentos previos (bloqueados)

| Fuente | Resultado |
|---|---|
| `infoelectoral.interior.gob.es` | timeout (portátil y servidor) |
| `interior.gob.es` | 403 Cloudflare |
| `resultados.elecciones.gob.es` | sin respuesta (000) |
| `elecciones.mir.es` | timeout |
| JEC | 200, pero solo enlaza al Interior; PDFs de CERA y Ceuta/Melilla, no provinciales |
| `resultados.elpais.com` | 403 |
| datos.gob.es (API) | sin dataset nacional de participación provincial |
| Wikipedia (página 2023 y anexo) | sin tabla de participación por provincia |
| Wayback Machine (CDX MIR) | sin resultados |

## Conclusión

La fuente oficial **sí existe y está disponible por HTTP**: el XLSX de
resultados del Interior con datos provinciales, publicado en Infoelectoral
(Datos Abiertos) y enlazado arriba. El archivo descargado coincide byte a byte
con el conservado en `data/raw/` (mismo SHA-256), así que la capa oficial se
puede reconstruir sin depender de una copia manual.

**Recomendación de uso**: descargar el XLSX desde la URL oficial, comprobar el
SHA-256 y ejecutar `python -m ingest.congreso_oficial`. Si se automatiza, fijar
el SHA esperado y fallar de forma visible si cambia; no sustituir el archivo a
ciegas.

**Aviso TLS**: desde este servidor, `curl` no valida la cadena de
`descargas.interior.gob.es` porque el servidor no envía el intermedio de FNMT.
El navegador sí resuelve la cadena. Para una verificación puntual se puede usar
`curl -k` **solo** si se comprueba después el SHA-256; para producción, instalar
el intermedio de FNMT o descargar desde un navegador. No se debe usar `-k` sin
verificación de integridad.

## Alternativas

1. **Navegador del dueño**: la web oficial puede abrirse manualmente; exportar
   o copiar tablas a un CSV y validarlas (mismo patrón que la noche electoral).
2. **Archivo del Interior** en otro dominio/espejo oficial, si aparece.
3. **JEC**: comprobar si publica actas/resultados provinciales en PDF tras la
   jornada.
4. **Curación manual** de PDFs oficiales: costosa (52 provincias × elecciones),
   pero viable para una sola elección (2023) y para el 29N.

## Qué desbloquea

- Con participación provincial (una o varias elecciones) → estudio de
  meteorología con AEMET.
- Con votos/escaños provinciales 2019 y 2023 → fichas, escaño marginal y
  comparación voto↔escaño.
- **Límite**: la URL oficial existe, pero su cadena TLS está incompleta desde
  este servidor y el fichero puede cambiar cuando el Interior publique una
  nueva actualización. Por eso se conserva una copia con SHA y la reingesta
  automática debe verificar el hash antes de reemplazar el archivo.
- **Licencia**: CC BY 4.0 (metadatos de Infoelectoral); citar Ministerio del
  Interior / Infoelectoral.
