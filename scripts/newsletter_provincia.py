#!/usr/bin/env python3
"""Resumen semanal 29N con bloque provincial, a partir de la página de alta.

No guarda una provincia nueva: usa `page` (/circunscripcion/<slug>.html).
Uso:
  python3 scripts/newsletter_provincia.py --dry
  python3 scripts/newsletter_provincia.py --test tu@email --province madrid
  python3 scripts/newsletter_provincia.py --send [--limit 50]
"""
from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from agg import blackout  # noqa: E402
from gen import circunscripciones  # noqa: E402

TZ = ZoneInfo("Europe/Madrid")
DB = ROOT / "data" / "subs.db"
LATEST = ROOT / "web" / "data" / "latest.json"
ENV = Path("/home/deploy/newsletter/.env")
BASE = "https://elecciones29n.pruebapublica.com"
FROM_DEFAULT = "Observatorio 29N <newsletter@viajeinteligencia.com>"
REPLY = "info.elecciones29n@pruebapublica.com"


def load_env(path=ENV):
    d = {}
    try:
        for ln in path.read_text(encoding="utf-8").splitlines():
            ln = ln.strip()
            if ln and not ln.startswith("#") and "=" in ln:
                k, _, v = ln.partition("=")
                d[k.strip()] = v.strip().strip('"').strip("'")
    except OSError:
        pass
    return d


def fmt_pct(v):
    if v is None:
        return "—"
    return f"{v:.2f}".replace(".", ",")


def fmt_int(v):
    if v is None:
        return "—"
    return f"{int(v):,}".replace(",", ".")


def load_provinces():
    oficial = json.loads((ROOT / "data/congreso-oficial.json").read_text(encoding="utf-8"))
    escanos = json.loads((ROOT / "data/escanos_2026.json").read_text(encoding="utf-8"))
    censo = {}
    p = ROOT / "data/censo_2026.json"
    if p.exists():
        censo = json.loads(p.read_text(encoding="utf-8"))
    return {x["slug"]: x for x in circunscripciones.build_pages(oficial, escanos, censo)}


def province_block(slug, prov):
    if not slug or not prov:
        return "", ""
    p = prov.get(slug)
    if not p:
        return "", ""
    res = (p.get("resultados") or [{}])[0]
    cands = sorted(res.get("candidaturas") or [], key=lambda c: -c.get("votos", 0))[:2]
    top = " · ".join(f"{c.get('acronimo')} {c.get('escanos', 0)}" for c in cands)
    mar = (p.get("marginales") or {}).get("2023-07-23") or {}
    last = ""
    if mar.get("ultimo"):
        label = (mar["ultimo"].get("etiqueta") or "").split(" - ")[-1]
        if mar.get("margen_votos") is not None:
            last = f"Último escaño 2023: {label} por {fmt_int(mar.get('margen_votos'))} votos."
        else:
            last = f"Último escaño 2023: {label}."
    html = f'''<h2 style="font-size:20px;margin:26px 0 8px">Tu provincia: {p['nombre']}</h2>
<p style="font-size:15px;line-height:1.6;margin:0 0 8px"><strong>{p.get('escanos_2026')} diputados</strong> · {fmt_int(p.get('electores_2026'))} electores · participación 2023: {fmt_pct(p.get('participacion_2023'))}%.</p>
<p style="font-size:15px;line-height:1.6;margin:0 0 8px">Resultado 2023: <strong>{top}</strong>.</p>
<p style="font-size:14px;line-height:1.6;color:#59636e;margin:0 0 8px">{last}</p>
<p style="font-size:14px;margin:0"><a href="{BASE}/circunscripcion/{p['slug']}.html" style="color:#b4532a">Ver la ficha de {p['nombre']}</a></p>'''
    text = (
        f"\nTu provincia: {p['nombre']}\n"
        f"{p.get('escanos_2026')} diputados · {fmt_int(p.get('electores_2026'))} electores · "
        f"participación 2023: {fmt_pct(p.get('participacion_2023'))}%.\n"
        f"Resultado 2023: {top}.\n{last}\n"
        f"{BASE}/circunscripcion/{p['slug']}.html\n"
    )
    return html, text


