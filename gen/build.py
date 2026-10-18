from __future__ import annotations

import json
import os
from datetime import datetime

import pytz
from jinja2 import Environment, FileSystemLoader, select_autoescape

from agg import blackout


TZ = pytz.timezone("Europe/Madrid")
OUT = "web"
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
    ("electorado.html", "electorado.html", "2026-10-18", "monthly", "0.7"),
    ("participacion.html", "participacion.html", "2026-10-18", "monthly", "0.7"),
    ("territorio.html", "territorio.html", "2026-10-18", "monthly", "0.7"),
    ("noche-electoral.html", "noche-electoral.html", "2026-10-18", "weekly", "0.7"),
    ("factores.html", "factores.html", "2026-10-18", "monthly", "0.6"),
    ("comportamiento.html", "comportamiento.html", "2026-10-18", "monthly", "0.6"),
    ("apoyo.html", "apoyo.html", "2026-10-18", "yearly", "0.5"),
    ("sobre-mi.html", "sobre-mi.html", "2026-10-18", "yearly", "0.5"),
]


def ensure_dirs() -> None:
    os.makedirs(os.path.join(OUT, "css"), exist_ok=True)
    os.makedirs(os.path.join(OUT, "js"), exist_ok=True)
    os.makedirs(os.path.join(OUT, "data"), exist_ok=True)


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
.themebtn{appearance:none;display:inline-flex;align-items:center;gap:7px;height:34px;padding:0 12px;border:1px solid var(--line);border-radius:999px;background:var(--panel);color:var(--fg);font:inherit;font-size:12.5px;font-weight:650;cursor:pointer;transition:border-color .15s,background .15s}
.themebtn:hover{border-color:var(--muted);background:var(--panel2)}
.themebtn:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.themebtn .ticon{font-size:14px;line-height:1}
.themebtn .tlabel{line-height:1;letter-spacing:.01em}
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
.tab{appearance:none;border:1px solid transparent;background:transparent;color:var(--muted);font:inherit;font-size:15.5px;padding:10px 16px;border-radius:9px;cursor:pointer;text-decoration:none}
.tab:hover{color:var(--fg);background:var(--panel)}
.tab.active{color:var(--bg);background:var(--fg);font-weight:700}
/* nav de páginas */
.mainnav{margin-top:14px;display:flex;flex-direction:column;gap:8px}
.navrow{display:flex;flex-wrap:wrap;align-items:center;gap:8px}
.navrow-primary{gap:6px}
.navpill{padding:8px 15px;border-radius:999px;border:1px solid var(--line);background:var(--panel);color:var(--muted);text-decoration:none;font-size:15.5px;font-weight:600}
.navpill:hover{color:var(--fg);border-color:var(--muted)}
.navpill.active{background:var(--fg);color:var(--bg);border-color:var(--fg)}
.navrow-secondary{gap:16px;font-size:14.5px;border-top:1px solid var(--line);padding-top:9px}
.navrow-secondary a{color:var(--faint);text-decoration:none}
.navrow-secondary a:hover{color:var(--fg)}
.navrow-secondary a.active{color:var(--accent);font-weight:700}
.navdata{border:1px solid var(--line);border-radius:999px;padding:6px 13px;font-size:14px;color:var(--muted)!important}
.navdata:hover{border-color:var(--accent);color:var(--accent)!important}
@media(max-width:760px){
  .navrow-primary{flex-wrap:nowrap;overflow-x:auto;-webkit-overflow-scrolling:touch;padding-bottom:4px}
  .navpill{white-space:nowrap}
  .navrow-secondary{font-size:13.5px;gap:11px}
}
.subnav{display:flex;gap:16px;flex-wrap:wrap;padding:10px 0 0;font-size:14.5px}
.subnav a{color:var(--faint);text-decoration:none}
.subnav a:hover{color:var(--fg)}
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
.tablewrap{overflow-x:auto;-webkit-overflow-scrolling:touch}
table{width:100%;border-collapse:collapse;min-width:520px}
th,td{border-bottom:1px solid var(--line);padding:9px 8px;text-align:left}
th{font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:var(--faint);font-weight:700}
td.num{font-variant-numeric:tabular-nums;text-align:right}
tbody tr:hover td{background:var(--panel2)}

/* chart */
svg.chart{width:100%;height:auto;display:block}
@media(max-width:760px){svg.chart{min-width:560px}}
.chartwrap{overflow-x:auto}

/* calendario */
.cal{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin-top:6px}
.calev{position:relative;background:var(--panel2);border:1px solid var(--line);border-radius:10px;padding:10px 12px 10px 14px}
.calev:before{content:"";position:absolute;left:0;top:10px;bottom:10px;width:3px;border-radius:2px;background:var(--line)}
.calev b{display:block;font-size:13px}
.calev span{display:block;font-size:11.5px;color:var(--muted)}
.calev.done:before{background:var(--accent2)}
.calev.active{border-color:var(--accent)}
.calev.active:before{background:var(--accent)}
.calev.active b{color:var(--accent)}
@media(max-width:760px){.cal{grid-template-columns:repeat(2,minmax(0,1fr))}}

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

/* controles de gráfico */
.chart-controls{display:flex;align-items:center;gap:10px;margin:0 0 10px;font-size:13px;color:var(--muted)}
.chart-controls select{background:var(--panel2);color:var(--fg);border:1px solid var(--line);border-radius:8px;padding:7px 10px;font:inherit}

