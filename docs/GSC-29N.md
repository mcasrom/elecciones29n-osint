# GSC 29N — lectura del aviso de cobertura

## Qué dice el export del 18-nov

| Motivo | Páginas | Lectura |
|---|---:|---|
| No encontrada (404) | 3 | Corregir enlaces o recursos. |
| Excluida por `noindex` | 2 | **Intencionado** en páginas de embed. No tocar. |
| Rastreada, sin indexar | 119 | Mezcla de assets y páginas; no es un único error técnico. |
| Descubierta, sin indexar | 1 | Revisar con drilldown. |
| Error 5xx | 0 | Sin problema de servidor. |

## Por qué 119 no son 119 páginas

La lista de ejemplos incluye:

- `sw.js?v=202611...` — decenas de variantes por el cache-busting del service worker.
- `/data/*.json` y `/data/*.csv` — datos descargables, no páginas.
- `/version.json`, `/data/v1/*`, `/manifest.webmanifest`.
- Páginas de contenido: portada, territorio, metodología, participación, factores, provincias y páginas EN.

Es decir: **una parte importante del aviso era ruido de rastreo de assets**, no contenido roto.

## Corregido

- Eliminado `?v=` del registro del service worker en todas las páginas y en la plantilla.
- `robots.txt` bloquea ahora:
  - `/data/`
  - `/sw.js`
  - `/version.json`
  - `/manifest.webmanifest`
  - `/cambios.xml`
- `/contacto.html` → **301** a `/sobre-mi.html`.
- `/apple-touch-icon.png` → **200**.
- Enlace del glosario corregido a `/sobre-mi.html`.
- `noindex` de `/embed/*` se mantiene: es intencionado.

## Noindex intencionados

- `/embed/medias.html`
- `/embed/hemiciclo.html`
- `/embed/robustez.html`

GSC ve 2 de las 3. No se quita el `noindex`.

## Páginas de contenido sin indexar

Comprobadas las 97 URLs del sitemap:

- todas responden **200**;
- todas tienen **canonical propio**;
- ninguna tiene `noindex`;
- `robots.txt` permite el rastreo.

La portada y varias páginas clave siguen en “rastreada, sin indexar”. Eso **no es un fallo de etiqueta**: es una decisión de Google sobre un sitio nuevo con muchas URLs y poca autoridad. No se resuelve con “solicitar indexación” en masa.

## Qué hacer

1. Esperar el recrawl tras eliminar `sw.js?v` y bloquear assets.
2. Revisar el drilldown para el tercer 404.
3. No tocar los embed.
4. No hacer indexación masiva.
5. Seguir con distribución y enlaces internos; el aviso de 119 bajará solo en parte.

## GSC

Solo export manual. No se automatiza.
