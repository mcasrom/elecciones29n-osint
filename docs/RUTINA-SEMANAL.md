# Rutina semanal de sondeos

> Objetivo: que la media tenga **al menos 4 sondeos y 2 encuestadoras**. Con una
> sola casa, la «media» es su serie, no un agregado entre casas.
>
> Tiempo: **10–15 minutos**, los lunes por la mañana.

## 1. Revisar fuentes

Buscar publicaciones nuevas desde el último sondeo registrado:

| Encuestadora | Dónde suele publicar | Notas |
|---|---|---|
| CIS | cis.es · barómetros | mensual; muestra grande |
| 40dB | 40db.es / El País | semanal |
| GAD3 | prensa (ABC, La Vanguardia) | frecuente |
| Sigma Dos | El Mundo | frecuente |
| SocioMétrica | El Español | frecuente |
| Simple Lógica | elDiario.es / web | periódica |
| NC Report | La Razón | periódica |
| DYM | prensa | ocasional |
| ElectoPanel | electomania.es | ya automatizado |

No hace falta cubrirlas todas cada semana: con **2–3 casas** la muestra mejora.

## 2. Alta de un sondeo

Modo lote (recomendado): una línea por sondeo, con todos los partidos que publica.

```bash
.venv/bin/python scripts/add_poll.py \
  --date 2026-10-20 \
  --pollster "40dB" \
  --sample 1500 \
  --source-url "https://…" \
  --values "PP=31.8,PSOE=27.1,VOX=18.9,SUMAR=5.4,Podemos=3.3,ERC=2.0,Junts=1.2,Bildu=1.3,PNV=1.1,SAF=1.8"
```

- Solo los partidos que publica la fuente; si faltan, la suma avisará.
- La suma debe quedar **90–110 %**. Si no, revisa antes de continuar.
- `--kind average` solo para promedios de otras casas (se excluyen de la media).

Modo simple (un partido):

```bash
.venv/bin/python scripts/add_poll.py --party PP --value 31.8 --date 2026-10-20 \
  --pollster "40dB" --sample 1500 --source-url "https://…"
```

## 3. Validar y publicar

```bash
bash scripts/check.sh          # compila + tests + validación local
.venv/bin/python scripts/health_report.py
bash scripts/run_daily.sh      # agrega, valida, publica y purga
```

`run_daily.sh` ya hace staging, validación, swap, rsync, canary e IndexNow.
No publiques a mano si `check.sh` o la validación fallan.

## 4. Leer la salud

```bash
.venv/bin/python scripts/health_report.py
```

- **Muestra suficiente**: ≥4 sondeos y ≥2 encuestadoras, último ≤10 días.
- **Muestra frágil**: 4 sondeos pero una sola casa, o último >10 días. Se publica con aviso.
- **Muestra insuficiente**: <4 sondeos o último >21 días. Se publica, pero el aviso es visible.

La tarjeta **«Salud de la muestra»** de la portada muestra los mismos números.

## 5. Reglas

- **Fuente y muestra** siempre que existan; sin enlace, no entra.
- **No mezclar** promedios de otras casas (`kind=average`) con paneles.
- **No usar adelantos parciales** en la media; si se quieren mostrar, van aparte.
- **No inventar** ni completar partidos que la fuente no publica.
- **No corregir** una cifra sin enlace a la fuente.
- Si una fuente cambia de formato, se documenta y se decide: no se parchea a ciegas.

## 6. Registro

Cada alta queda en `data/polls_history.csv` con `pollster`, `source_url` y
`sample`. El histórico es el registro: no hace falta un fichero aparte.
