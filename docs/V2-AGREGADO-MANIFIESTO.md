# Manifiesto — v2 agregada del Observatorio 29N

**Estado:** publicado en Zenodo el **2026-10-28**.
**Snapshot:** 2026-10-28T09:18:07+01:00.
**Versión de datos:** `2.0-agregado`; **app:** `0.11.1`.
**DOI de esta versión:** `10.5281/zenodo.23734740`.
**DOI conceptual:** `10.5281/zenodo.23695702`.
**Publicación:** 2026-10-28 · [registro](https://zenodo.org/records/23734740).

## Alcance

- Agregado de sondeos y robustez.
- Censo, participación, territorio, resultados 2023, M4, M5 y fuentes.
- Contrato de datos v1, esquema, changelog y nota legal.
- **Sin** filas individuales de sondeos de terceros, `polls_history.csv`,
  `data/raw`, `subs.db`, logs, correos ni datos personales.

## Agregado de este snapshot

- **8 sondeos · 6 casas · 14 días** (18–26 oct).
- Casas: Ateneo del Dato, ElectoPanel, IMOP Insights, NC Report, Sigma Dos,
  Sociométrica.
- Muestra declarada: **75 %** (6 de 8).
- IQR: **2,3 pp**.
- Último sondeo: **26-oct**.
- Media y rango: los publicados en `web/data/latest.json`; no se recalculan aquí.

## Decisión de derechos

- **Agregado:** se mantiene con todas las casas; no se excluye a nadie por no
  responder.
- **Microdatos:** solo casas con autorización; hoy no hay base multicasa
  suficiente. No se publica una v2 de microdatos con una sola casa.
- **Casas sin autorización:** no aparecen en microdatos; sus datos agregados
  publicados se citan con enlace y fecha.
- **Electomanía:** autorización limitada; se respetan sus condiciones.
- **Onda Cero:** sin autorización y sin muestra completa; no entra en microdatos.

## Archivos incluidos

| Archivo | Bytes | SHA-256 |
|---|---:|---|
| `web/data/latest.json` | 73453 | `a6cc267a3032cf8e5bde261c68f3a7dfe16722915fbc45b1d96e7724b577a8b9` |
| `web/data/robustez.json` | 14927 | `5e1cf470b0b7ccf884fb9d04fbc0f38d1f0aa9528b08c6493f0fe5f65fb51fa0` |
| `web/data/v1/latest.json` | 73453 | `a6cc267a3032cf8e5bde261c68f3a7dfe16722915fbc45b1d96e7724b577a8b9` |
| `web/data/v1/robustez.json` | 14927 | `5e1cf470b0b7ccf884fb9d04fbc0f38d1f0aa9528b08c6493f0fe5f65fb51fa0` |
| `web/data/v1/schema.json` | 542 | `370ae8da0bb825a0a4e4a733801884cbeb1878d6135b329d916d238d90cdcfd1` |
| `data/fuentes_sondeos.csv` | 2187 | `b1f065a69b95710dc87b46c07bf37ea4f0cc6f3f9e9aa5278a6d3d4891cb8a31` |
| `CHANGELOG.md` | 12879 | `545fdd67bac35dcee1f0709a48e25b50c52436a027faf959858928fff1719d5d` |
| `CITATION.cff` | 367 | `0d737c87159a921c5fbf3d0a2481e72300cdc53fc14301f14814feb63c2981ec` |
| `README.md` | 21819 | `74f28e1d42b8e806c998dfc39b2a3d716c1518b2acd6217d9f0d941135090f49` |
| `docs/LEGAL-29N.md` | 11018 | `cb7cf015aecf262a50061d0d99511c3423203d09eeb63e2305e11939c36405f7` |

## Excluidos explícitamente

- `data/polls_history.csv`
- `data/entrada_sondeos.csv`
- `data/raw/**`
- `data/subs.db`
- `logs/**`, `web_prev/**`, `export/**`
- `*.bak`, `*.enc`, `.env`, claves y datos personales.

## Metadatos previstos

- **Título:** Observatorio electoral 29N — datos agregados (v2, snapshot 2026-10-28).
- **Tipo:** dataset.
- **Licencia:** CC BY 4.0 para datos propios y agregados; fuentes oficiales
  conservan su licencia.
- **Creador:** Miguel Castillo.
- **Relación:** suplemento de `https://elecciones29n.pruebapublica.com` y del
  repositorio.
- **DOI:** se asignará al publicar la versión; no se reutiliza el DOI de v1.
- **Nota:** no es un pronóstico ni una encuesta propia; el rango no es un
  intervalo de confianza.

## Verificación antes de publicar

1. Regenerar el snapshot y recalcular hashes.
2. Confirmar que `polls_history.csv` no está en el paquete.
3. Revisar que no haya datos personales ni claves.
4. Verificar que la nota de cobertura y las fuentes están actualizadas.
5. Confirmar que no se ha publicado una v2 de microdatos.
6. Subir solo tras OK explícito.
