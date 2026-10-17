from __future__ import annotations

import json
import os
from datetime import datetime

import pytz
from jinja2 import Environment, FileSystemLoader, select_autoescape

from agg import blackout


TZ = pytz.timezone("Europe/Madrid")
SITE_URL = "https://elecciones29n.pruebapublica.com"
SITE_NAME = "elecciones29n-osint"
SITE_TITLE = "Sondeos elecciones generales 29N 2026"
SITE_DESC = (
    "Media agregada de los sondeos publicados para las elecciones generales "
    "del 29 de noviembre de 2026, con rango mínimo–máximo y datos abiertos."
)

INDEXNOW_KEY = "e29n0sint2026b7f3c1a9d4e6"

PAGES = [
    ("index.html", "", "2026-10-17", "daily", "1.0"),
    ("metodologia.html", "metodologia.html", "2026-10-17", "monthly", "0.8"),
    ("fuentes.html", "fuentes.html", "2026-10-17", "weekly", "0.7"),
    ("about.html", "about.html", "2026-10-17", "monthly", "0.5"),
    ("caveat.html", "caveat.html", "2026-10-17", "monthly", "0.5"),
]


def ensure_dirs() -> None:
    os.makedirs("web/css", exist_ok=True)
    os.makedirs("web/js", exist_ok=True)
    os.makedirs("web/data", exist_ok=True)