/* aviso nueva versión (SW) */
.swupdate{position:fixed;left:50%;bottom:18px;transform:translateX(-50%);z-index:85;display:flex;align-items:center;gap:10px;background:var(--panel2);border:1px solid var(--accent);border-radius:12px;padding:10px 14px;box-shadow:0 10px 30px rgba(0,0,0,.35);font-size:13.5px;color:var(--muted);max-width:calc(100vw - 24px)}
.swupdate strong{color:var(--fg)}
.swupdate button{border:1px solid var(--line);background:var(--panel);color:var(--fg);border-radius:8px;padding:6px 10px;font:inherit;font-size:13px;font-weight:600;cursor:pointer}
#swupdate-btn{border-color:var(--accent);color:var(--accent)}
.swupdate #swupdate-close{border:0;background:transparent;color:var(--faint);font-size:18px;padding:0 4px}
@media(max-width:600px){.swupdate{left:12px;right:12px;transform:none;bottom:12px;font-size:12.5px}}

/* salud de la muestra */
.health{display:flex;align-items:center;gap:14px;flex-wrap:wrap}
.healthitems{display:flex;gap:18px;flex-wrap:wrap;font-size:13px;color:var(--muted)}
.healthitems b{display:block;color:var(--fg);font-size:16px;line-height:1.1}
.chip{padding:5px 11px;border-radius:999px;font-size:12px;font-weight:700;border:1px solid}
.chip.ok{color:var(--accent2);border-color:var(--accent2);background:rgba(61,220,151,.10)}
.chip.warn{color:#f2c94c;border-color:#f2c94c;background:rgba(242,201,76,.10)}
.chip.bad{color:var(--accent);border-color:var(--accent);background:rgba(255,90,31,.10)}

/* barras de progreso (censo) */
.prog{display:block;height:8px;background:var(--panel2);border:1px solid var(--line);border-radius:5px;overflow:hidden}
.prog i{display:block;height:100%;background:linear-gradient(90deg,var(--blue),var(--accent2))}

/* apoyo */
.support{display:inline-flex;align-items:center;gap:7px;margin-top:6px;padding:8px 14px;border:1px solid var(--line);border-radius:999px;background:var(--panel2);color:var(--fg);text-decoration:none;font-size:13.5px;font-weight:600}
.support:hover{border-color:var(--accent);color:var(--accent)}

/* ayuda */
.helpopen{appearance:none;border:1px solid var(--line);background:var(--panel);color:var(--muted);border-radius:999px;padding:6px 12px;font:inherit;font-size:13px;font-weight:700;cursor:pointer}
.helpopen:hover{border-color:var(--accent);color:var(--accent)}
.helpintro{display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap;background:var(--panel2);border:1px solid var(--line);border-left:3px solid var(--accent);border-radius:10px;padding:12px 14px;margin:16px 0;font-size:14px;color:var(--muted)}
.helpintro-actions{display:flex;align-items:center;gap:8px}
.helpintro-off{appearance:none;border:0;background:transparent;color:var(--faint);font-size:20px;line-height:1;cursor:pointer;padding:4px 8px}
.helpintro-off:hover{color:var(--fg)}
.helpbackdrop{position:fixed;inset:0;z-index:90;background:rgba(0,0,0,.55)}
.helppanel{position:fixed;top:0;right:0;bottom:0;z-index:100;width:min(430px,94vw);background:var(--panel);border-left:1px solid var(--line);padding:22px;overflow:auto;box-shadow:-20px 0 50px rgba(0,0,0,.45)}
.helphead{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:8px}
.helphead h2{font-size:19px;margin:0}
.helpclose{appearance:none;border:1px solid var(--line);background:var(--panel2);color:var(--fg);width:34px;height:34px;border-radius:9px;font-size:20px;line-height:1;cursor:pointer}
.helpsteps{margin:8px 0 16px;padding-left:18px;color:var(--muted);font-size:14.5px}
.helpsteps li{margin:10px 0}
.helpsteps strong{color:var(--fg)}
.eco{margin-top:8px}
.eco a{color:var(--faint)}
.eco a:hover{color:var(--fg)}


/* footer */
.footer{border-top:1px solid var(--line);padding:24px 0;color:var(--faint);font-size:13.5px;margin-top:24px}
.footer p{margin:4px 0}

@media (prefers-reduced-motion: reduce){
  .dot,.stale{animation:none}
  *{scroll-behavior:auto}
}

details{border:1px solid var(--line);border-radius:10px;padding:10px 12px;margin:8px 0;background:var(--panel2)}
summary{cursor:pointer;font-size:14px}
summary::-webkit-details-marker{display:none}

@media(max-width:760px){
  .hero-kpis,.kpis{grid-template-columns:repeat(2,minmax(0,1fr))}
  .tab{padding:8px 11px;font-size:13px}
  .blocks{grid-template-columns:1fr}
  .seatrow{grid-template-columns:76px 1fr 40px}
}
"""
    with open(os.path.join(OUT, "css/main.css"), "w", encoding="utf-8") as f:
        f.write(css)


def write_js() -> None:
    with open(os.path.join(OUT, "js/charts.js"), "w", encoding="utf-8") as f:
        f.write("/* charts inline; no external deps */\n")


def write_cambios() -> None:
    """RSS 2.0 con un item por sondeo nuevo (fecha + encuestadora)."""
    import csv as _csv
    from email.utils import format_datetime
    from xml.sax.saxutils import escape

    hist = "data/polls_history.csv"
    groups: dict = {}
    if os.path.exists(hist):
        with open(hist, encoding="utf-8", newline="") as f:
            for row in _csv.DictReader(f):
                if (row.get("kind") or "tracking") == "average":
                    continue
                key = (row.get("date") or "", row.get("pollster") or "Electomania")
                g = groups.setdefault(key, {"url": row.get("source_url") or "", "vals": {}})
                try:
                    g["vals"][row["party"]] = float(row["value"])
                except Exception:
                    continue

    items = []
    for (d, pollster), g in sorted(groups.items(), reverse=True)[:60]:
        top = sorted(g["vals"].items(), key=lambda kv: -kv[1])[:5]
        desc = " · ".join(f"{k} {v:.1f}%" for k, v in top)
        try:
            dt = TZ.localize(datetime.strptime(d, "%Y-%m-%d").replace(hour=8))
        except Exception:
            continue
        url = g["url"] or f"{SITE_URL}/"
        title = f"Nuevo sondeo · {pollster} · {d[8:10]}/{d[5:7]}"
        items.append(
            "  <item>"
            f"<title>{escape(title)}</title>"
            f"<link>{escape(url)}</link>"
            f"<guid isPermaLink=\"false\">{escape(d + '-' + pollster)}</guid>"
            f"<pubDate>{format_datetime(dt)}</pubDate>"
            f"<description>{escape(desc + '. Media agregada, no pronóstico.')}</description>"
            "</item>"
        )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0"><channel>'
        f"<title>{escape(SITE_TITLE)} · cambios</title>"
        f"<link>{SITE_URL}/</link>"
        f"<description>{escape(SITE_DESC)}</description>"
        f"<language>es-ES</language>"
        + ("\n" + "\n".join(items) if items else "")
        + "\n</channel></rss>\n"
    )
    with open(os.path.join(OUT, "cambios.xml"), "w", encoding="utf-8") as f:
        f.write(xml)


def write_manifest(version: str = "0.0.0") -> None:
    data = {
        "name": "Observatorio electoral 29N",
        "short_name": "29N",
        "description": SITE_DESC,
        "start_url": "/",
        "scope": "/",
        "display": "standalone",
        "background_color": "#0b0c1c",
        "theme_color": "#ff5a1f",
        "lang": "es-ES",
        "version": version,
        "icons": [
            {"src": "/icons/icon-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "/icons/icon-512.png", "sizes": "512x512", "type": "image/png"},
            {"src": "/icons/icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
        ],
    }
    with open(os.path.join(OUT, "manifest.webmanifest"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def write_version_json(version: str, build_ts: str, build_date: str, commit: str) -> None:
    data = {"version": version, "build": build_ts, "date": build_date, "commit": commit}
    with open(os.path.join(OUT, "version.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def write_sw(build_ts: str) -> None:
    js = f"""const CACHE = 'e29n-{build_ts}';
const ASSETS = ['/', '/css/main.css', '/js/charts.js', '/favicon.svg', '/og.png', '/manifest.webmanifest'];
self.addEventListener('install', e => {{
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(ASSETS)));
}});
self.addEventListener('message', e => {{
  if (e.data && e.data.type === 'SKIP_WAITING') self.skipWaiting();
}});
self.addEventListener('activate', e => {{
  e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim()));
}});
self.addEventListener('fetch', e => {{
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== location.origin) return;
  if (req.mode === 'navigate' || url.pathname.startsWith('/data/') || url.pathname.endsWith('.json')) {{
    e.respondWith(fetch(req).then(r => {{ const c = r.clone(); caches.open(CACHE).then(x => x.put(req, c)); return r; }})
      .catch(() => caches.match(req).then(r => r || caches.match('/'))));
    return;
  }}
  e.respondWith(caches.match(req).then(r => r || fetch(req).then(res => {{
    const c = res.clone(); caches.open(CACHE).then(x => x.put(req, c)); return res;
  }})));
}});
"""
    with open(os.path.join(OUT, "sw.js"), "w", encoding="utf-8") as f:
        f.write(js)


def write_robots() -> None:
    robots = (
        "User-agent: *\n"
        "Allow: /\n"
        f"\nSitemap: {SITE_URL}/sitemap.xml\n"
    )
    with open(os.path.join(OUT, "robots.txt"), "w", encoding="utf-8") as f:
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
    with open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(xml)


def write_indexnow_key() -> None:
    with open(os.path.join(OUT, f"{INDEXNOW_KEY}.txt"), "w", encoding="utf-8") as f:
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

## Contacto
- info.elecciones29n@pruebapublica.com

## Cita
Miguel Castillo. {SITE_NAME}: media agregada de sondeos, elecciones
generales 29N 2026. {SITE_URL}
"""
    with open(os.path.join(OUT, "llms.txt"), "w", encoding="utf-8") as f:
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
    with open(os.path.join(OUT, "favicon.svg"), "w", encoding="utf-8") as f:
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


