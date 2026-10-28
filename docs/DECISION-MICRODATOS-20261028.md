# Decisión sobre microdatos y v2 agregada — 2026-10-28

## Decisión

1. **El agregado no se toca.** Se mantienen los **8 sondeos y 6 casas** del 14-d (18–26 oct).
   No se excluye del cálculo a ninguna casa por no haber respondido.
2. **Los microdatos quedan bloqueados.** No se publican filas individuales de sondeos
   (`polls_history.csv`, `data/raw`, tablas por partido) de casas sin autorización.
3. **La v2 será agregada.** Incluirá media, rango, robustez, fuentes y metadatos; no
   incluirá sondeos individuales de terceros.
4. **La v2 agregada se publicó el 28-oct-2026.** Microdatos siguen bloqueados.
5. **Más sondeos sí, pero con criterio.** Se buscan casas nuevas con ficha técnica;
   no se persigue volumen ni se añaden promedios de otras webs.

## Por qué

- Excluir casas del agregado dejaría prácticamente **una sola casa** y destruiría
  la estimación de dispersión y de efecto de casa.
- Excluir solo de microdatos mantiene la media pública y evita redistribuir datos
  de terceros sin permiso.
- El silencio no es autorización. La autorización de Electomanía es limitada y no
  se extrapola a las demás casas.
- Zenodo no sustituye permisos: un DOI no convierte en lícita la redistribución.

## Estado de la v2

- Estado: **publicada el 2026-10-28**.
- DOI de versión: `10.5281/zenodo.23734740`.
- DOI conceptual: `10.5281/zenodo.23695702`.
- Registro: https://zenodo.org/records/23734740
- Datos incluidos: agregados y robustez, no filas individuales.
- Casas actuales: Ateneo del Dato, ElectoPanel, IMOP Insights, NC Report,
  Sigma Dos y Sociométrica.
- Casas sin autorización: no aparecen en microdatos; sus datos agregados publicados
  se citan con enlace y fecha.

## Referencias

- `docs/V2-AGREGADO-MANIFIESTO.md`
- `docs/v2-agregado-manifest.json`
- `docs/BUSQUEDA-SONDEOS-20261028.md`