def write_css() -> None:
    css = """/* elecciones29n-osint */
:root{--bg:#0b0c1c;--panel:#12142a;--panel2:#171a34;--fg:#eef0f6;--muted:#a7abc4;--faint:#7c819c;--accent:#ff5a1f;--accent2:#3ddc97;--blue:#8ec5ff;--line:#262a4a;--hero-a:#1b1f45;--hero-b:#0b0c1c;--btn-fg:#14080a;--badge-fg:#0b0c1c;--seat-a:#ff5a1f;--seat-b:#ff9b6b;--dot-grid:#2a2b45}
:root[data-theme="light"]{--bg:#f4f6fb;--panel:#ffffff;--panel2:#eef1f8;--fg:#131a28;--muted:#4d5a73;--faint:#75829a;--blue:#1b62c9;--line:#d9e0ee;--hero-a:#e7ecf7;--hero-b:#f4f6fb;--btn-fg:#fff;--badge-fg:#06210f;--dot-grid:#c9d3e6}
html,body{transition:background-color .25s ease,color .25s ease}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;font-family:Inter,system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;background:radial-gradient(1200px 600px at 80% -10%,var(--hero-a) 0%,var(--hero-b) 55%);background-color:var(--bg);color:var(--fg);line-height:1.6}
a{color:var(--blue)}
.container{max-width:1120px;margin:0 auto;padding:0 20px}

/* masthead */
.masthead{border-bottom:1px solid var(--line);background:linear-gradient(180deg,rgba(23,26,52,.9),rgba(11,12,28,.6));backdrop-filter:blur(6px);position:relative}
.topbar{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:14px 0;flex-wrap:wrap}
.brand{display:flex;align-items:center;gap:10px}
.mark{width:14px;height:14px;border-radius:4px;background:linear-gradient(135deg,var(--accent),#ffb37a);box-shadow:0 0 18px rgba(255,90,31,.55)}
.brandname{font-weight:800;font-size:19px;letter-spacing:-.02em}
.brandname a{color:var(--fg);text-decoration:none}
.badge{font-size:10.5px;letter-spacing:.12em;font-weight:700;color:var(--badge-fg);background:var(--accent2);padding:3px 7px;border-radius:5px}
.themebtn{appearance:none;border:1px solid var(--line);background:var(--panel);color:var(--muted);width:34px;height:34px;border-radius:9px;cursor:pointer;font-size:15px;line-height:1;display:inline-flex;align-items:center;justify-content:center}
.themebtn:hover{color:var(--fg)}
.status{font-size:12.5px;color:var(--muted);display:flex;align-items:center;gap:8px;font-family:ui-monospace,SFMono-Regular,Menlo,monospace}
.dot{width:8px;height:8px;border-radius:50%;background:var(--accent2);box-shadow:0 0 10px var(--accent2);animation:pulse 1.8s infinite}
.dot.off{background:var(--accent);box-shadow:0 0 10px var(--accent)}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.45}}

.hero{padding:26px 0 8px}
.eyebrow{margin:0 0 8px;font-size:12px;letter-spacing:.16em;text-transform:uppercase;color:var(--accent2);font-weight:700}
.hero h1{margin:0;font-size:clamp(30px,5vw,52px);line-height:1.05;letter-spacing:-.035em;font-weight:850;max-width:16ch}
.sub{margin:12px 0 0;color:var(--muted);font-size:clamp(15px,2vw,18px);max-width:62ch}
.hero-kpis{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin:22px 0 0}
.hk{background:linear-gradient(180deg,var(--panel2),var(--panel));border:1px solid var(--line);border-radius:14px;padding:14px 16px}
.hk b{display:block;font-size:clamp(26px,4vw,38px);line-height:1;letter-spacing:-.03em;font-weight:850}
.hk span{display:block;margin-top:6px;font-size:12px;color:var(--muted)}
.hk.accent b{color:var(--accent)}
.stamp{margin:16px 0 0;font-size:13px;color:var(--faint)}
.stamp strong{color:var(--muted)}

/* tabs */
.tabs{display:flex;gap:6px;flex-wrap:wrap;padding:14px 0 0;border-top:1px solid var(--line);margin-top:20px}
.tab{appearance:none;border:1px solid transparent;background:transparent;color:var(--muted);font:inherit;font-size:14px;padding:9px 14px;border-radius:9px;cursor:pointer;text-decoration:none}
.tab:hover{color:var(--fg);background:var(--panel)}
.tab.active{color:var(--bg);background:var(--fg);font-weight:700}
.tabpanel{display:none}
.tabpanel.active{display:block}

/* content */
main{padding-bottom:10px}
h2{font-size:19px;margin:0;letter-spacing:-.01em}
h3{font-size:15px;margin:16px 0 6px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:18px;margin:16px 0}
.cardhead{display:flex;align-items:baseline;justify-content:space-between;gap:10px;flex-wrap:wrap;margin-bottom:12px}
.hint{font-size:12px;color:var(--faint)}
.muted{color:var(--muted)}
.small{font-size:13px}
.alert{border:1px solid var(--line);border-left:3px solid var(--accent);background:var(--panel2);border-radius:10px;padding:12px 14px;margin:16px 0;color:var(--muted);font-size:14px}
.alert.warn{border-left-color:#f2c94c}
.alert strong{color:var(--fg)}

/* kpis */
.kpis{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin:16px 0}
.kpi{background:linear-gradient(180deg,var(--panel2),var(--panel));border:1px solid var(--line);border-radius:14px;padding:14px 16px}
.kpi-name{display:block;font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);font-weight:700}
.kpi b{display:block;font-size:32px;line-height:1.1;letter-spacing:-.03em;margin-top:4px}
.kpi-range{display:block;font-size:12px;color:var(--faint);margin-top:2px}

/* table */
table{width:100%;border-collapse:collapse}
th,td{border-bottom:1px solid var(--line);padding:9px 8px;text-align:left}
th{font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:var(--faint);font-weight:700}
td.num{font-variant-numeric:tabular-nums;text-align:right}
tbody tr:hover td{background:var(--panel2)}

/* chart */
svg.chart{width:100%;height:auto;display:block}
@media(max-width:760px){svg.chart{min-width:560px}}
.chartwrap{overflow-x:auto}

/* legend */
.legend{display:flex;flex-wrap:wrap;gap:14px;margin:10px 2px 0;font-size:12.5px;color:var(--muted)}
.lg{display:inline-flex;align-items:center;gap:6px}
.lg i{width:10px;height:10px;border-radius:3px;display:inline-block}

/* sparks (evolución) */
.sparks{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin-top:6px}
.spark{background:var(--panel2);border:1px solid var(--line);border-radius:12px;padding:12px}
.sparkhead{display:flex;align-items:baseline;justify-content:space-between;gap:8px}
.sparkhead span{font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);font-weight:700}
.sparkhead b{font-size:20px;letter-spacing:-.02em}
.spark svg{width:100%;height:auto;display:block;margin:6px 0 2px}
.sparkfoot{display:flex;align-items:center;justify-content:space-between;font-size:11px;color:var(--faint);font-variant-numeric:tabular-nums}
.delta.up{color:var(--accent2)}
.delta.down{color:var(--accent)}
.delta.flat{color:var(--faint)}
@media(max-width:900px){.sparks{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:560px){.sparks{grid-template-columns:1fr}}

/* seats + blocks */
.seats{display:flex;flex-direction:column;gap:8px;margin-top:6px}
.seatrow{display:grid;grid-template-columns:92px 1fr 46px;align-items:center;gap:10px}
.sname{font-weight:700;font-size:14px}
.sbar{height:12px;background:var(--panel2);border-radius:6px;overflow:hidden;border:1px solid var(--line)}
.sbar i{display:block;height:100%;background:linear-gradient(90deg,var(--seat-a),var(--seat-b))}
.snum{text-align:right;font-variant-numeric:tabular-nums;font-weight:700}
.blocks{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:6px}
.block{background:var(--panel2);border:1px solid var(--line);border-radius:12px;padding:12px 14px}
.block span{display:block;font-size:12px;color:var(--muted)}
.block b{display:block;font-size:26px;letter-spacing:-.02em}

/* share + cta */
.cta{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin-top:12px}
.btn{display:inline-block;padding:9px 14px;border-radius:9px;background:var(--accent);color:var(--btn-fg);text-decoration:none;font-weight:700;font-size:14px}
.btn.ghost{background:transparent;border:1px solid var(--line);color:var(--fg);font-weight:500}
.share{display:flex;gap:8px;flex-wrap:wrap;margin-top:10px}
.share a{font-size:13px;padding:6px 11px;border:1px solid var(--line);border-radius:9px;text-decoration:none;color:var(--muted)}
.share a:hover{color:var(--fg);border-color:var(--muted)}

/* stale warning */
.stale{position:sticky;top:0;z-index:60;background:#3a0d0d;border-bottom:2px solid var(--accent);color:#ffd9c9;padding:10px 20px;font-size:14px;animation:stalePulse 1.4s infinite}
:root[data-theme="light"] .stale{background:#ffe9e2;color:#7a1f08}
.stale strong{color:#fff}
@keyframes stalePulse{0%,100%{background:#3a0d0d}50%{background:#611a1a}}

/* footer */
.footer{border-top:1px solid var(--line);padding:24px 0;color:var(--faint);font-size:13.5px;margin-top:24px}
.footer p{margin:4px 0}

details{border:1px solid var(--line);border-radius:10px;padding:10px 12px;margin:8px 0;background:var(--panel2)}
summary{cursor:pointer;font-size:14px}
summary::-webkit-details-marker{display:none}

@media(max-width:760px){
  .hero-kpis,.kpis{grid-template-columns:repeat(2,minmax(0,1fr))}
  .blocks{grid-template-columns:1fr}
  .seatrow{grid-template-columns:76px 1fr 40px}
}
"""
    with open("web/css/main.css", "w", encoding="utf-8") as f:
        f.write(css)


