# M5 · Meteorología y participación (v1)

## Datos

- **Participación**: XLSX provincial del Ministerio del Interior (16 elecciones,
  1977–2023) → `data/congreso.json`.
- **Meteorología**: AEMET OpenData, valores climatológicos diarios del día de
  cada elección, agregados por provincia → `data/meteo_electoral.json`.
  Variables: precipitación media y máxima, % de estaciones con lluvia,
  temperatura máxima/mínima y viento medio. `Ipyn` se trata como 0,05 mm.
- **Clave AEMET**: `AEMET_API_KEY` en el entorno (o fallback al `.env` del
  ecosistema en el servidor). No se versiona.

## Método

Unidad: **provincia × elección**. Modelo:

```
participación ~ precipitación + tmax + viento + EF elección + EF provincia
```

Errores estándar agrupados por provincia (52 clusters). Se reporta el efecto en
puntos porcentuales y su IC. Modelo alternativo con `% de estaciones con lluvia`.
Robustez: 2004–2023 (mejor cobertura) y provincias con ≥3 estaciones.

## Resultados (v1)

- n = **806**; 16 elecciones; 52 provincias. R² = 0,90 (dominado por los EF).
- Correlación simple −0,174; **intra-elección −0,136**.
- Precipitación: **−0,041 pp/mm** (IC −0,087 a 0,005; p=0,081).
- En **2004–2023**: −0,041 pp/mm (IC −0,070 a −0,011; p=0,007).
- % de estaciones con lluvia: −0,010 pp por punto porcentual (p=0,0007).
- Viento: +0,24 pp por m/s (p=0,019). **No se interpreta como causal**: puede
  reflejar sistemas meteorológicos o correlación espuria.
- Bins intra-elección: 0 mm +0,41 pp; 0–1 mm −0,38; 1–5 mm −0,18; >5 mm −2,02.

## Límites

- Asociación observacional, **no causalidad**.
- Cobertura de estaciones desigual (1977–1982: ~120–140 estaciones).
- Agregación provincial: oculta variación local.
- No se predice participación ni voto.

## Reproducir

```bash
# 1) AEMET (requiere AEMET_API_KEY; el JSON agregado se versiona)
python ingest/aemet.py
# 2) análisis (dependencias de analysis, no del cron)
pip install -r requirements-analysis.txt
python scripts/m5_analysis.py
bash scripts/run_daily.sh
```


## Anexo de transparencia (18-oct, v0.8.2)

En **`/factores.html` → Resultados (v1)** hay un `<details>` colapsable
**«Datos meteorológicos usados»** con la tabla nacional por elección
(16 filas): estaciones, precipitación media, % de estaciones con lluvia y
tmax media. Se agrega **ponderando por número de estaciones**; 1979/1982
tienen menos cobertura.

Descargas: `/data/meteo-electoral.json`, `meteo-electoral.csv` (nacional) y
`meteo-electoral-provincias.csv` (provincial). No hay mapa ni tarjeta en la
portada: es un anexo de auditoría, no un dashboard.
