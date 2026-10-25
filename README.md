# Observatorio electoral 29N

**Sondeos con rango, censo, participación y territorio.** Datos abiertos, método público y ninguna cifra que el dato no sostenga.

[![En vivo](https://img.shields.io/badge/en%20vivo-elecciones29n.pruebapublica.com-ff5a1f)](https://elecciones29n.pruebapublica.com/)
[![Licencia](https://img.shields.io/badge/licencia-AGPL--3.0-3ddc97)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.12-8ec5ff)](https://www.python.org/)
[![Versión](https://img.shields.io/badge/versi%C3%B3n-0.10.6-ff5a1f)](CHANGELOG.md)

---

## Qué es y qué no es

**Es** un observatorio que reúne cuatro capas del proceso electoral:

| Capa | Pregunta | Dato |
|---|---|---|
| Sondeos | ¿Qué dicen las encuestas publicadas? | media móvil + rango mín–máx |
| Censo | ¿Quién puede votar? | INE · Oficina del Censo Electoral |
| Participación | ¿Quién vota y cómo ha cambiado? | JEC, 1979–2023 |
| Territorio | ¿Cómo se traduce el voto en escaños? | BOE · RD 806/2026 + LOREG |

**No es** un pronóstico, ni una estimación propia de intención de voto, ni una
proyección de escaños. El rango no es un intervalo de confianza: es la
dispersión observada entre los sondeos incluidos. La incertidumbre va en el
dato, no en una nota al pie.

## Módulos publicados

- `/` — Agregado, evolución, Congreso (D'Hondt etiquetado como simulación) y Senado.
- `/hemiciclo.html` — **350 escaños por fecha de sondeo**: D'Hondt nacional sobre la media, selector de fecha, bloques y serie completa. Simulación mecánica, no proyección; sin territoriales. Enlace visible en la portada (pestaña **Hemiciclo** y botón bajo los indicadores) y en la navegación del resto de páginas.
- `/en.html` — **resumen mínimo en inglés**: media, rango, límites, método, datos y enlaces. `hreflang` es/en; el resto del sitio sigue en español.
- `/competitivas.html` — **52 provincias por margen oficial 2023** entre los dos primeros, con escaños, diferencia y participación. Contexto factual, no proyección.
- `/mayorias.html` — **calculadora de mayorías** sobre el hemiciclo simulado: suma de escaños, umbral 176 y presets. No predice pactos ni investidura.
- `/postelectoral.html` — **calibración post-electoral**: pendiente hasta el escrutinio; comparará media pre-electoral, resultado oficial, MAE, sesgo y escaños.
- `/embed/medias.html`, `/embed/robustez.html`, `/embed/hemiciclo.html` — **paneles incrustables** con atribución; ejemplos iframe en sus páginas y en `/fuentes.html`.
- `/aviso.html` — **landing de avisos**: un correo solo cuando cambia la media o el hemiciclo; doble opt-in y baja en un clic.
- `/prensa.html` — **kit de prensa**: titular canónico (media ponderada + rango), cifras, método, cita, contacto y enlaces a datos/embeds.
- `/electorado.html` — Censo 29N: total, CER/CERA, edad y sexo, provincias y nuevos electores.
- `/participacion.html` — Participación nacional 1979–2023 y **provincial 1977–2023** (selector + comparación con la media nacional).
- `/territorio.html` — 350 escaños, 52 circunscripciones, electores por escaño y **votos↔escaños 2023 con índice de Gallagher**.
- `/circunscripciones.html` — **52 fichas provinciales** con histórico oficial 2019/2023, escaño marginal y calculadora D'Hondt; acceso desde la **nav principal y la portada**. Detalle técnico en [`README-circunscripciones.md`](README-circunscripciones.md).
- `/factores.html` — Factores y participación: día/festivo, meteorología (M5) y **resultados v1**.
- `/comportamiento.html` — **M4 v1**: voto declarado en 2023 por edad, sexo e ideología (CIS 3582, n=5.025), con n por celda y celdas n<30 suprimidas.
- `/noche-electoral.html` — Qué se publica el 29N, cuándo y con qué fuente.
- `/metodologia.html` y `/fuentes.html` — Método, fuentes, catálogo de datos y licencias.
- `/privacidad.html` — Datos del aviso por correo, finalidad, conservación y derechos. Sin cookies.

## Datos abiertos y reproducibilidad

- `data/latest.json` y `data/robustez.json`: agregado y robustez.
- `data/status.json`: build, commit, fuentes y **hashes SHA-256** de los ficheros publicados.
- `data/changelog.json`: historial de builds/datos (máximo 100 entradas).
- `/data/v1/latest.json`, `/data/v1/robustez.json`, `/data/v1/status.json` y `/data/v1/schema.json`: contrato versionado y esquema.
- `scripts/reproduce.sh`: reconstruye con el CSV y los datos actuales y devuelve los hashes. El cálculo es **determinista** (D’Hondt y ponderación); no usa semilla. Para reproducir un build histórico hay que congelar antes el CSV y los JSON de entrada.
- En **blackout** (24–28 nov), los JSON y OG retirados responden **410**; el service worker no cachea `/data/` ni `.json`.
- `scripts/archive_check.py`: comprueba si hay instantáneas en Archive.org (0 sin capturas, 1 con capturas, 2 consulta incompleta).
- **Sección EN**: `/en.html`, `/en/method.html`, `/en/hemicycle.html`, `/en/robustness.html`, `/en/competitive.html`, `/en/majorities.html`, `/en/limits.html`, `/en/data.html`, `/en/post-election.html`; nav propia y `hreflang` recíproco.

## Parte matinal de campaña

`scripts/campaign_digest.py` publica a las **08:00 (13–23 nov)** solo si hay cambio relevante: nuevo sondeo, cambio de bloque/mayoría, Δ≥1 pp o Δ≥3 escaños. Encola en Mastodon/Bluesky/Telegram y manda al dueño el texto de X; sin cambio, silencio. Detalle y cron en [`docs/CAMPANA-29N.md`](docs/CAMPANA-29N.md).

## Aviso por correo

La web incluye un **aviso de doble opt-in** para saber cuándo cambia la media o
sale un sondeo nuevo. No hay cuentas ni cookies: el alta guarda email, fecha,
página, UTM, **host** del referrer (nunca la URL completa ni la IP) y la
**versión del consentimiento**. Confirmar y darse de baja exige pulsar un botón
(un `GET` no cambia el estado, para que no lo haga un escáner de correo). Los
logs de acceso se conservan 14 días y las copias de la base 30 días. La API vive
en `scripts/subs_api.py` (puerto 3031, PM2 `elecciones29n-api`, SQLite
`data/subs.db`) y el informe agregado sin PII —incluidas las versiones de
consentimiento— se obtiene con `python3 scripts/subs_report.py`.

## Salud de la muestra

La portada muestra un panel de **salud de la muestra**: número de sondeos,
encuestadoras y días desde el último. Es el principal control de calidad del
agregado.

| Estado | Criterio | Qué significa |
|---|---|---|
| **Datos suficientes** | ≥4 sondeos, ≥2 casas, último ≤10 días | media entre encuestadoras |
| **Datos frágiles** | 4 sondeos pero una sola casa, o último >10 días | se publica con aviso |
| **Datos insuficientes** | <4 sondeos o último >21 días | se publica con aviso visible |

> Al 23-oct: **9 sondeos y 7 encuestadoras en la ventana de 14 d** (14 en 45 d), último hace 4 días → **datos suficientes**.
> Se combinan Electomania, la compilación de Onda Cero y el CIS (septiembre y octubre). Ver
> [`docs/RUTINA-SEMANAL.md`](docs/RUTINA-SEMANAL.md).

```bash
.venv/bin/python scripts/health_report.py
```

## Revisión P0 (23-oct-2026)

- **Ventana por fecha natural**, no por hora: 14 días contando hoy (45/90 en sus ventanas). Un sondeo del día 14 ya no entra a las 23:00 y desaparece a las 08:00.
- **Frente Amplio → SUMAR**: el ElectoPanel del 18-oct publica «Frente Amplio … 4,9 %»; se mapea a SUMAR y se backfilla la fila (suma del sondeo 87,3 → 92,2).
- **Sin doble conteo territorial**: ERC, Junts, Bildu y PNV salen de la tabla principal (en Onda Cero ya van dentro de «Otros») y se publican aparte. La tabla muestra su suma: **98,83**.
- **Etiquetas y auditoría**: «Datos suficientes/frágiles/insuficientes», muestra «3/9 con muestra (12.291 encuestados)» y casas a 45/14 d. `audit_datos.py` exige 90–110 en sondeos tracking y comprueba la suma.
- Verificación: **103 tests**, **233 comprobaciones, 0 fallos críticos**; `n_polls=9` (11–19 oct). Versión **0.10.6**.

## Fuentes

| Dato | Fuente | Formato |
|---|---|---|
| Sondeos | [Electomania · ElectoPanel](https://electomania.es/) | WordPress REST API · autorización escrita 23-oct-2026, enlace por pieza y escaños publicados sin recalcular |
| Sondeos (secundaria) | [Onda Cero · Encuestas 29N](https://www.ondacero.es/elecciones/generales/encuestas/) | HTML/JSON |
| Sondeos (manual) | [CIS · barómetros](https://www.cis.es/) | PDF |
| Contraste | [Política Sin Ruido](https://politicasinruido.com/encuestas) | HTML |
| Censo | [INE · CEL](https://www.ine.es/dyngs/CEL/es/index.htm?cid=1703) | XLSX (tablas 2/3/6/9/12) |
| Participación | [JEC](https://www.juntaelectoralcentral.es/) | tablas por elección |
| Escaños | [BOE · RD 806/2026](https://www.boe.es/diario_boe/txt.php?id=BOE-A-2026-20742) | anexo |
| Normativa | [LOREG](https://www.boe.es/buscar/act.php?id=BOE-A-1985-11672) | BOE consolidado |
| Resultados provinciales | [Ministerio del Interior · Infoelectoral](https://descargas.interior.gob.es/datasets/resultados_electorales/Elecciones-Congreso.xlsx) | XLSX (CC BY 4.0) · copia con SHA-256 en `data/raw/elecciones-congreso.xlsx` |

Cada fila de sondeo guarda `pollster`, `date`, `source_url` y `sample`. Los
metadatos del censo incluyen URL y **SHA-256** de cada XLSX.

## Arquitectura

```
ingest/electomania.py ─┐
ingest/censo.py        ├─→ data/ ─→ agg/aggregate.py ─→ gen/build.py ─→ web_tmp/
ingest/participacion.py│              (media, salud)      (HTML, OG, RSS)
ingest/escanos.py      ┘                                      │
                                                              ▼
                                     scripts/validate_site.py  ←  validación
                                                              │
                                     swap atómico (web/ ← web_tmp/)
                                                              │
                                     rsync → servidor nginx (estático)
                                                              │
                                     canary en vivo + IndexNow + purge CF
```

- **Local-first**: ingesta, agregado y build corren en Python; la publicación es
  estática (nginx). El **cron del servidor** (`06:15 UTC`) ejecuta
  `scripts/run_daily_server.sh` (ingesta → build en `web_tmp/` → validación →
  swap atómico → rsync → canario → IndexNow → purge). No hay backend.
- **Fail-safe**: si la ingesta o la validación fallan, **no se publica nada** y
  se conserva la última versión buena (`web_prev/` para revertir).
- **Robustez del dato**: panel con cinco indicadores (sondeos, casas, días desde el
  último, % con muestra declarada y dispersión IQR entre casas), sin nota agregada.
  La tabla muestra además casas e IQR por partido; el contraste por casa incluye el
  último sondeo de cada una con su método (CIS = estimación de voto) y una nota sobre
  mín–máx frente a IQR. Explicación y límites en `/metodologia.html#robustez`. El build diario genera también `og-robustez.png` (1200×630) para RRSS. La robustez separa **fuente** y **casa** (no se suman), muestra concentración efectiva, aviso si una fuente supera el 50 %, sensibilidad al quitar Onda Cero/ElectoPanel/CIS y una ficha de **método/cobertura por casa** con «no consta» cuando la fuente no lo publica.
- **Aviso de novedades**: chip en la cabecera («Nuevo sondeo · <casa> (DD/MM)»)
  que solo aparece si la ejecución ha incorporado sondeos nuevos. Se mantiene
  durante el día y desaparece al siguiente; las medias (`kind=average`) no
  cuentan. Estado en `data/novedades_state.json` (no versionado).
- **Sin terceros**: sin cookies, sin analítica externa, sin publicidad.

## Puesta en marcha

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

bash scripts/check.sh       # compila + tests + validación + auditoría
bash scripts/run_daily.sh   # ingesta + agregado + build + deploy
python3 scripts/needs.py panel --open   # pendientes y avisos
```

### Cron diario (systemd --user)

```bash
mkdir -p ~/.config/systemd/user ~/.local/state/elecciones29n
cp systemd/elecciones29n.service systemd/elecciones29n.timer ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now elecciones29n.timer
systemctl --user list-timers | grep elecciones

# opcional: que corra sin sesión iniciada
sudo loginctl enable-linger $USER
```

El servicio escribe en `~/.local/state/elecciones29n/run.log`. El cron de las
08:00 termina publicando; si el portátil está apagado, la web muestra un aviso
pulsante cuando los datos superan las 26 h o pasa de las 09:00 sin actualizar.

## Alta manual de sondeos

Objetivo: **≥4 sondeos y ≥2 encuestadoras**. Rutina de 10–15 min/semana en
[`docs/RUTINA-SEMANAL.md`](docs/RUTINA-SEMANAL.md).

**Método CSV (recomendado)**: edita `data/entrada_sondeos.csv` (una fila por sondeo)
y ejecuta `python scripts/import_polls.py`.

```
pollster,date,sample,source_url,values
40dB,2026-10-20,1500,https://…,PP=31.8;PSOE=27.1;VOX=18.9;SUMAR=5.4
```

**Método comando**: un sondeo completo en una línea.

```bash
.venv/bin/python scripts/add_poll.py --date 2026-10-20 --pollster "40dB" \
  --sample 1500 --source-url "https://…" \
  --values "PP=31.8;PSOE=27.1;VOX=18.9;SUMAR=5.4;Podemos=3.3;ERC=2.0;Junts=1.2;Bildu=1.3;PNV=1.1;SAF=1.8"
```

Valida partidos, rango y suma (90–110 %). `kind=average` marca promedios de
otras casas y se excluye de la media principal.

## Estructura

```
agg/            agregado, blackout y salud de la muestra
ingest/         Electomania, censo (INE), participación (JEC), escaños (BOE), resultados oficiales (Interior)
gen/            build estático, OG, plantillas Jinja
data/           histórico de sondeos y datasets normalizados (fuente de verdad)
web/            salida estática publicada
scripts/        run_daily, check, validate_site, canary, IndexNow, add_poll, health_report
docs/           método, fuentes, rutina semanal, legal y sprint del observatorio
tests/          94 pruebas (datos, build, validador, fichas provinciales)
systemd/        servicio y timer
```

## Meteorología y participación (M5 v1)

- Panel **provincia × elección** (806 observaciones, 16 elecciones) con participación provincial y AEMET OpenData.
- Modelo con **efectos fijos** de elección y provincia y errores agrupados: precipitación **−0,041 pp/mm** (IC −0,087 a 0,005; p=0,081); en **2004–2023**, −0,041 pp/mm (p=0,007).
- Correlación intra-elección −0,136. El viento sale positivo y **no se interpreta como causal**.
- Resultados y límites en `/factores.html` y `data/m5-results.json`. Método: `docs/M5-METODOLOGIA.md`.

## Contraste por casa

Además de la media por sondeo (ponderada por recencia y muestra cuando existe), la portada muestra el **contraste por casa**: la última encuesta de cada casa en 45 días, con **peso igual por casa**. Sirve para detectar si la media está dominada por una encuestadora. Incluye CIS. No es la media principal.

## Avisos locales

- **`scripts/needs.py`**: fuente de pendientes de 29N (GSC, IRDP, tarjeta social) + chequeos automáticos (cron, datos, salud, inbox); panel `~/.config/elecciones29n/needs.html`.
- El aviso diario lo manda el **centro único** `~/Desktop/atencion` (un solo aviso, 21 servicios + 29N). Detalle: [`docs/AVISOS.md`](docs/AVISOS.md).

## Auditoría de datos

- **`scripts/audit_datos.py`**: **233 comprobaciones offline, 0 fallos críticos** (más 12 online con `--online`). Recalcula medias/MA, sumas, censo, participación, escaños, M4/M5, etiquetas de UI y contrasta Onda Cero/CIS/Electomania.
- `check.sh` la ejecuta en modo offline; informe: [`docs/AUDITORIA-DATOS.md`](docs/AUDITORIA-DATOS.md).
- Límites: no verifica el trabajo de campo de las encuestas ni el indexado de buscadores.

## Métricas y auditoría

- **`metrics.py`** es la fuente única de las métricas derivadas (media móvil 14 d, resumen de tarjeta, periodo de serie).
- Un **delta compara la misma base** (MA vs MA, media vs media); nunca último sondeo vs primero de otra casa.
- **Tests** y **validador** recalculan la MA desde `latest.json` y comparan con la cifra renderizada.
- Incidente y reglas: [`docs/METRICAS.md`](docs/METRICAS.md).

## PWA y actualizaciones

- Instalable: `manifest.webmanifest`, iconos 192/512/maskable y service worker.
- **Network-first** para HTML y `data/*.json`; cache-first para CSS/JS/OG/iconos.
- Aviso **«Nueva versión disponible»** con **Recargar** y **×**. El × se recuerda por
  versión y pestaña; no vuelve a molestar hasta el siguiente deploy.
- Un `[hidden]` global garantiza que ningún componente oculto se muestre por CSS.

## Calidad

- **94 tests** (`unittest`) y hook **pre-push**.
- `scripts/check.sh`: compila, tests, valida el sitio local y ejecuta la auditoría de datos.
- **Validador** de publicación: gráfico con puntos, pestañas, JSON, sitemap, OG,
  RSS, censo, participación y escaños.
- **Canario en vivo** tras cada deploy: comprueba en la URL pública el gráfico,
  el JSON, la OG, el censo, la participación, el territorio y las páginas nuevas.
- **Reversión**: `web_prev/` conserva la versión anterior.

## SEO y datos abiertos

- `sitemap.xml` (69 URLs, incluidas las 52 fichas provinciales), `robots.txt`, `llms.txt` y RSS `cambios.xml`.
- OG 1200×630, `twitter:card`, canonical y JSON-LD (`WebSite`, `Dataset`,
  `FAQPage`, `Person`).
- **IndexNow** en cada build; cache-busting `?v=` en CSS/JS.
- Datos descargables en `/data/`: JSON y CSV de sondeos, censo, participación y
  escaños.

## Límites

- Una media no sustituye a la incertidumbre; el rango no es un intervalo de confianza.
- Una sola encuestadora no es una media entre casas.
- El censo describe quién puede votar, no a quién vota.
- La simulación de Congreso es mecánica (distrito único), no una proyección.
- El Senado no se simula: depende de listas provinciales y designación autonómica.
- La calculadora provincial es un escenario mecánico con votos introducidos a mano. El hemiciclo nacional sí simula escaños desde la media, pero se etiqueta como mecánica de bloques: no es una proyección ni el Congreso real. El Senado no se simula.
- No se atribuyen preferencias por edad, sexo, renta o territorio.
- No se mezclan señales sociales con sondeos, censo o participación.

## Hoja de ruta

- **M4 v1** · Comportamiento por grupos: ✅ hecho (CIS 3582, recuerdo 2023; edad/sexo/ideología; celdas n<30 suprimidas).
- **M5 v1** · Meteorología × participación: ✅ hecho (806 obs; −0,041 pp/mm; sin causalidad).
- **29N** · Activar resultados y participación oficiales tras la jornada (fallback manual listo).
- **Provincial** · ✅ participación 1977–2023 y votos↔escaños 2023 integrados.
- **M5b** (opcional) · placebo con el día anterior, umbrales de lluvia y robustez adicional.
- **IRDP** · revisión del índice sintético (calidad, dispersión y error histórico); **no publicar** hasta contrastar.

## Licencia y cita

Código **AGPL-3.0** ([`LICENSE`](LICENSE)). Datos agregados reutilizables citando
el proyecto.

> Miguel Castillo. *Observatorio electoral 29N*. https://elecciones29n.pruebapublica.com

Contacto: **info.elecciones29n@pruebapublica.com**

## Documentación legal

- `docs/LEGAL-29N.md` — fuentes, blackout, privacidad, licencias y pendientes.
- `docs/ONDA-CERO-AUTORIZACION-BORRADOR.md` — correo de autorización (no enviado).