def write_js() -> None:
    with open("web/js/charts.js", "w", encoding="utf-8") as f:
        f.write("/* charts inline; no external deps */\n")


def write_robots() -> None:
    robots = (
        "User-agent: *\n"
        "Allow: /\n"
        f"\nSitemap: {SITE_URL}/sitemap.xml\n"
    )
    with open("web/robots.txt", "w", encoding="utf-8") as f:
        f.write(robots)


def write_sitemap(today: str) -> None:
    rows = []
    for path, loc, lastmod, freq, prio in PAGES:
        url = f"{SITE_URL}/{loc}" if loc else f"{SITE_URL}/"
        rows.append(
            "  <url>"
            f"<loc>{url}</loc>"
            f"<lastmod>{today}</lastmod>"
            f"<changefreq>{freq}</changefreq>"
            f"<priority>{prio}</priority>"
            "</url>"
        )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(rows)
        + "\n</urlset>\n"
    )
    with open("web/sitemap.xml", "w", encoding="utf-8") as f:
        f.write(xml)


def write_indexnow_key() -> None:
    with open(f"web/{INDEXNOW_KEY}.txt", "w", encoding="utf-8") as f:
        f.write(INDEXNOW_KEY)


def write_llms() -> None:
    txt = f"""# {SITE_NAME}

> Media agregada de sondeos publicados para las elecciones generales de España
> del 29 de noviembre de 2026. No es un pronóstico ni una estimación de
> intención de voto: es la media móvil (14 días) de los sondeos publicados,
> con el rango mínimo–máximo observado.

## Qué ofrece
- Media móvil 14d por partido, con mínimo, máximo y n de sondeos.
- Serie temporal por partido (JSON) y datos descargables.
- Metodología, fuentes y límites explicados.

## Datos
- {SITE_URL}/data/latest.json
- {SITE_URL}/sitemap.xml

## Límites
- Solo sondeos publicados (no hay microdatos ni cocina de encuestas).
- Prohibido publicar sondeos del 24 al 28 de noviembre (JEC/LOREG); el
  agregado se congela en esas fechas y no se actualiza.
- Una media no sustituye a la incertidumbre: revisar siempre el rango.

## Código
- https://github.com/mcasrom/elecciones29n-osint (AGPL-3.0)

## Cita
Miguel Castillo. {SITE_NAME}: media agregada de sondeos, elecciones
generales 29N 2026. {SITE_URL}
"""
    with open("web/llms.txt", "w", encoding="utf-8") as f:
        f.write(txt)


