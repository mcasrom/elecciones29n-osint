# elecciones29n-osint

Media agregada de los sondeos publicados para las **Elecciones Generales del 29 de noviembre de 2026**, con rango mínimo–máximo, datos abiertos y cumplimiento del blackout electoral.

**En vivo:** https://elecciones29n.pruebapublica.com

---

## Qué hace y qué no

Muestra **tendencia y dispersión** de los sondeos publicados: media móvil de 14 días, mínimo, máximo y número de sondeos por partido.

No es un pronóstico, no estima intención de voto individual y no anticipa el resultado. La incertidumbre va en el dato: el rango se muestra siempre.

- **No mezcla** señales sociales (Bluesky, RSS) con la media de sondeos.
- **No corrige** sesgos de las encuestadoras.
- La pestaña *Congreso* aplica D'Hondt sobre la media nacional como **simulación mecánica** (distrito único, 350 escaños, umbral 3%), etiquetada como tal, nunca como proyección.
- La pestaña *Senado* no se simula: el reparto depende de listas provinciales y de las CCAA.

## Interfaz

- **Agregado**: KPIs, evolución reciente, tabla por partido y bloque para compartir/citar.
- **Evolución**: minigráficos por partido (cada punto es un sondeo publicado) con delta del periodo.
- **Congreso**: simulación D'Hondt + composición de referencia vigente + bloques de voto.
- **Senado**, **Metodología**, **Fuentes** y **Qué no dice**.
- Tema **claro/oscuro** con persistencia en el navegador.
- **Aviso pulsante** si el cron no se ha ejecutado (>26 h o pasadas las 09:00 sin actualización del día). La comprobación es en cliente, así que funciona aunque el generador esté parado.

## Electorado (censo 29N)

- Ingesta oficial del **INE · Oficina del Censo Electoral** (XLSX del 29N):
  total, CER, CERA, provincias, CCAA, edad/sexo (CER) y nuevos electores.
- `python -m ingest.censo` → `data/censo_2026.json` (con URL y SHA-256 de cada
  XLSX) y CSV en `web/data/`.
- Página `/electorado.html`: 4 cifras oficiales, edad/sexo, top CERA por país,
  provincias y nuevos electores.
- Validación al ingerir: provincias, CCAA, edad y nuevos cuadran con el total
  (38.728.356). Si no cuadra, no se sobrescribe el JSON.
- Límite declarado: edad/sexo solo cubre residentes en España; el extranjero no
  tiene ese desglose. El censo no dice a quién se vota.

## Participación histórica

- Serie nacional 1979–2023 (15 elecciones) de participación sobre censo.
- Fuente: **JEC**, con enlace a la tabla oficial de cada elección; serie
  normalizada con validación de extremos (2023 66,59 %; máx. 1982 79,97 %;
  mín. 2019-N 66,23 %).
- `python -m ingest.participacion` → `data/participacion.json` + CSV en
  `web/data/`.
- Página `/participacion.html`: última cita, media, máximo, mínimo, evolución y
  tabla con enlace a la JEC.
- Límite: participación **nacional**; el desglose provincial del Interior no es
  accesible desde el servidor (timeout) y se añadirá cuando se pueda verificar.

## Territorio y representación

