# Registro de fuentes de sondeos

> Para la fase de diseño/desarrollo: aquí se registra **dónde buscar**, no los
> datos. Las encuestas se introducen después en `data/entrada_sondeos.csv`.

## Cómo funciona

1. **Explorar**: revisar las fuentes del registro (`data/fuentes_sondeos.csv`).
2. **Registrar la fuente**: si aparece una nueva, añadir una fila con
   `encuestadora, medio, url, frecuencia, estado, notas`.
3. **Introducir el sondeo**: cuando se publique uno, copiar fecha, muestra,
   enlace y porcentajes en `data/entrada_sondeos.csv`.
4. **Importar**: `.venv/bin/python scripts/import_polls.py`.

El registro no se publica en la web: es una herramienta de trabajo.

## Estados

- `automatico`: ya lo ingiere el pipeline (Electomania).
- `manual`: se busca y se introduce a mano.
- `pendiente`: fuente identificada, aún sin explorar/validar.
- `descartado`: no se usa (sin serie actual, muro de pago, formato no fiable).

## Cómo localizar un sondeo

- **CIS**: barómetros mensuales; PDFs con tabla por partido.
- **40dB / GAD3 / Sigma Dos / SocioMétrica**: publican en prensa; la noticia
  suele incluir la tabla o el titular con los porcentajes.
- **Simple Lógica / NC Report / Celeste-Tel**: prensa; a veces solo titulares
  parciales → si faltan partidos, no se introduce (la suma avisará).
- **Buscadores**: `site:elpais.com 40dB encuesta`, `site:elmundo.es Sigma Dos`,
  `site:abc.es GAD3`. Últimos 7 días.

## Qué registrar y qué no

- **Sí**: encuestadora, medio, URL base, frecuencia y estado.
- **No**: porcentajes sueltos sin enlace, ni medias de otras casas
  (`kind=average` se marca aparte).
- Si un sondeo no se puede verificar, se deja en `pendiente`, no se publica.

## Relación con la rutina

La rutina semanal (`docs/RUTINA-SEMANAL.md`) usa este registro como punto de
partida. Objetivo: **≥4 sondeos y ≥2 encuestadoras** en la media.
