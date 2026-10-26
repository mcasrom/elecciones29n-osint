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

- `automatico`: ya lo ingiere el pipeline (Electomanía y Onda Cero).
- `manual`: se busca, se verifica la tabla completa y se introduce a mano.
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

## Automático y cola de prensa

- **Electomanía** y **Onda Cero** son las fuentes estructuradas: `ingest.electomania` y `ingest.ondacero`.
- `scripts/refresh_polls.sh` corre a las **14:00 y 20:00**, y solo publica si cambió `polls_history.csv`.
- `scripts/watch_sondeos.py` detecta titulares de El Mundo, El Español, La Razón y elDiario y los deja en `data/candidatos_sondeos.csv` con estado `pendiente_revision`.
- La cola **no publica**: hay que abrir la pieza, comprobar fecha de publicación/campo, muestra y tabla completa, y usar `data/entrada_sondeos.csv` o `scripts/add_poll.py`.
- Si solo hay PP/PSOE/Vox, **no se inventa el resto**: se deja pendiente o se agrega el residual en `Otros` y se documenta.

## Qué registrar y qué no

- **Sí**: encuestadora, medio, URL base, frecuencia y estado.
- **No**: porcentajes sueltos sin enlace, ni medias de otras casas
  (`kind=average` se marca aparte).
- Si un sondeo no se puede verificar, se deja en `pendiente`, no se publica.

## Relación con la rutina

La rutina semanal (`docs/RUTINA-SEMANAL.md`) usa este registro como punto de
partida. Objetivo: **≥4 sondeos y ≥2 encuestadoras** en la media.