def fmt_miles(n) -> str:
    try:
        return f"{int(n):,}".replace(",", ".")
    except Exception:
        return str(n)


def build_age_chart(edad: list) -> str:
    if not edad:
        return ""
    W, row_h, pad_l, pad_r, pad_t = 760, 30, 104, 78, 34
    H = pad_t + row_h * len(edad) + 8
    vmax = max((e["total"] for e in edad), default=1) or 1
    scale = (W - pad_l - pad_r) / vmax
    parts = [
        f'<svg class="chart" viewBox="0 0 {W} {H}" role="img" aria-label="Electores por edad y sexo">',
        f'<rect x="{pad_l}" y="6" width="10" height="10" rx="2" fill="#8ec5ff"/>',
        f'<text x="{pad_l+16}" y="15" fill="var(--muted)" font-size="11">Mujeres</text>',
        f'<rect x="{pad_l+90}" y="6" width="10" height="10" rx="2" fill="#ff5a1f"/>',
        f'<text x="{pad_l+106}" y="15" fill="var(--muted)" font-size="11">Hombres</text>',
    ]
    for i, e in enumerate(edad):
        y = pad_t + i * row_h
        wm = e["mujeres"] * scale
        wh = e["hombres"] * scale
        parts.append(f'<text x="{pad_l-8}" y="{y+13}" text-anchor="end" fill="var(--muted)" font-size="11">{e["grupo"]}</text>')
        parts.append(f'<rect x="{pad_l}" y="{y+3}" width="{wm:.1f}" height="16" fill="#8ec5ff"/>')
        parts.append(f'<rect x="{pad_l+wm:.1f}" y="{y+3}" width="{wh:.1f}" height="16" fill="#ff5a1f"/>')
        parts.append(f'<text x="{pad_l+wm+wh+8:.1f}" y="{y+16}" fill="var(--muted)" font-size="11">{fmt_miles(e["total"])}</text>')
    parts.append("</svg>")
    return "".join(parts)