def write_favicon() -> None:
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
        '<rect width="64" height="64" rx="12" fill="#0f1026"/>'
        '<rect x="10" y="30" width="10" height="24" rx="2" fill="#ff5a1f"/>'
        '<rect x="27" y="20" width="10" height="34" rx="2" fill="#3ddc97"/>'
        '<rect x="44" y="12" width="10" height="42" rx="2" fill="#8ec5ff"/>'
        "</svg>"
    )
    with open("web/favicon.svg", "w", encoding="utf-8") as f:
        f.write(svg)


REF_CONGRESO = [
    ("PP", 137), ("PSOE", 121), ("VOX", 33), ("SUMAR", 31),
    ("ERC", 7), ("Junts", 7), ("EH Bildu", 6), ("PNV", 5),
    ("BNG", 1), ("CC", 1), ("UPN", 1),
]


def simulate_congress(parties: list, total: int = 350, threshold: float = 3.0) -> dict:
    """Simulación mecánica D'Hondt nacional. NO es una proyección."""
    cands = [(p["party"], float(p["mean"])) for p in parties if float(p["mean"]) >= threshold]
    if not cands:
        return {}
    seats = {name: 0 for name, _ in cands}
    for _ in range(total):
        best = max(cands, key=lambda c: c[1] / (seats[c[0]] + 1))
        seats[best[0]] += 1
    return dict(sorted(seats.items(), key=lambda kv: kv[1], reverse=True))


