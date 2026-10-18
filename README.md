# Observatorio electoral 29N

**Sondeos con rango, censo, participación y territorio.** Datos abiertos, método público y ninguna cifra que el dato no sostenga.

[![En vivo](https://img.shields.io/badge/en%20vivo-elecciones29n.pruebapublica.com-ff5a1f)](https://elecciones29n.pruebapublica.com/)
[![Licencia](https://img.shields.io/badge/licencia-AGPL--3.0-3ddc97)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.12-8ec5ff)](https://www.python.org/)
[![Versión](https://img.shields.io/badge/versi%C3%B3n-0.8.0-ff5a1f)](CHANGELOG.md)

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
- `/electorado.html` — Censo 29N: total, CER/CERA, edad y sexo, provincias y nuevos electores.
- `/participacion.html` — Participación nacional 1979–2023 y **provincial 1977–2023** (selector + comparación con la media nacional).
- `/territorio.html` — 350 escaños, 52 circunscripciones, electores por escaño y **votos↔escaños 2023 con índice de Gallagher**.
- `/factores.html` — Factores y participación: día/festivo, meteorología (M5) y **resultados v1**.
- `/comportamiento.html` — **M4 v1**: voto declarado en 2023 por edad, sexo e ideología (CIS 3582, n=5.025), con n por celda y celdas n<30 suprimidas.
- `/noche-electoral.html` — Qué se publica el 29N, cuándo y con qué fuente.
- `/metodologia.html` y `/fuentes.html` — Método, fuentes, catálogo de datos y licencias.

## Salud de la muestra

La portada muestra un panel de **salud de la muestra**: número de sondeos,
encuestadoras y días desde el último. Es el principal control de calidad del
agregado.

| Estado | Criterio | Qué significa |
|---|---|---|
| **Suficiente** | ≥4 sondeos, ≥2 casas, último ≤10 días | media entre encuestadoras |
| **Frágil** | 4 sondeos pero una sola casa, o último >10 días | se publica con aviso |
| **Insuficiente** | <4 sondeos o último >21 días | se publica con aviso visible |

> Al 18-oct: **15 sondeos, 12 encuestadoras, último hace 4 días → suficiente**.
> Se combinan Electomania, la compilación de Onda Cero y el CIS (septiembre y octubre). Ver
> [`docs/RUTINA-SEMANAL.md`](docs/RUTINA-SEMANAL.md).

```bash
.venv/bin/python scripts/health_report.py
```

## Fuentes

| Dato | Fuente | Formato |
|---|---|---|
| Sondeos | [Electomania · ElectoPanel](https://electomania.es/) | WordPress REST API |
| Sondeos (secundaria) | [Onda Cero · Encuestas 29N](https://www.ondacero.es/elecciones/generales/encuestas/) | HTML/JSON |
| Sondeos (manual) | [CIS · barómetros](https://www.cis.es/) | PDF |
| Contraste | [Política Sin Ruido](https://politicasinruido.com/encuestas) | HTML |
| Censo | [INE · CEL](https://www.ine.es/dyngs/CEL/es/index.htm?cid=1703) | XLSX (tablas 2/3/6/9/12) |
| Participación | [JEC](https://www.juntaelectoralcentral.es/) | tablas por elección |
| Escaños | [BOE · RD 806/2026](https://www.boe.es/diario_boe/txt.php?id=BOE-A-2026-20742) | anexo |
| Normativa | [LOREG](https://www.boe.es/buscar/act.php?id=BOE-A-1985-11672) | BOE consolidado |
| Resultados provinciales | Ministerio del Interior (XLSX) | `data/raw/elecciones-congreso.xlsx` · 1977–2023 |

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

- **Local-first**: la ingesta y el build corren en el portátil. El servidor solo
  sirve estático (cero backend, cero cron en servidor).
- **Fail-safe**: si la ingesta o la validación fallan, **no se publica nada** y
  se conserva la última versión buena (`web_prev/` para revertir).
- **Sin terceros**: sin cookies, sin analítica externa, sin publicidad.

## Puesta en marcha

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

bash scripts/check.sh       # compila + tests + validación del sitio local
bash scripts/run_daily.sh   # ingesta + agregado + build + deploy
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
ingest/         Electomania, censo (INE), participación (JEC), escaños (BOE)
gen/            build estático, OG, plantillas Jinja
data/           histórico de sondeos y datasets normalizados (fuente de verdad)
web/            salida estática publicada
scripts/        run_daily, check, validate_site, canary, IndexNow, add_poll, health_report
docs/           método, fuentes, rutina semanal, sprint del observatorio
tests/          34 pruebas (datos, build, validador)
systemd/        servicio y timer
```

## Meteorología y participación (M5 v1)

- Panel **provincia × elección** (806 observaciones, 16 elecciones) con participación provincial y AEMET OpenData.
- Modelo con **efectos fijos** de elección y provincia y errores agrupados: precipitación **−0,041 pp/mm** (IC −0,087 a 0,005; p=0,081); en **2004–2023**, −0,041 pp/mm (p=0,007).
- Correlación intra-elección −0,136. El viento sale positivo y **no se interpreta como causal**.
- Resultados y límites en `/factores.html` y `data/m5-results.json`. Método: `docs/M5-METODOLOGIA.md`.

## Contraste por casa

Además de la media por sondeo (ponderada por recencia y muestra cuando existe), la portada muestra el **contraste por casa**: la última encuesta de cada casa en 45 días, con **peso igual por casa**. Sirve para detectar si la media está dominada por una encuestadora. Incluye CIS. No es la media principal.

## PWA y actualizaciones

- Instalable: `manifest.webmanifest`, iconos 192/512/maskable y service worker.
- **Network-first** para HTML y `data/*.json`; cache-first para CSS/JS/OG/iconos.
- Aviso **«Nueva versión disponible»** con **Recargar** y **×**. El × se recuerda por
  versión y pestaña; no vuelve a molestar hasta el siguiente deploy.
- Un `[hidden]` global garantiza que ningún componente oculto se muestre por CSS.

## Calidad

- **51 tests** (`unittest`) y hook **pre-push**.
- `scripts/check.sh`: compila, tests y valida el sitio local.
- **Validador** de publicación: gráfico con puntos, pestañas, JSON, sitemap, OG,
  RSS, censo, participación y escaños.
- **Canario en vivo** tras cada deploy: comprueba en la URL pública el gráfico,
  el JSON, la OG, el censo, la participación, el territorio y las páginas nuevas.
- **Reversión**: `web_prev/` conserva la versión anterior.

## SEO y datos abiertos

- `sitemap.xml` (11 URLs), `robots.txt`, `llms.txt` y RSS `cambios.xml`.
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
- No se simulan escaños provinciales ni el Senado sin encuestas provinciales.
- No se atribuyen preferencias por edad, sexo, renta o territorio.
- No se mezclan señales sociales con sondeos, censo o participación.

## Hoja de ruta

- **M4 v1** · Comportamiento por grupos: ✅ hecho (CIS 3582, recuerdo 2023; edad/sexo/ideología; celdas n<30 suprimidas).
- **M5 v1** · Meteorología × participación: ✅ hecho (806 obs; −0,041 pp/mm; sin causalidad).
- **29N** · Activar resultados y participación oficiales tras la jornada (fallback manual listo).
- **Provincial** · ✅ participación 1977–2023 y votos↔escaños 2023 integrados.
- **M5b** (opcional) · placebo con el día anterior, umbrales de lluvia y robustez adicional.

## Licencia y cita

Código **AGPL-3.0** ([`LICENSE`](LICENSE)). Datos agregados reutilizables citando
el proyecto.

> Miguel Castillo. *Observatorio electoral 29N*. https://elecciones29n.pruebapublica.com

Contacto: **info.elecciones29n@pruebapublica.com**
