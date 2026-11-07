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

## Autorizaciones

- **Electomanía**: autorización escrita del **23-oct-2026** para usar los
  datos en abierto del ElectoPanel (voto y escaños), histórico incluido, con
  atribución y enlace a cada pieza. No se reproducen tablas, gráficos ni
  microdatos.
- **Ateneo del Dato**: autorización escrita del **4-nov-2026** para usar
  todos los datos publicados en abierto, con atribución y enlace. La fuente
  sigue en **revisión manual**: la autorización no la convierte en ingesta
  automática ni permite publicar tablas parciales. El correo se conserva en
  archivo privado y no se publica.

## Qué registrar y qué no

- **Sí**: encuestadora, medio, URL base, frecuencia y estado.
- **No**: porcentajes sueltos sin enlace, ni medias de otras casas
  (`kind=average` se marca aparte).
- Si un sondeo no se puede verificar, se deja en `pendiente`, no se publica.

## Relación con la rutina

La rutina semanal (`docs/RUTINA-SEMANAL.md`) usa este registro como punto de
partida. Objetivo: **≥4 sondeos y ≥2 encuestadoras** en la media.


## Mastodon: descubrimiento, no fuente

- `@electomania@masto.ai` se usa solo para **descubrir** piezas y enlaces.
- `@electografica@social.politicaconciencia.org` está **inactiva desde 2023**; no se usa para el 29N.
- El post de Mastodon **no es el dato canónico**: hay que abrir la pieza enlazada, verificar fecha, casa, muestra y tabla completa.
- `scripts/watch_sondeos.py` añade esos hallazgos a `data/candidatos_sondeos.csv` como `pendiente_revision`.
- No se importa automáticamente ningún porcentaje leído de una red social.
- Un tracking puede servir de contexto, pero no se suma como si fuera un sondeo independiente sin declararlo.
- Si la tabla no suma ~100 %, falta un partido o no hay enlace verificable, **no entra en la media**: se queda pendiente.
- No se rellena “Otros” con un residual inventado salvo que la fuente lo publique y se documente.


## Exploración 7-nov-2026: qué hay y qué no se incorpora

- **SW Demoscopia · 5–6 nov · La Séptima/Electomanía:** aparece en el histórico y en
  la cola como `tracking` y sin `sample`. Es una pieza nueva, pero **no entra en la
  media** hasta comprobar la ficha original, la muestra y si es un tracking
  independiente. No basta el artículo-resumen de un tercero.
- **Celeste Tel · 6-nov:** la cola de descubrimiento ya la detecta; falta verificar
  ficha, campo y muestra antes de introducirla. No se añade por titular.
- **Encuestas regionales de Galicia, Andalucía y Comunidad Valenciana (6–7 nov):**
  son material regional; no se meten en la media nacional. Solo entrarían en
  `regional_sondeos.csv` si tienen la tabla y la ficha completas.
- **La Sexta, Antena 3, ABC, Demócrata y similares:** sus páginas de seguimiento
  son **pistas de descubrimiento**, no sondeos independientes. Hay que abrir la
  pieza original y registrar casa, campo, muestra, cliente y tabla completa.
- **Búsqueda viable:** sí, con `site:`/RSS por casa y prensa; no con scraping
  agresivo ni contando titulares parciales. La cola `watch_sondeos.py` ya deja
  candidatos para revisión, pero **no publica**.

## Canal Bluesky específico

- **Hub Electoral | Prueba Pública** · `@electoraldatahub.bsky.social`.
- Uso previsto: mensajes del proceso electoral 29N. No se mezcla con la cuenta
  general; las credenciales viven en la configuración privada y no se documentan.

## Decisión 7-nov-2026: fuentes de descubrimiento

| Fuente | Prueba | Decisión |
|---|---|---|
| Sigma Dos/Demócrata | `democrata.es` 403 al servidor | **Manual/pendiente**; revisar en navegador y no usar sin ficha primaria |
| PolitPro | 200, aplicación JS y `/es/api` | **Contraste/descubrimiento**; no ingesta automática |
| 40dB / El País | 200; informe citado de febrero | **Solo formato/metodología**; no es un sondeo del 29N |
| Wikipedia EN | 200; última edición 7-nov | **Índice de descubrimiento** CC BY-SA; enlazar la fuente original |

Ninguna de estas fuentes se incorpora automáticamente ni altera la media. La cola
`candidatos_sondeos.csv` sigue siendo el punto de entrada para revisión humana.