def build_sparklines(series: dict, parties: list) -> str:
    """Minigráficos por partido (serie larga) para la pestaña Evolución."""
    order = [p["party"] for p in parties][:6]
    panels = []
    for party in order:
        pts = series.get(party, [])
        if len(pts) < 2:
            continue
        W, H, pad = 300, 110, 12
        vals = [p["value"] for p in pts]
        vmin, vmax = min(vals), max(vals)
        if vmax == vmin:
            vmax += 0.2
            vmin -= 0.2
        span = vmax - vmin

        def X(i):
            return pad + (W - 2 * pad) * i / (len(pts) - 1)

        def Y(v):
            return H - pad - (H - 2 * pad) * (v - vmin) / span

        coords = [(X(i), Y(p["value"])) for i, p in enumerate(pts)]
        d = "M " + " L ".join(f"{cx:.1f},{cy:.1f}" for cx, cy in coords)
        delta = vals[-1] - vals[0]
        cls = "up" if delta > 0.05 else ("down" if delta < -0.05 else "flat")
        sign = "+" if delta > 0 else ""
        dots = "".join(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="2.4" fill="#8ec5ff"/>' for cx, cy in coords)
        panels.append(
            f'<div class="spark">'
            f'<div class="sparkhead"><span>{party}</span><b>{vals[-1]:.1f}%</b></div>'
            f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Evolución de {party}">'
            f'<path d="{d}" fill="none" stroke="#ff5a1f" stroke-width="2"/>{dots}</svg>'
            f'<div class="sparkfoot"><span>{pts[0]["date"][5:].replace("-", "/")}</span>'
            f'<span class="delta {cls}">{sign}{delta:.1f} pts</span>'
            f'<span>{pts[-1]["date"][5:].replace("-", "/")}</span></div>'
            f"</div>"
        )
    return '<div class="sparks">' + "".join(panels) + "</div>" if panels else ""


def build_jsonld(parties: list, updated_at: str) -> str:
    dataset = {
        "@context": "https://schema.org",
        "@type": "Dataset",
        "name": "Media agregada de sondeos · Elecciones Generales 29N 2026",
        "description": SITE_DESC,
        "url": SITE_URL + "/",
        "creator": {"@type": "Person", "name": "Miguel Castillo", "url": SITE_URL},
        "license": "https://www.gnu.org/licenses/agpl-3.0.html",
        "isAccessibleForFree": True,
        "dateModified": updated_at,
        "temporalCoverage": "2026-09/2026-11",
        "spatialCoverage": "ES",
        "distribution": [
            {
                "@type": "DataDownload",
                "contentUrl": SITE_URL + "/data/latest.json",
                "encodingFormat": "application/json",
            }
        ],
    }
    website = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": SITE_NAME,
        "url": SITE_URL + "/",
        "inLanguage": "es-ES",
        "description": SITE_DESC,
    }
    faq = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": "¿Qué es la media agregada de sondeos?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "Es la media de los sondeos publicados en los últimos 14 días con su rango mínimo–máximo. No es un pronóstico ni una estimación de intención de voto.",
                },
            },
            {
                "@type": "Question",
                "name": "¿Puedo publicar sondeos el 24–28 de noviembre de 2026?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "No. La normativa electoral prohíbe publicar, difundir o reproducir sondeos del 24 al 28 de noviembre de 2026, ambos inclusive.",
                },
            },
            {
                "@type": "Question",
                "name": "¿De dónde salen los datos?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "De paneles publicados por Electomania, con enlace a la fuente y fecha. Se descartan paneles autonómicos y adelantos sin serie completa.",
                },
            },
        ],
    }
    return json.dumps([website, dataset, faq], ensure_ascii=False)


CHART_COLORS = ["#ff5a1f", "#3ddc97", "#8ec5ff", "#f2c94c", "#bb6bd9", "#56ccf2"]


def chart_legend(parties: list) -> list:
    return [
        {"party": p["party"], "color": CHART_COLORS[i % len(CHART_COLORS)]}
        for i, p in enumerate(parties[:6])
    ]


def build_chart(series: dict, parties: list) -> str:
    if not series or not parties:
        return ""

    order = [p["party"] for p in parties][:6]
    colors = CHART_COLORS
    dates = sorted({d["date"] for vals in series.values() for d in vals})
    if len(dates) < 2:
        return ""

    W, H = 760, 320
    pad_l, pad_r, pad_t, pad_b = 52, 18, 20, 40
    iw, ih = W - pad_l - pad_r, H - pad_t - pad_b

    vals_all = [d["value"] for p in order for d in series.get(p, [])]
    vmin = max(0, min(vals_all) - 2)
    vmax = max(vals_all) + 2

    def x(i: int) -> float:
        return pad_l + (iw * i / max(1, len(dates) - 1))

    def y(v: float) -> float:
        return pad_t + ih * (1 - (v - vmin) / (vmax - vmin))

    parts = [f'<svg class="chart" viewBox="0 0 {W} {H}" role="img" aria-label="Evolución de la media por partido">']
    for g in range(5):
        val = vmin + (vmax - vmin) * g / 4
        yy = y(val)
        parts.append(f'<line x1="{pad_l}" y1="{yy:.1f}" x2="{W-pad_r}" y2="{yy:.1f}" stroke="#2a2b45" stroke-width="1"/>')
        parts.append(f'<text x="6" y="{yy+4:.1f}" fill="#b9b9c3" font-size="11">{val:.0f}%</text>')
    for i, d in enumerate(dates):
        lbl = d[8:10] + "/" + d[5:7]
        parts.append(f'<text x="{x(i):.1f}" y="{H-10}" fill="#b9b9c3" font-size="10" text-anchor="middle">{lbl}</text>')
    for idx, party in enumerate(order):
        pts = series.get(party, [])
        if not pts:
            continue
        coords = []
        for p in pts:
            i = dates.index(p["date"])
            coords.append((x(i), y(p["value"])))
        dpath = "M " + " L ".join(f"{cx:.1f},{cy:.1f}" for cx, cy in coords)
        color = colors[idx % len(colors)]
        parts.append(f'<path d="{dpath}" fill="none" stroke="{color}" stroke-width="2.2"/>')
        for cx, cy in coords:
            parts.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="3" fill="{color}"/>')
    parts.append(f'<text x="12" y="{pad_t+4}" fill="currentColor" opacity="0.55" font-size="10">% voto</text>')
    parts.append("</svg>")
    return "".join(parts)


