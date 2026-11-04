# Sprint — Mi circunscripción (fase 2)

**Estado:** MVP desplegado el 4-nov-2026 (`247ef2d`).  
**Objetivo:** ampliar la página sin convertirla en una proyección ni inventar cobertura.

## Ya hecho

- Buscador de 8.008 municipios.
- Municipio → provincia por código INE.
- Escaños, censo, participación y resultado oficial de 2023.
- Enlace a ficha provincial y calculadora D'Hondt.
- Una sola página; sin 8.000 URLs.
- Aviso explícito: no hay media provincial de encuestas.

## Fase 2A — Sliders D'Hondt

- Reutilizar la calculadora de `/circunscripcion/<slug>.html`.
- Base inicial: **votos de 2023**, no una media nacional repartida.
- Sliders para PP, PSOE, VOX, Sumar y otros.
- Normalizar porcentajes automáticamente.
- Botón **Restablecer a 2023**.
- Etiqueta fija: **escenario del usuario, no pronóstico**.
- Tests: suma normalizada, umbral del 3 %, escaños ≤ circunscripción.

## Fase 2B — Vivienda

- Fuente: SERPAVI/MIVAU (mediana de contratos, anual).
- Cobertura actual: **431 municipios**.
- Mostrar `sin dato` en el resto; **no estimar**.
- Enlazar a `vivienda.pruebapublica.com` y declarar la cobertura.

## Fase 2C — Población

- Incorporar población municipal del INE.
- Mostrar evolución solo si hay serie verificable y fuente por año.
- No usar población para inferir voto ni escaños.

## Límites duros

- **No** publicar una media provincial: no existe.
- **No** repartir la media nacional por provincias.
- **No** presentar el simulador como proyección.
- **No** tocar la media, Onda Cero ni el gráfico de portada.
- **No** generar páginas por municipio.

## Criterio de cierre

- Página < 2 s en móvil con datos cacheados.
- Búsqueda tolerante a tildes y nombres alternativos.
- Tests de datos y de calculadora.
- Aviso de límites visible sin abrir detalles.
