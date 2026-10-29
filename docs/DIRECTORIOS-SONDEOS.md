# Directorios de sondeos — política de uso

**Fecha:** 2026-10-29
**Regla:** un directorio sirve para **descubrir**; no es una fuente primaria ni una encuesta.

## Jerarquía

1. **Fuente primaria:** publicación de la casa, PDF, tabla o nota metodológica.
2. **Medio que publica:** El País, El Mundo, ABC, La Razón, etc.
3. **Agencia/medio:** Europa Press, RTVE, Antena 3.
4. **Directorio/agregador:** comparaVoto, Mapa Electoral, promedios.
5. **Producto propio:** PruebaPública 29N; no se usa para localizar sondeos como si fuera independiente.

## Uso permitido

- Consultar RTVE, Europa Press, Antena 3, comparaVoto y Mapa Electoral para **detectar** una pieza.
- Abrir la **URL original** y comprobar tabla, campo, muestra y método.
- Registrar la pieza en `data/entrada_sondeos.csv` y sus metadatos en `data/registro_sondeos.csv`.
- Si no hay fuente original o ficha: marcar **`no_verificado`**.
- Un **promedio** ajeno se usa solo como contraste, nunca como sondeo.

## Prohibido

- Sumar un promedio como si fuera una encuesta.
- Completar muestra, método o partidos por inferencia.
- Usar un directorio como fuente si no enlaza la publicación original.
- Duplicar la misma encuesta por aparecer en varios medios.
- Hacer scraping de directorios.

## Campos de `registro_sondeos.csv`

`pollster, date, media, url_original, url_medio, field_start, field_end, sample, method, margin, kind, verification, seats, notes`

- `date`: fecha de publicación.
- `field_start/field_end`: trabajo de campo.
- `kind`: `sondeo` o `promedio`; los promedios no entran.
- `verification`: `verificado`, `parcial`, `no_verificado`.
- `seats`: estimación publicada, si existe; no recalcular.
- `notes`: fuente, dudas y motivo de la clasificación.

## Flujo

1. Detectar en un directorio.
2. Abrir fuente original.
3. Verificar tabla y ficha.
4. Registrar metadatos.
5. Añadir valores a `data/entrada_sondeos.csv`.
6. Importar, regenerar y comprobar salud.
7. No tocar scoring ni media a mano.

## Estado actual

- `data/directorios_sondeos.csv`: RTVE, Europa Press, Antena 3, PruebaPública, comparaVoto y Mapa Electoral.
- `comparaVoto` y `Mapa Electoral` quedan **por verificar** hasta confirmar URL y metodología.
- `data/registro_sondeos.csv`: plantilla de metadatos, sin filas todavía.