def build_cera_chart(paises: list) -> str:
    if not paises:
        return ""
    W, row_h, pad_l, pad_r, pad_t = 760, 28, 186, 76, 10
    H = pad_t + row_h * len(paises) + 6
    vmax = max((p["electores"] for p in paises), default=1) or 1
    scale = (W - pad_l - pad_r) / vmax
    parts = [f'<svg class="chart" viewBox="0 0 {W} {H}" role="img" aria-label="Residentes en el extranjero por país">']
    for i, p in enumerate(paises):
        y = pad_t + i * row_h
        w = p["electores"] * scale
        parts.append(f'<text x="{pad_l-8}" y="{y+14}" text-anchor="end" fill="var(--muted)" font-size="11">{p["pais"][:26]}</text>')
        parts.append(f'<rect x="{pad_l}" y="{y+4}" width="{w:.1f}" height="15" rx="3" fill="#3ddc97" opacity="0.85"/>')
        parts.append(f'<text x="{pad_l+w+8:.1f}" y="{y+16}" fill="var(--muted)" font-size="11">{fmt_miles(p["electores"])}</text>')
    parts.append("</svg>")
    return "".join(parts)


def fmt_pct(v) -> str:
    try:
        return f"{float(v):.2f}".replace(".", ",")
    except Exception:
        return str(v)


def build_resultados_2023(n: dict) -> list:
    votes = n.get("votos", {})
    seats = n.get("escanos", {})
    if not votes or not seats:
        return []
    vtot = sum(votes.values()) or 1
    stot = sum(seats.values()) or 1
    rows = []
    for party in sorted(set(votes) | set(seats), key=lambda k: -seats.get(k, 0)):
        v = votes.get(party, 0)
        e = seats.get(party, 0)
        vp = 100.0 * v / vtot
        ep = 100.0 * e / stot
        rows.append({
            "party": party, "votes": v, "seats": e,
            "vote_pct": round(vp, 2), "seat_pct": round(ep, 2),
            "diff": round(ep - vp, 2),
        })
    return rows


def build_escanos_chart(provincias: list) -> str:
    if not provincias:
        return ""
    rows = sorted(provincias, key=lambda p: p["electores_por_escanos"])
    W, row_h, pad_l, pad_r, pad_t = 760, 13, 132, 78, 12
    H = pad_t + row_h * len(rows) + 6
    vmax = max(p["electores_por_escanos"] for p in rows) or 1
    scale = (W - pad_l - pad_r) / vmax
    parts = [f'<svg class="chart" viewBox="0 0 {W} {H}" role="img" aria-label="Electores por escaño en cada provincia">']
    for i, p in enumerate(rows):
        y = pad_t + i * row_h
        w = p["electores_por_escanos"] * scale
        color = "#ff5a1f" if p["nombre"] in ("Madrid", "Barcelona") else ("#3ddc97" if p["nombre"] in ("Teruel", "Soria") else "#8ec5ff")
        parts.append(f'<text x="{pad_l-6}" y="{y+10}" text-anchor="end" fill="var(--muted)" font-size="9.5">{p["nombre"][:20]}</text>')
        parts.append(f'<rect x="{pad_l}" y="{y+1}" width="{w:.1f}" height="9" rx="2" fill="{color}" opacity="0.85"/>')
        parts.append(f'<text x="{pad_l+w+5:.1f}" y="{y+10}" fill="var(--muted)" font-size="9">{fmt_miles(p["electores_por_escanos"])}</text>')
    parts.append("</svg>")
    return "".join(parts)


