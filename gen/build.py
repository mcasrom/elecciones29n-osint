from __future__ import annotations

import json
import os
from datetime import datetime

import pytz
from jinja2 import Environment, FileSystemLoader, select_autoescape

from agg import blackout


TZ = pytz.timezone("Europe/Madrid")


def ensure_dirs() -> None:
    os.makedirs("web/css", exist_ok=True)
    os.makedirs("web/js", exist_ok=True)
    os.makedirs("web/data", exist_ok=True)


def write_css() -> None:
    css = """/* elecciones29n-osint */
:root{--bg:#0f1026;--fg:#e7e7ea;--muted:#b9b9c3;--accent:#ff5a1f;--card:#15162b;--line:#2a2b45}
*{box-sizing:border-box}
body{margin:0;font-family:Inter,system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;background:var(--bg);color:var(--fg);line-height:1.6}
header{padding:24px 16px;border-bottom:1px solid var(--line)}
.container{max-width:1100px;margin:0 auto;padding:0 16px}
h1{margin:0;font-size:28px;letter-spacing:-0.02em}
h2{margin:24px 0 12px;font-size:20px}
.muted{color:var(--muted)}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:16px;margin:16px 0}
.warning{border-left:3px solid var(--accent);padding-left:12px;color:var(--muted)}
.footer{border-top:1px solid var(--line);padding:20px 16px;color:var(--muted);font-size:14px}
table{width:100%;border-collapse:collapse}
th,td{border:1px solid var(--line);padding:8px;text-align:left}
th{background:var(--card);color:var(--muted);font-weight:600}
"""
    with open("web/css/main.css", "w", encoding="utf-8") as f:
        f.write(css)


def write_js() -> None:
    with open("web/js/charts.js", "w", encoding="utf-8") as f:
        f.write("console.log('elecciones29n-osint');\n")


def main() -> None:
    ensure_dirs()
    write_css()
    write_js()

    env = Environment(
        loader=FileSystemLoader("gen/templates"),
        autoescape=select_autoescape(["html", "xml"]),
    )

    # cargar latest
    latest = {"parties": []}
    if os.path.exists("web/data/latest.json"):
        with open("web/data/latest.json", encoding="utf-8") as f:
            latest = json.load(f)

    now = datetime.now(TZ)
    in_blackout = blackout.is_blackout(now)
    context = {
        "updated_at": latest.get("updated_at", now.strftime("%Y-%m-%d %H:%M %Z")),
        "in_blackout": in_blackout,
        "blackout_reason": blackout.blackout_reason(),
        "parties": latest.get("parties", []),
    }

    for tname in ["index.html", "metodologia.html", "fuentes.html", "about.html", "caveat.html"]:
        tpl = env.get_template(tname + ".j2")
        html = tpl.render(**context)
        with open(os.path.join("web", tname), "w", encoding="utf-8") as f:
            f.write(html)

    # asegurar latest existe
    if not os.path.exists("web/data/latest.json"):
        with open("web/data/latest.json", "w", encoding="utf-8") as f:
            json.dump(context, f, ensure_ascii=False, indent=2)

    print("build ok", now)


if __name__ == "__main__":
    main()