def render(sub, latest, prov):
    slug = ""
    page = sub.get("page") or ""
    if page.startswith("/circunscripcion/") and page.endswith(".html"):
        slug = page[len("/circunscripcion/"):-len(".html")]
    parts = {p["party"]: p for p in latest.get("parties", [])}
    rows = []
    for party in ("PP", "PSOE", "VOX", "SUMAR"):
        p = parts.get(party)
        if p:
            rows.append(f"<tr><td style='padding:5px 8px'><strong>{party}</strong></td><td style='padding:5px 8px;text-align:right'>{fmt_pct(p.get('mean'))}%</td><td style='padding:5px 8px;text-align:right'>{fmt_pct(p.get('min'))}–{fmt_pct(p.get('max'))}</td></tr>")
    table = "".join(rows)
    phtml, ptext = province_block(slug, prov)
    subject = "29N · media semanal" + (f" · {prov[slug]['nombre']}" if slug in prov else "")
    html = f'''<!doctype html><html lang="es"><body style="margin:0;background:#f6f3ed;color:#17202a;font-family:Georgia,serif">
<div style="max-width:600px;margin:0 auto;padding:30px 22px">
<p style="font-family:Arial,sans-serif;font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:#b4532a">Observatorio 29N</p>
<h1 style="font-size:26px;line-height:1.2;margin:8px 0 12px">La media de la semana</h1>
<p style="font-size:15px;line-height:1.6;margin:0 0 12px">Media ponderada de {latest.get('n_polls')} sondeos. Actualizado: {latest.get('updated_at')} · último sondeo: {latest.get('last_poll_date')}.</p>
<table style="border-collapse:collapse;font-family:Arial,sans-serif;font-size:14px;width:100%;background:#fff;border:1px solid #ddd"><thead><tr><th style="text-align:left;padding:6px 8px">Partido</th><th style="text-align:right;padding:6px 8px">Media</th><th style="text-align:right;padding:6px 8px">Rango</th></tr></thead><tbody>{table}</tbody></table>
<p style="font-size:13px;line-height:1.5;color:#59636e;margin:10px 0 0">Rango observado, no intervalo de confianza. No es un pronóstico.</p>
{phtml}
<p style="margin:24px 0 0"><a href="{BASE}/hemiciclo.html" style="display:inline-block;background:#17202a;color:#fff;text-decoration:none;padding:11px 16px;border-radius:4px;font-family:Arial,sans-serif;font-size:14px">Ver el hemiciclo</a></p>
<p style="font-size:12px;line-height:1.6;color:#59636e;margin-top:24px">Recibes esto porque te suscribiste al Observatorio 29N. <a href="{BASE}/api/unsubscribe?id={sub['id']}" style="color:#59636e">Darse de baja</a>.</p>
</div></body></html>'''
    text = (
        f"29N · media semanal\n\nMedia de {latest.get('n_polls')} sondeos. "
        f"Actualizado: {latest.get('updated_at')}.\n\n"
        + "\n".join(f"{p}: {fmt_pct(parts[p].get('mean'))}% (rango {fmt_pct(parts[p].get('min'))}–{fmt_pct(parts[p].get('max'))})"
                    for p in ("PP", "PSOE", "VOX", "SUMAR") if p in parts)
        + "\n\nNo es un pronóstico.\n"
        + ptext
        + f"\n{BASE}/hemiciclo.html\n\nBaja: {BASE}/api/unsubscribe?id={sub['id']}\n"
    )
    return subject, html, text


def send_resend(to, subject, html, text):
    env = load_env()
    key = env.get("RESEND_API_KEY", "")
    if not key:
        raise RuntimeError("RESEND_API_KEY no configurada")
    sender = env.get("RESEND_FROM", FROM_DEFAULT)
    if "<" not in sender:
        sender = f"Observatorio 29N <{sender}>"
    payload = json.dumps({"from": sender, "to": [to], "reply_to": REPLY,
                          "subject": subject, "html": html, "text": text}).encode()
    req = urllib.request.Request("https://api.resend.com/emails", data=payload,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                 "User-Agent": "Mozilla/5.0 (compatible; Observatorio29N/1.0)"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return 200 <= r.status < 300
    except urllib.error.HTTPError as ex:
        print(f"Resend HTTP {ex.code}: {ex.read(300).decode('utf-8','replace')}", file=sys.stderr)
        return False
    except Exception as ex:
        print(f"Resend: {ex}", file=sys.stderr)
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--test", metavar="EMAIL")
    ap.add_argument("--province", default="madrid")
    ap.add_argument("--send", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    now = datetime.now(TZ)
    if blackout.is_blackout(now):
        print("blackout: no se envían sondeos", file=sys.stderr)
        return 1
    latest = json.loads(LATEST.read_text(encoding="utf-8"))
    prov = load_provinces()
    if a.test:
        sub = {"id": "test", "email": a.test, "page": f"/circunscripcion/{a.province}.html"}
        subject, html, text = render(sub, latest, prov)
        print(subject)
        Path("/tmp/29n_email_preview.html").write_text(html, encoding="utf-8")
        if a.send:
            return 0 if send_resend(a.test, subject, html, text) else 1
        print("dry: preview en /tmp/29n_email_preview.html")
        return 0
    if not DB.exists():
        print(f"sin base de datos: {DB}", file=sys.stderr)
        return 1
    conn = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT id,email,page FROM subscribers WHERE status='confirmed' ORDER BY created_at").fetchall()
    conn.close()
    if a.limit:
        rows = rows[:a.limit]
    print(f"confirmados: {len(rows)}")
    if not rows:
        return 0
    subject, html, text = render(rows[0], latest, prov)
    Path("/tmp/29n_email_preview.html").write_text(html, encoding="utf-8")
    print("preview: /tmp/29n_email_preview.html")
    print("asunto:", subject)
    if a.dry or not a.send:
        print("dry: no se envía a la lista")
        return 0
    ok = 0
    for r in rows:
        s, h, t = render(dict(r), latest, prov)
        if send_resend(r["email"], s, h, t):
            ok += 1
        else:
            print("fallo:", r["email"], file=sys.stderr)
    print(f"enviados: {ok}/{len(rows)}")
    return 0 if ok == len(rows) else 1


if __name__ == "__main__":
    sys.exit(main())