def build_participacion_chart(rows: list) -> str:
    if len(rows) < 2:
        return ""
    W, H = 760, 320
    pad_l, pad_r, pad_t, pad_b = 46, 20, 22, 40
    iw, ih = W - pad_l - pad_r, H - pad_t - pad_b
    vmin, vmax = 60.0, 82.0

    def x(i):
        return pad_l + iw * i / (len(rows) - 1)

    def y(v):
        return pad_t + ih * (1 - (v - vmin) / (vmax - vmin))

    parts = [f'<svg class="chart" viewBox="0 0 {W} {H}" role="img" aria-label="Participación en las elecciones generales">']
    for g in range(5):
        val = vmin + (vmax - vmin) * g / 4
        yy = y(val)
        parts.append(f'<line x1="{pad_l}" y1="{yy:.1f}" x2="{W-pad_r}" y2="{yy:.1f}" stroke="var(--line)" stroke-width="1"/>')
        parts.append(f'<text x="6" y="{yy+4:.1f}" fill="var(--muted)" font-size="11">{val:.0f}%</text>')
    coords = [(x(i), y(r["participacion"])) for i, r in enumerate(rows)]
    dpath = "M " + " L ".join(f"{cx:.1f},{cy:.1f}" for cx, cy in coords)
    parts.append(f'<path d="{dpath}" fill="none" stroke="#ff5a1f" stroke-width="2.2"/>')
    parts.append("".join(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="3.2" fill="#ff5a1f"/>' for cx, cy in coords))
    for i, r in enumerate(rows):
        lbl = r["eleccion"]
        if lbl.startswith("2019 ("):
            lbl = "2019a" if "abr" in lbl else "2019n"
        parts.append(f'<text x="{x(i):.1f}" y="{H-12}" fill="var(--muted)" font-size="10" text-anchor="middle">{lbl}</text>')
    # etiquetas: primero, último, mínimo y máximo
    labelled = {0, len(rows) - 1}
    imax = max(range(len(rows)), key=lambda i: rows[i]["participacion"])
    imin = min(range(len(rows)), key=lambda i: rows[i]["participacion"])
    labelled |= {imax, imin}
    for i in sorted(labelled):
        cx, cy = coords[i]
        dy = -8 if i not in (imin,) else 16
        parts.append(f'<text x="{cx:.1f}" y="{cy+dy:.1f}" fill="var(--fg)" font-size="11" text-anchor="middle">{fmt_pct(rows[i]["participacion"])}%</text>')
    parts.append("</svg>")
    return "".join(parts)


def build_sparklines(series: dict, parties: list) -> str:
    """Minigráficos por partido (serie larga) para la pestaña Evolución."""
    order = [p["party"] for p in parties][:6]
    panels = []
    for party in order:
        pts = series.get(party, [])
        if not pts:
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
        color = CHART_COLORS[order.index(party) % len(CHART_COLORS)]
        if len(pts) == 1:
            coords = [(W / 2, Y(pts[0]["value"]))]
        lo_pts, hi_pts = [], []
        for i in range(len(pts)):
            win = vals[max(0, i - 1):i + 2]
            lo_pts.append((X(i), Y(min(win))))
            hi_pts.append((X(i), Y(max(win))))
        band = _band(lo_pts, hi_pts) if len(pts) >= 2 else ""
        d = "M " + " L ".join(f"{cx:.1f},{cy:.1f}" for cx, cy in coords)
        delta = vals[-1] - vals[0]
        cls = "up" if delta > 0.05 else ("down" if delta < -0.05 else "flat")
        sign = "+" if delta > 0 else ""
        dots = "".join(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="2.4" fill="{color}"/>' for cx, cy in coords)
        panels.append(
            f'<div class="spark">'
            f'<div class="sparkhead"><span>{party}</span><b>{vals[-1]:.1f}%</b></div>'
            f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Evolución de {party}">'
            f'<path d="{band}" fill="{color}" opacity="0.18" stroke="none"/>'
            f'<path d="{d}" fill="none" stroke="{color}" stroke-width="2"/>{dots}</svg>'
            f'<div class="sparkfoot"><span>{pts[0]["date"][5:].replace("-", "/")}</span>'
            f'<span class="delta {cls}">{sign}{delta:.1f} pts</span>'
            f'<span>{pts[-1]["date"][5:].replace("-", "/")}</span></div>'
            f"</div>"
        )
    return '<div class="sparks">' + "".join(panels) + "</div>" if panels else ""


def write_censo_data(censo: dict) -> None:
    import csv as _csv

    if not censo:
        return
    data_dir = os.path.join(OUT, "data")
    os.makedirs(data_dir, exist_ok=True)
    with open(os.path.join(data_dir, "censo-2026.json"), "w", encoding="utf-8") as f:
        json.dump(censo, f, ensure_ascii=False, indent=2)

    def dump(name, keys, rows):
        with open(os.path.join(data_dir, name), "w", encoding="utf-8", newline="") as f:
            w = _csv.writer(f)
            w.writerow(keys)
            for r in rows:
                w.writerow([r.get(k, "") for k in keys])

    dump("censo-provincias.csv", ["codigo", "nombre", "cer", "cera", "total"], censo.get("provincias", []))
    dump("censo-edad.csv", ["grupo", "mujeres", "hombres", "total"], censo.get("edad_sexo", []))
    dump("censo-nuevos.csv", ["codigo", "nombre", "desde_2023", "desde_2024"], censo.get("nuevos_provincia", []))
    dump("censo-cera.csv", ["codigo", "pais", "electores"], censo.get("cera_paises", []))


def write_congreso_web(prov_part: dict, congreso: dict) -> None:
    if not prov_part:
        return
    data_dir = os.path.join(OUT, "data")
    os.makedirs(data_dir, exist_ok=True)
    with open(os.path.join(data_dir, "participacion-provincial.json"), "w", encoding="utf-8") as f:
        json.dump(prov_part, f, ensure_ascii=False, indent=2)
    n = congreso.get("elecciones", {}).get("2023-07-23", {}).get("nacional", {})
    rows = build_resultados_2023(n)
    if rows:
        import csv as _csv
        with open(os.path.join(data_dir, "resultados-2023.csv"), "w", encoding="utf-8", newline="") as f:
            w = _csv.writer(f)
            w.writerow(["partido", "votos", "pct_voto", "escanos", "pct_escanos", "diferencia_pp"])
            for r in rows:
                w.writerow([r["party"], r["votes"], r["vote_pct"], r["seats"], r["seat_pct"], r["diff"]])
        with open(os.path.join(data_dir, "resultados-2023.json"), "w", encoding="utf-8") as f:
            json.dump({"nacional": n, "filas": rows}, f, ensure_ascii=False, indent=2)


def write_resultados_data(data: dict) -> None:
    if not data:
        return
    os.makedirs(os.path.join(OUT, "data"), exist_ok=True)
    with open(os.path.join(OUT, "data", "resultados-29n.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def write_escanos_data(data: dict) -> None:
    import csv as _csv

    rows = data.get("provincias", [])
    if not rows:
        return
    os.makedirs(os.path.join(OUT, "data"), exist_ok=True)
    with open(os.path.join(OUT, "data", "escanos-2026.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    with open(os.path.join(OUT, "data", "escanos-2026.csv"), "w", encoding="utf-8", newline="") as f:
        w = _csv.writer(f)
        w.writerow(["provincia", "escanos", "electores", "electores_por_escanos"])
        for r in rows:
            w.writerow([r["nombre"], r["escanos"], r["electores"], r["electores_por_escanos"]])


def write_participacion_data(data: dict) -> None:
    import csv as _csv

    rows = data.get("elecciones", [])
    if not rows:
        return
    os.makedirs(os.path.join(OUT, "data"), exist_ok=True)
    with open(os.path.join(OUT, "data", "participacion.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    with open(os.path.join(OUT, "data", "participacion.csv"), "w", encoding="utf-8", newline="") as f:
        w = _csv.writer(f)
        w.writerow(["eleccion", "year", "participacion", "fuente_url"])
        for r in rows:
            w.writerow([r["eleccion"], r["year"], r["participacion"], r["fuente_url"]])


def build_person_jsonld() -> str:
    data = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": "Miguel Castillo",
        "url": SITE_URL + "/sobre-mi.html",
        "jobTitle": "Analista y desarrollador de datos abiertos",
        "description": "Autor del observatorio electoral 29N, del observatorio de amplificación (FIMI) y de otros proyectos de datos abiertos.",
        "email": "mailto:info.elecciones29n@pruebapublica.com",
        "sameAs": [
            "https://github.com/mcasrom",
            "https://mastodon.social/@viajeinteligencia",
            "https://bsky.app/profile/viajeinteligencia.bsky.social",
            "https://analisis.pruebapublica.com/",
        ],
    }
    return json.dumps(data, ensure_ascii=False)


def build_censo_jsonld(censo: dict) -> str:
    if not censo:
        return "[]"
    data = {
        "@context": "https://schema.org",
        "@type": "Dataset",
        "name": "Censo electoral · Elecciones Generales 29N 2026",
        "description": "Censo electoral de las elecciones generales del 29 de noviembre de 2026 por provincia, comunidad autónoma, sexo y grupo de edad, y residentes en el extranjero por país.",
        "url": SITE_URL + "/electorado.html",
        "creator": {"@type": "Person", "name": "Miguel Castillo", "url": SITE_URL},
        "license": "https://www.gnu.org/licenses/agpl-3.0.html",
        "isAccessibleForFree": True,
        "dateModified": censo.get("meta", {}).get("descargado", ""),
        "spatialCoverage": "ES",
        "temporalCoverage": "2026",
        "sourceOrganization": {"@type": "Organization", "name": "INE · Oficina del Censo Electoral"},
        "distribution": [
            {"@type": "DataDownload", "contentUrl": SITE_URL + "/data/censo-2026.json", "encodingFormat": "application/json"},
            {"@type": "DataDownload", "contentUrl": SITE_URL + "/data/censo-provincias.csv", "encodingFormat": "text/csv"},
            {"@type": "DataDownload", "contentUrl": SITE_URL + "/data/censo-edad.csv", "encodingFormat": "text/csv"},
        ],
    }
    return json.dumps(data, ensure_ascii=False)


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


def _band(coords_lo, coords_hi) -> str:
    top = " L ".join(f"{x:.1f},{y:.1f}" for x, y in coords_hi)
    bot = " L ".join(f"{x:.1f},{y:.1f}" for x, y in reversed(coords_lo))
    return f"M {top} L {bot} Z"


def chart_legend(parties: list) -> list:
    return [
        {"party": p["party"], "color": CHART_COLORS[i % len(CHART_COLORS)]}
        for i, p in enumerate(parties[:6])
    ]


def _empty_chart() -> str:
    return (
        '<svg class="chart" viewBox="0 0 760 320" role="img" '
        'aria-label="Sin datos suficientes"><text x="380" y="160" '
        'text-anchor="middle" fill="var(--muted)" font-size="14">'
        "Sin datos suficientes para dibujar la serie</text></svg>"
    )


def build_chart(series: dict, parties: list) -> str:
    if not series or not parties:
        return _empty_chart()

    order = [p["party"] for p in parties][:6]
    colors = CHART_COLORS
    dates = sorted({d["date"] for vals in series.values() for d in vals})
    if not dates:
        return _empty_chart()

    W, H = 760, 320
    pad_l, pad_r, pad_t, pad_b = 52, 18, 20, 40
    iw, ih = W - pad_l - pad_r, H - pad_t - pad_b

    vals_all = [d["value"] for p in order for d in series.get(p, [])]
    vmin = max(0, min(vals_all) - 2)
    vmax = max(vals_all) + 2

    def x(i: int) -> float:
        if len(dates) == 1:
            return pad_l + iw / 2
        return pad_l + (iw * i / (len(dates) - 1))

    def y(v: float) -> float:
        return pad_t + ih * (1 - (v - vmin) / (vmax - vmin))

    parts = [f'<svg class="chart" viewBox="0 0 {W} {H}" role="img" aria-label="Evolución de la media por partido">']
    for g in range(5):
        val = vmin + (vmax - vmin) * g / 4
        yy = y(val)
        parts.append(f'<line x1="{pad_l}" y1="{yy:.1f}" x2="{W-pad_r}" y2="{yy:.1f}" stroke="var(--line)" stroke-width="1"/>')
        parts.append(f'<text x="6" y="{yy+4:.1f}" fill="var(--muted)" font-size="11">{val:.0f}%</text>')
    for i, d in enumerate(dates):
        lbl = d[8:10] + "/" + d[5:7]
        parts.append(f'<text x="{x(i):.1f}" y="{H-10}" fill="var(--muted)" font-size="10" text-anchor="middle">{lbl}</text>')
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
        if idx < 3 and len(pts) >= 3:
            vals = [p["value"] for p in pts]
            lo = [(x(i), y(min(vals[max(0, i - 1):i + 2]))) for i in range(len(pts))]
            hi = [(x(i), y(max(vals[max(0, i - 1):i + 2]))) for i in range(len(pts))]
            parts.append(f'<path d="{_band(lo, hi)}" fill="{color}" opacity="0.10" stroke="none"/>')
        parts.append(f'<path d="{dpath}" fill="none" stroke="{color}" stroke-width="2.2"/>')
        for cx, cy in coords:
            parts.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="3" fill="{color}"/>')
    parts.append(f'<text x="12" y="{pad_t+4}" fill="currentColor" opacity="0.55" font-size="10">% voto</text>')
    parts.append("</svg>")
    return "".join(parts)


def main(out: str = "web") -> None:
    global OUT
    OUT = out
    build_ts = datetime.now(TZ).strftime("%Y%m%d%H%M")
    build_date = datetime.now(TZ).strftime("%Y-%m-%d")
    version = "0.0.0"
    if os.path.exists("VERSION"):
        version = open("VERSION", encoding="utf-8").read().strip() or version
    try:
        import subprocess
        build_commit = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        build_commit = "dev"
    ensure_dirs()
    write_css()
    write_js()
    write_robots()
    write_cambios()
    write_indexnow_key()
    write_llms()
    write_favicon()
    write_manifest(version)
    write_sw(build_ts)
    write_version_json(version, build_ts, build_date, build_commit)

    env = Environment(
        loader=FileSystemLoader("gen/templates"),
        autoescape=select_autoescape(["html", "xml"]),
    )

    congreso = {}
    if os.path.exists("data/congreso.json"):
        with open("data/congreso.json", encoding="utf-8") as f:
            congreso = json.load(f)
    prov_part = {}
    if os.path.exists("data/participacion_provincial.json"):
        with open("data/participacion_provincial.json", encoding="utf-8") as f:
            prov_part = json.load(f)

    resultados = {}
    if os.path.exists("data/resultados_29n.json"):
        with open("data/resultados_29n.json", encoding="utf-8") as f:
            resultados = json.load(f)

    escanos = {"provincias": [], "total_escanos": 0}
    if os.path.exists("data/escanos_2026.json"):
        with open("data/escanos_2026.json", encoding="utf-8") as f:
            escanos = json.load(f)

    participacion = {"elecciones": []}
    if os.path.exists("data/participacion.json"):
        with open("data/participacion.json", encoding="utf-8") as f:
            participacion = json.load(f)
    els = participacion.get("elecciones", [])
    part_kpis = {
        "ultima": els[-1] if els else None,
        "media": round(sum(r["participacion"] for r in els) / len(els), 2) if els else None,
        "max": max(els, key=lambda r: r["participacion"]) if els else None,
        "min": min(els, key=lambda r: r["participacion"]) if els else None,
        "n": len(els),
    }

    censo = {}
    if os.path.exists("data/censo_2026.json"):
        with open("data/censo_2026.json", encoding="utf-8") as f:
            censo = json.load(f)

    latest = {"parties": []}
    if os.path.exists(os.path.join(OUT, "data/latest.json")):
        with open(os.path.join(OUT, "data/latest.json"), encoding="utf-8") as f:
            latest = json.load(f)

    now = datetime.now(TZ)
    today = now.strftime("%Y-%m-%d")

    campaign = now.replace(year=2026, month=11, day=13, hour=0, minute=0, second=0, microsecond=0)
    blackout_dt = now.replace(year=2026, month=11, day=24, hour=0, minute=0, second=0, microsecond=0)
    election_dt = now.replace(year=2026, month=11, day=29, hour=0, minute=0, second=0, microsecond=0)
    if now < campaign:
        phase, next_ms = "precampaña", "Campaña · 13 nov"
    elif now < blackout_dt:
        phase, next_ms = "campaña", "Blackout de sondeos · 24 nov"
    elif now < election_dt:
        phase, next_ms = "blackout", "Jornada electoral · 29 nov"
    else:
        phase, next_ms = "postelectoral", "—"
    calendar = [
        {"date": "6 oct", "label": "Convocatoria (BOE)", "state": "done"},
        {"date": "13–27 nov", "label": "Campaña electoral",
         "state": "done" if now >= blackout_dt else "active"},
        {"date": "24–28 nov", "label": "Prohibición de sondeos",
         "state": "done" if now >= election_dt else ("active" if now >= blackout_dt else "")},
        {"date": "29 nov", "label": "Jornada electoral",
         "state": "active" if now >= election_dt else ""},
    ]
    in_blackout = blackout.is_blackout(now)
    parties = latest.get("parties", [])
    series = latest.get("series", {})

    build_ts = now.strftime("%Y%m%d%H%M")
    context = {
        "build_ts": build_ts,
        "build_date": build_date,
        "version": version,
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
        "chart_svg": build_chart(latest.get("series_long", series), parties),
        "chart_legend": chart_legend(parties),
        "censo_jsonld": build_censo_jsonld(censo),
        "person_jsonld": build_person_jsonld(),
        "sparks_svg": build_sparklines(latest.get("series_long", series), parties),
        "series_span": (
            f'{next(iter(latest.get("series_long", {}).values()))[0]["date"]} – '
            f'{next(iter(latest.get("series_long", {}).values()))[-1]["date"]}'
            if latest.get("series_long") else ""
        ),
        "updated_iso": latest.get("updated_at_iso", now.isoformat()),
        "low_n": latest.get("low_n", False),
        "window_span": latest.get("window_span", ""),
        "window_extended": latest.get("window_extended", False),
        "weight_basis": latest.get("weight_basis", ""),
        "phase": phase,
        "next_milestone": next_ms,
        "calendar": calendar,
        "censo": censo,
        "age_svg": build_age_chart(censo.get("edad_sexo", [])),
        "cera_svg": build_cera_chart(censo.get("cera_paises", [])[:10]),
        "fmt_miles": fmt_miles,
        "fmt_pct": fmt_pct,
        "participacion": participacion,
        "part_chart": build_participacion_chart(participacion.get("elecciones", [])),
        "part_kpis": part_kpis,
        "health": latest.get("health", {}),
        "escanos": escanos,
        "resultados": resultados,
        "congreso": congreso,
        "prov_part": prov_part,
        "congreso_2023": congreso.get("elecciones", {}).get("2023-07-23", {}),
        "resultados_2023_rows": build_resultados_2023(
            congreso.get("elecciones", {}).get("2023-07-23", {}).get("nacional", {})
        ),
        "prov_2023": (prov_part.get("elecciones", {}).get("2023-07-23", {}).get("provincias", [])),
        "escanos_chart": build_escanos_chart(escanos.get("provincias", [])),
        "escanos_kpis": {
            "total": escanos.get("total_escanos", 0),
            "n": len(escanos.get("provincias", [])),
            "media": round(sum(p["electores"] for p in escanos.get("provincias", [])) / max(1, escanos.get("total_escanos", 1)), 0),
            "min": min(escanos.get("provincias", []), key=lambda p: p["electores_por_escanos"]) if escanos.get("provincias") else None,
            "max": max(escanos.get("provincias", []), key=lambda p: p["electores_por_escanos"]) if escanos.get("provincias") else None,
        },
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

    for tname in ["index.html", "metodologia.html", "fuentes.html", "about.html", "caveat.html", "electorado.html", "participacion.html", "territorio.html",
             "apoyo.html", "sobre-mi.html", "noche-electoral.html", "factores.html", "comportamiento.html"]:
        tpl = env.get_template(tname + ".j2")
        html = tpl.render(current=tname, **context)
        with open(os.path.join(OUT, tname), "w", encoding="utf-8") as f:
            f.write(html)

    write_sitemap(today)
    write_censo_data(censo)
    write_participacion_data(participacion)
    write_escanos_data(escanos)
    write_resultados_data(resultados)
    write_congreso_web(prov_part, congreso)

    if not os.path.exists(os.path.join(OUT, "data/latest.json")):
        with open(os.path.join(OUT, "data/latest.json"), "w", encoding="utf-8") as f:
            json.dump(context, f, ensure_ascii=False, indent=2)

    print("build ok", now)


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="web")
    a = ap.parse_args()
    main(a.out)
