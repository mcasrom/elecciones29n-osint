# Fuentes

## Primaria (automática)

- **Electomania · ElectoPanel** — WordPress REST API
  (`/wp-json/wp/v2/posts?search=electopanel`), paginada (4 páginas).
  Se extraen porcentajes del texto del panel completo, más `Tamaño muestral`,
  `pollster` y `kind`. Se descartan adelantos parciales, autonómicos y
  regionales. `ElectoPromedio` (media de medias) se marca `kind=average` y se
  excluye de la media principal.

## Secundaria (compilación)

- **Onda Cero · Encuestas 29N** — `https://www.ondacero.es/elecciones/generales/encuestas/`.
  sondeos de 14 casas (sep-2025 → oct-2026). Se usan los **sondeos
  individuales**, no su promedio. La fecha es de **publicación**, no de campo.
  Robots permite la ruta; se cita la compilación y la encuestadora/medio.
  «Otros» es un residual: se guarda para la suma, pero no se usa en gráficos.

## CIS (manual)

- **CIS · barómetros** — `https://www.cis.es/`. Se añade a mano el último
  barómetro con su **PDF**, `sample` y fecha de publicación. Los de septiembre (campo 1–4 sep, n=4.042) y octubre (n=5.025) ya están en el
  histórico. El de octubre entra en la media de 14 días; el de septiembre queda
  en la serie y en el contraste por casa.

## Contraste (no fuente de la media)

- **Política Sin Ruido** — `https://politicasinruido.com/encuestas`. Usa una
  encuesta por casa y peso igual (4 casas, 45 d), con metadatos de campo y
  muestra. Se usa como **referencia metodológica y contraste**, no como
  agregador. La media propia se calcula con nuestros sondeos individuales.

## Alta manual (cuando no hay API)

Rutina completa: **`docs/RUTINA-SEMANAL.md`**. Objetivo: ≥4 sondeos y ≥2
encuestadoras; 10–15 min/semana. Modo lote:

```bash
python scripts/add_poll.py --date 2026-10-20 --pollster "40dB" --sample 1500 \
  --source-url "https://…" --values "PP=31.8,PSOE=27.1,VOX=18.9,SUMAR=5.4"
```

```bash
python3 scripts/add_poll.py --party PP --value 31.8 --date 2026-10-18 \
  --pollster "40dB" --sample 1500 --source-url "https://…"
```

Valida rango y muestra, y avisa si la suma de la fecha queda fuera de 90–110 %.

Candidatas a alta manual (publican en prensa, no API estable):
CIS, 40dB, GAD3, Sigma Dos, Simple Lógica, SocioMétrica, NC Report, DYM,
Celeste-Tel, Hamalgama, KeyData, Ipsos, YouGov.

## Segunda fuente automática — sonda (18-oct)

**Wikipedia EN: `Opinion polling for the 2026 Spanish general election`.**
- HTTP 200, ~5 MB, 25 tablas. La tabla nacional existe.
- Cabeceras con `data-mw='{"caption":"PP"}'` → el orden de partidos es parseable.
- Los valores llegan concatenados con escaños (p. ej. `32.6141` = 32,6 % + 141)
  y las fechas vienen sin año (`10–11 Oct`).
- El HTML es *Parsoid* (`data-mw`, JSON embebido); el parser de tablas normal
  devuelve 2 filas y el texto útil está en los atributos.

**Decisión: NO integrar aún.** Es viable pero frágil (año inferido, valores
pegados a escaños) y una fuente terciaria. Se usa solo como **contraste manual**
(p. ej. SocioMétrica/El Español 10–11 oct: PP 32,6 · PSOE 26,2 · VOX 18,8).
Requisito para integrarla: parser con test que compare 5 filas contra los
titulares publicados y resuelva el año sin ambigüedad.

## Regla

Medir antes de implementar. Una fuente nueva entra con test de contraste y
`kind`/`pollster` declarados; si no pasa, no entra en la media.
