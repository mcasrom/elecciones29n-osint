# Changelog

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