def main() -> None:
    ensure_dirs()
    write_css()
    write_js()
    write_robots()
    write_indexnow_key()
    write_llms()
    write_favicon()

    env = Environment(
        loader=FileSystemLoader("gen/templates"),
        autoescape=select_autoescape(["html", "xml"]),
    )

    latest = {"parties": []}
    if os.path.exists("web/data/latest.json"):
        with open("web/data/latest.json", encoding="utf-8") as f:
            latest = json.load(f)

    now = datetime.now(TZ)
    today = now.strftime("%Y-%m-%d")
    in_blackout = blackout.is_blackout(now)
    parties = latest.get("parties", [])
    series = latest.get("series", {})

    build_ts = now.strftime("%Y%m%d%H%M")
    context = {
        "build_ts": build_ts,
        "site_url": SITE_URL,
        "site_name": SITE_NAME,
        "site_title": SITE_TITLE,
        "site_desc": SITE_DESC,
        "updated_at": latest.get("updated_at", now.strftime("%Y-%m-%d %H:%M %Z")),
        "in_blackout": in_blackout,
        "blackout_reason": blackout.blackout_reason(),
        "parties": parties,
        "series": series,
        "poll_dates": latest.get("poll_dates", []),
        "n_polls": latest.get("n_polls", 0),
        "sources": latest.get("sources", []),
        "chart_svg": build_chart(series, parties),
        "chart_legend": chart_legend(parties),
        "sparks_svg": build_sparklines(latest.get("series_long", series), parties),
        "series_span": (
            f'{next(iter(latest.get("series_long", {}).values()))[0]["date"]} – '
            f'{next(iter(latest.get("series_long", {}).values()))[-1]["date"]}'
            if latest.get("series_long") else ""
        ),
        "updated_iso": latest.get("updated_at_iso", now.isoformat()),
        "days_to_election": latest.get("days_to_election", 0),
        "days_to_blackout": latest.get("days_to_blackout", 0),
        "last_poll_date": latest.get("last_poll_date"),
        "gap_pp_psoe": latest.get("gap_pp_psoe"),
        "bloc_right": latest.get("bloc_right"),
        "bloc_left": latest.get("bloc_left"),
        "sim_congress": simulate_congress(parties),
        "ref_congreso": REF_CONGRESO,
        "jsonld": build_jsonld(parties, latest.get("updated_at", today)),
        "indexnow_key": INDEXNOW_KEY,
        "share_url": SITE_URL + "/",
    }

    for tname in ["index.html", "metodologia.html", "fuentes.html", "about.html", "caveat.html"]:
        tpl = env.get_template(tname + ".j2")
        html = tpl.render(**context)
        with open(os.path.join("web", tname), "w", encoding="utf-8") as f:
            f.write(html)

    write_sitemap(today)

    if not os.path.exists("web/data/latest.json"):
        with open("web/data/latest.json", "w", encoding="utf-8") as f:
            json.dump(context, f, ensure_ascii=False, indent=2)

    print("build ok", now)


if __name__ == "__main__":
    main()