- Asignación oficial de escaños por circunscripción: **BOE · RD 806/2026** (anexo), 350 diputados y 52 circunscripciones.
- Cruce con el censo del INE: **electores por escaño** por provincia (Teruel 35.417 ↔ Madrid 145.708; 4,1× de diferencia).
- `python -m ingest.escanos` → `data/escanos_2026.json` + CSV.
- Página `/territorio.html`: gráfico de electores/escaño, tabla completa y explicador (mínimo de 2 escaños, D'Hondt provincial, umbral del 3 %).
- Límite: no incluye votos↔escaños de 2023 por provincia (resultados del Interior no accesibles); no proyecta el 29N.

## Ayuda en pantalla y ecosistema

- Botón **«? Ayuda»** en la cabecera: abre un panel lateral con las claves de lectura (sondeos ≠ pronóstico, tres capas, datos oficiales, límites).
- Tarjeta **en el flujo** de la portada para la primera visita («¿Primera vez?»), con «Ver guía» y «×». Se cierra y no vuelve (`localStorage`).
- No hay overlay fijo ni popup bloqueante: no tapa el footer ni el botón de Ko-fi.
- Footer con enlaces al ecosistema: **Prueba Pública**, **Blog de análisis**, **Observatorio de amplificación** y **Vivienda**, con UTM.

## Documentación y páginas

- `/metodologia.html`: método de cada módulo (sondeos, censo, participación, territorio), reglas comunes y límites.
- `/fuentes.html`: fuentes por módulo, enlaces oficiales, catálogo de datos descargables (JSON/CSV) y licencias.
- `/apoyo.html`: Ko-fi, compartir y colaboración; qué financia y qué no cambia.
- `/sobre-mi.html`: autor, principios de trabajo, proyectos y contacto.

## Noche electoral 29N

- Página `/noche-electoral.html`: qué se publica y cuándo, qué no se publica y cómo se valida.
- Estado previo explícito: **sin datos electorales hasta después de la jornada**.
- Fuentes: Ministerio del Interior y JEC. No se usan sondeos a pie de urna como resultados.
- El módulo de resultados se activará con datos oficiales validados (participación, escrutinio).

## Datos

- Fuente de sondeos: **Electomania** (ElectoPanel) vía WordPress REST API, con paginación y backfill.
- Ingesta con filtros de plausibilidad: suma 90–110 %, ≥6 partidos, rango 0–45 %, sin autonómicos ni adelantos incompletos.
- Histórico versionado en `data/polls_history.csv` (`party,date,value,source_url,sample`).
- Salida pública: `web/data/latest.json` (agregado + series + series_long + KPIs).

## Arquitectura

```
ingest/electomania.py  →  data/polls_history.csv
agg/aggregate.py       →  web/data/latest.json (+ media 14d, series, KPIs)
agg/blackout.py        →  bloqueo 24–28 nov (LOREG/JEC)
gen/build.py           →  web/*.html, sitemap, robots, llms.txt, favicon
gen/gen_og.py          →  web/og.png (1200×630)
scripts/indexnow_push.py → IndexNow (Bing/Yandex)
scripts/rsync_push.sh  →  deploy@<server>:/var/www/elecciones29n/
```

`run_daily.sh` construye en `web_tmp/`, ejecuta `scripts/validate_site.py` y solo
entonces hace el swap a `web/` (guardando `web_prev/`). Si la validación falla no
se publica nada. Tras el despliegue, `scripts/canary_live.py` verifica en la URL
pública que el gráfico, el JSON y la OG están presentes.

- **Local-first**: la ingesta y el build corren en el portátil (16 GB, CPU modesto). El servidor solo sirve estático con nginx (cero cron, cero backend).
- **Fail-safe**: si la ingesta falla o los datos no pasan validación, no se actualiza nada y se conserva el último resultado válido.

## Uso

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

bash scripts/check.sh          # compila + tests + validación del sitio local
bash scripts/run_daily.sh      # ingest + agg + build + OG + IndexNow + deploy
bash scripts/rsync_push.sh     # solo publicar
python3 scripts/add_poll.py --party PP --value 31.8   # alta manual
```

## Cron local (systemd --user)

```bash
mkdir -p ~/.config/systemd/user ~/.local/state/elecciones29n
cp systemd/elecciones29n.service systemd/elecciones29n.timer ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now elecciones29n.timer
systemctl --user list-timers | grep elecciones   # siguiente ejecución

# Opcional: que el timer corra sin sesión iniciada
sudo loginctl enable-linger $USER

# Vigilante al iniciar sesión (avisa si no corrió a las 08:00)
mkdir -p ~/.config/autostart
cp elecciones29n-watchdog.desktop ~/.config/autostart/
```

El servicio escribe en `~/.local/state/elecciones29n/run.log` y el pipeline termina con `rsync`, así que una ejecución correcta publica sola.

## Blackout electoral (LOREG / JEC)

Del **24 al 28 de noviembre de 2026** (ambos inclusive) no se publican, difunden ni reproducen sondeos. El agregado se congela: no se generan cifras nuevas y la web conserva el último resultado válido con su fecha. El aviso de datos desactualizados no se muestra durante el blackout.

## SEO y datos abiertos

- `sitemap.xml`, `robots.txt`, canonical, `og.png` 1200×630 y `twitter:card`.
- JSON-LD: `WebSite`, `Dataset` (AGPL, distribución JSON) y `FAQPage`.
- `llms.txt` para asistentes de IA.
- **IndexNow** en cada build.
- Cache-busting (`?v=<timestamp>`) en CSS/JS para evitar caché de edge.

## Seguridad

- Sin credenciales en el repositorio. `.gitignore` cubre `.env`, `*.env`, `*.pem` y `*.key`.
- La publicación usa clave SSH; no hay secretos en el código ni en el historial.
- Sin cookies, sin analítica de terceros, sin backend.

## Límites declarados

- Una media no sustituye a la incertidumbre.
- La simulación de Congreso es un artefacto educativo, no una proyección.
- Los datos dependen de que las encuestadoras publiquen; un parón de publicación no es un parón del cron.

## Licencia

AGPL-3.0. Ver `LICENSE`.

## Cita

Miguel Castillo. *elecciones29n-osint: media agregada de sondeos, elecciones generales 29N 2026*. https://elecciones29n.pruebapublica.com
