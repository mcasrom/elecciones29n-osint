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
:root{--bg:#0f1026;--fg:#e7e7ea;--muted:#b9b9c3;--accent:#ff5a1f;--card:#15162b;--line:#2a2b45;--ok:#3ddc97}
*{box-sizing:border-box}
body{margin:0;font-family:Inter,system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;background:var(--bg);color:var(--fg);line-height:1.6}
a{color:#8ec5ff}
header{padding:20px 16px;border-bottom:1px solid var(--line)}
.container{max-width:1100px;margin:0 auto;padding:0 16px}
.brand{display:flex;align-items:center;gap:12px;flex-wrap:wrap}
.brand h1{margin:0;font-size:24px;letter-spacing:-0.02em}
.brand .tag{font-size:13px;color:var(--muted)}
nav{margin-top:10px;display:flex;gap:14px;flex-wrap:wrap;font-size:14px}
nav a{color:var(--muted);text-decoration:none}
nav a:hover{color:var(--fg)}
h2{margin:24px 0 12px;font-size:20px}
h3{margin:18px 0 8px;font-size:16px}
.muted{color:var(--muted)}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:16px;margin:16px 0}
.warning{border-left:3px solid var(--accent);padding-left:12px;color:var(--muted)}
.cta{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin-top:10px}
.btn{display:inline-block;padding:9px 14px;border-radius:8px;background:var(--accent);color:#14080a;text-decoration:none;font-weight:600;font-size:14px}
.btn.ghost{background:transparent;border:1px solid var(--line);color:var(--fg);font-weight:500}
.share{display:flex;gap:8px;flex-wrap:wrap;margin-top:8px}
.share a{font-size:13px;padding:6px 10px;border:1px solid var(--line);border-radius:8px;text-decoration:none;color:var(--muted)}
.share a:hover{color:var(--fg);border-color:var(--muted)}
.kpis{display:flex;gap:12px;flex-wrap:wrap;margin:8px 0 0}
.kpi{flex:1 1 160px;background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px}
.kpi b{display:block;font-size:22px}
.kpi span{font-size:13px;color:var(--muted)}
.footer{border-top:1px solid var(--line);padding:20px 16px;color:var(--muted);font-size:14px}
table{width:100%;border-collapse:collapse}
th,td{border:1px solid var(--line);padding:8px;text-align:left}
th{background:var(--card);color:var(--muted);font-weight:600}
tr:hover td{background:#191a30}
svg.chart{width:100%;height:auto;display:block;background:var(--card);border:1px solid var(--line);border-radius:10px}
@media(max-width:600px){.brand h1{font-size:20px}table{font-size:14px}}
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
    return json.dumps([website, dataset], ensure_ascii=False)


def build_chart(series: dict, parties: list) -> str:
    if not series or not parties:
        return ""

    order = [p["party"] for p in parties][:6]
    colors = ["#ff5a1f", "#3ddc97", "#8ec5ff", "#f2c94c", "#bb6bd9", "#56ccf2"]
    dates = sorted({d["date"] for vals in series.values() for d in vals})
    if len(dates) < 2:
        return ""

    W, H = 720, 300
    pad_l, pad_r, pad_t, pad_b = 44, 16, 18, 34
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
        lx = pad_l + 6 + idx * 108
        parts.append(f'<rect x="{lx}" y="{pad_t-2}" width="10" height="10" rx="2" fill="{color}"/>')
        parts.append(f'<text x="{lx+14}" y="{pad_t+7}" fill="#e7e7ea" font-size="11">{party}</text>')
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

    context = {
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
