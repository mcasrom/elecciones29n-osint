# Changelog

## 0.8.4 — 2026-10-18

- **Auditoría de datos reproducible** (`scripts/audit_datos.py`): **202 comprobaciones, 0 fallos críticos** (offline + online). Verifica sondeos, censo, participación, territorio, M4, M5, etiquetas de UI y fuentes (Onda Cero/CIS/Electomania).
- `check.sh` ejecuta la auditoría offline; `docs/AUDITORIA-DATOS.md` documenta alcance y límites.

## 0.8.3 — 2026-10-18

- **SEO**: JSON-LD por página (`Dataset` en participación, territorio, M5 y M4; `WebPage` en método/fuentes/límites/apoyo/acerca) en vez del Dataset de sondeos en todas.
- **`favicon.ico`** (Googlebot-Image pedía `/favicon.ico` y daba 404).
- Validador: comprueba JSON-LD por página y `favicon.ico`; canario incluye favicon.
- Auditoría de sitemap/indexado: 13 URLs, todas 200 con Googlebot; Googlebot/Bingbot/Applebot rastrean. Nuevas páginas pendientes de recrawl/GSC.

## 0.8.2 — 2026-10-18

- **Anexo de transparencia meteorológico** en `/factores.html`: tabla nacional por elección (16 filas) en un `<details>` colapsable, con descarga JSON/CSV nacional y CSV provincial. Sin mapa ni cambios en la portada.

## 0.8.1 — 2026-10-18

- **Auditoría de métricas**: `metrics.py` como fuente única (MA 14 d, resumen de tarjeta, periodo).
- Fix: la tarjeta de Evolución usaba el **último sondeo** (CIS) y un delta contra el primer sondeo de otra casa. Ahora cifra y delta son **MA 14 d**; periodo real.
- Tests (`test_metrics.py`) y validador recalculan la MA y el periodo desde `latest.json`.

## 0.8.0 — 2026-10-18

- **M4 v1**: voto declarado en 2023 por **edad, sexo e ideología** (CIS 3582, n=5.025), base de votantes a partidos, **N ponderado** y **celdas n<30 suprimidas**.
- Página `/comportamiento.html` con tablas, fuente y límites; JSON/CSV abiertos.
- Corrección de la agregación de «Otros» y de la normalización a voto a partidos.

## 0.7.0 — 2026-10-18

- **Onda Cero**: 94 sondeos de 14 casas integrados como fuente secundaria (sondeos individuales, no su promedio; fecha de publicación).
- **CIS**: barómetros de septiembre (n=4.042) y octubre (n=5.025) añadidos a mano con PDF y muestra.
- **Contraste por casa**: última encuesta de cada casa en 45 días con peso igual (14 casas), frente a la media por sondeo.
- Normalización de nombres (`Podemos`/`PODEMOS`, `Bildu`/`BILDU`, `Junts`/`JUNTS`); `n_polls` cuenta sondeos, no fechas.
- «Otros» se excluye de KPIs, gráficos y simulación; se mantiene en la tabla.

## 0.6.0 — 2026-10-18

- **M5 v1**: meteorología × participación con panel provincia × elección (806 obs, 16 elecciones), AEMET OpenData y OLS con efectos fijos y SE agrupados.
- Resultados en `/factores.html` y `data/m5-results.json`: asociación negativa modesta; en 2004–2023, −0,041 pp/mm (p=0,007). Sin afirmación causal.

## 0.5.0 — 2026-10-18

- **Datos provinciales**: 16 elecciones × 52 provincias; participación 1977–2023 con selector y comparación con la media nacional.
- **Votos↔escaños 2023** en `/territorio.html`, con índice de Gallagher y aviso CERA.
- **PWA**: aviso de nueva versión con Recargar/×; el cierre se recuerda por versión y pestaña. Fix: `[hidden]` ya no queda anulado por CSS.
- `ingest/congreso.py` y `data/raw/elecciones-congreso.xlsx` como fuente reproducible.

## 0.4.0 — 2026-10-18

- **PWA-lite**: manifest, iconos, service worker network-first y aviso de nueva versión.
- **Observatorio**: censo (INE), participación (JEC), territorio (BOE) y página de factores.
- **Sondeos**: media ponderada, mediana, salud de la muestra y alta manual (CSV/comando).
- **Documentación**: método, fuentes, rutina semanal, noche electoral y registro de fuentes.
- **Calidad**: staging + validación + swap atómico + canario en vivo; 34 tests.
- **Versión en el pie** y `version.json` público.

## 0.3.0 — 2026-10-17

- Agregado de sondeos con rango, evolución, Congreso y Senado.
- SEO: sitemap, robots, OG, JSON-LD, FAQ e IndexNow.
- Tema claro/oscuro y aviso de datos desactualizados.

## 0.2.0 — 2026-10-17

- Ingesta real de Electomania, blackout electoral y primeros tests.

## 0.1.0 — 2026-10-17

- MVP: ingesta, agregado, build estático y despliegue.
