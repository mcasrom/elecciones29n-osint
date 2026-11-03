#!/usr/bin/env python3
"""Avisos por correo a suscriptores confirmados del 29N.

- Solo envía si cambia el número/fecha de sondeos, la media o el hemiciclo.
- Excluye el blackout 24-28 nov.
- Estado por suscriptor (`last_sent_fingerprint`) y global.
- `--seed` fija el estado sin enviar; `--dry-run` no envía ni escribe.
- `--to` prueba una sola dirección sin tocar la lista.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from agg import blackout  # noqa: E402

DB = ROOT / "data" / "subs.db"
LATEST = ROOT / "web" / "data" / "latest.json"
STATE = ROOT / "data" / "alertas_email_state.json"
ENV = Path("/home/deploy/newsletter/.env")
BASE = "https://elecciones29n.pruebapublica.com"
FROM_DEFAULT = "Observatorio 29N <newsletter@viajeinteligencia.com>"
REPLY = "info.elecciones29n@pruebapublica.com"
PARTIES = ("PP", "PSOE", "VOX", "SUMAR")


def env(path=ENV):
    d = {}
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                d[k.strip()] = v.strip().strip('"').strip("'")
    except OSError:
        pass
    return d


def fmt(v):
    return f"{float(v):.2f}".replace(".", ",")


def fingerprint(latest: dict) -> str:
    means = {p.get("party"): round(float(p.get("mean") or 0), 2)
             for p in latest.get("parties", []) if p.get("party") in PARTIES}
    hem = (latest.get("hemicycle") or [{}])[-1]
    base = {
        "n_polls": latest.get("n_polls"),
        "last_poll_date": latest.get("last_poll_date"),
        "means": means,
        "blocks": hem.get("blocks"),
        "majority": hem.get("majority"),
    }
    raw = json.dumps(base, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def reason(prev: dict | None, cur: dict) -> str:
    if not prev:
        return "primer aviso"
    if cur["n_polls"] != prev["n_polls"] or cur["last_poll_date"] != prev["last_poll_date"]:
        try:
            if int(cur["n_polls"]) > int(prev["n_polls"]):
                return "nuevo sondeo"
        except Exception:
            pass
        return "recalculo por ventana"
    if any(abs(cur["means"].get(p, 0) - prev["means"].get(p, 0)) >= 0.1 for p in PARTIES):
        return "cambio en la media"
    if cur["blocks"] != prev["blocks"] or cur["majority"] != prev["majority"]:
        return "cambio en el hemiciclo"
    return "datos actualizados"


def ensure_schema() -> None:
    if not DB.exists():
        raise SystemExit(f"falta {DB}")
    con = sqlite3.connect(DB, timeout=15)
    try:
        cols = {r[1] for r in con.execute("PRAGMA table_info(subscribers)")}
        if "last_sent_fingerprint" not in cols:
            con.execute("ALTER TABLE subscribers ADD COLUMN last_sent_fingerprint TEXT")
        con.commit()
    finally:
        con.close()


def render(latest: dict, sub: dict, why: str) -> tuple[str, str, str]:
    parts = {p.get("party"): p for p in latest.get("parties", [])}
    unsub = f"{BASE}/api/unsubscribe?id={sub['id']}"
    nov = (latest.get("novedades") or [{}])[0] if why == "nuevo sondeo" else {}
    poll_note = ""
    if nov.get("pollster"):
        d = str(nov.get("date") or "")
        poll_note = f"{nov['pollster']}" + (f" ({d[8:10]}/{d[5:7]})" if len(d) >= 10 else "")
    # Asunto neutro: el primer envío con "nuevo sondeo" no llegó a la bandeja.
    subject = f"29N: actualización de la media · {poll_note}" if poll_note else "29N: actualización de la media"
    rows = "".join(
        f"<tr><td style='padding:5px 8px'><strong>{escape(p)}</strong></td>"
        f"<td style='padding:5px 8px;text-align:right'>{fmt(parts[p].get('mean'))}%</td>"
        f"<td style='padding:5px 8px;text-align:right;color:#59636e'>"
        f"{fmt(parts[p].get('min'))}–{fmt(parts[p].get('max'))}</td></tr>"
        for p in PARTIES if p in parts
    )
    text = (
        f"Observatorio 29N · {why}\n\n"
        + (f"Nuevo sondeo: {poll_note}.\n" if poll_note else "")
        + f"{latest.get('n_polls')} sondeos en la media. Último sondeo: {latest.get('last_poll_date')}.\n\n"
        + "\n".join(f"{p}: {fmt(parts[p].get('mean'))}% (rango {fmt(parts[p].get('min'))}–{fmt(parts[p].get('max'))})"
                    for p in PARTIES if p in parts)
        + "\n\nNo es un pronóstico. La media y el rango no son un intervalo de confianza.\n"
        + f"{BASE}/\n\nBaja: {unsub}\n"
    )
    html = f"""<!doctype html><html lang="es"><body style="margin:0;background:#f6f3ed;color:#17202a;font-family:Georgia,serif">
<div style="max-width:560px;margin:0 auto;padding:30px 22px">
<p style="font-family:Arial,sans-serif;font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:#b4532a">Observatorio Electoral 29N</p>
<h1 style="font-size:25px;line-height:1.2;margin:10px 0 8px">{escape(why.capitalize())}</h1>
{f'<p style="font-size:15px;line-height:1.6;margin:0 0 6px"><strong>Nuevo sondeo: {escape(poll_note)}</strong></p>' if poll_note else ''}
<p style="font-size:15px;line-height:1.6;margin:0 0 14px">{latest.get('n_polls')} sondeos en la media. Último sondeo: {escape(str(latest.get('last_poll_date')))}.</p>
<table style="border-collapse:collapse;font-family:Arial,sans-serif;font-size:14px;width:100%;background:#fff;border:1px solid #ddd">
<thead><tr><th style="text-align:left;padding:6px 8px">Partido</th><th style="text-align:right;padding:6px 8px">Media</th><th style="text-align:right;padding:6px 8px">Rango</th></tr></thead>
<tbody>{rows}</tbody></table>
<p style="font-size:13px;line-height:1.5;color:#59636e;margin:10px 0 0">Rango observado, no intervalo de confianza. No es un pronóstico.</p>
<p style="margin:22px 0 0"><a href="{BASE}/" style="display:inline-block;background:#17202a;color:#fff;text-decoration:none;padding:11px 16px;border-radius:4px;font-family:Arial,sans-serif;font-size:14px">Ver el observatorio</a></p>
<p style="font-size:12px;line-height:1.6;color:#59636e;margin-top:24px">Recibes esto porque confirmaste tu suscripción. <a href="{unsub}" style="color:#59636e">Darse de baja</a>.</p>
</div></body></html>"""
    return subject, html, text


def send(to: str, subject: str, html: str, text: str, sub_id: str | None = None) -> bool:
    e = env()
    key = e.get("RESEND_API_KEY", "")
    if not key:
        print("falta RESEND_API_KEY", file=sys.stderr)
        return False
    sender = e.get("RESEND_FROM", FROM_DEFAULT)
    if "<" not in sender:
        sender = f"Observatorio 29N <{sender}>"
    data = {"from": sender, "to": [to], "reply_to": REPLY,
            "subject": subject, "html": html, "text": text}
    if sub_id:
        data["headers"] = {
            "List-Unsubscribe": f"<{BASE}/api/unsubscribe?id={sub_id}>",
            "List-Unsubscribe-Post": "List-Unsubscribe=One-Click",
        }
    payload = json.dumps(data).encode()
    req = urllib.request.Request(
        "https://api.resend.com/emails", data=payload,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                 "User-Agent": "Mozilla/5.0 (compatible; Observatorio29N/1.0)"},
        method="POST")
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            body = r.read(500).decode("utf-8", "replace")
            try:
                rid = json.loads(body).get("id", "")
            except Exception:
                rid = ""
            if rid:
                print(f"resend id: {rid}")
            return 200 <= r.status < 300
    except urllib.error.HTTPError as ex:
        print(f"Resend HTTP {ex.code}: {ex.read(300).decode('utf-8','replace')}", file=sys.stderr)
    except Exception as ex:  # noqa: BLE001
        print(f"Resend: {ex}", file=sys.stderr)
    return False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--seed", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--to", metavar="EMAIL")
    ap.add_argument("--subject", default="")
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()

    if blackout.is_blackout():
        print("blackout: no se envían sondeos")
        return 0
    try:
        latest = json.loads(LATEST.read_text(encoding="utf-8"))
    except Exception as ex:
        print(f"no se pudo leer {LATEST}: {ex}", file=sys.stderr)
        return 1
    cur = json.loads(json.dumps({
        "n_polls": latest.get("n_polls"),
        "last_poll_date": latest.get("last_poll_date"),
        "means": {p.get("party"): round(float(p.get("mean") or 0), 2)
                  for p in latest.get("parties", []) if p.get("party") in PARTIES},
        "blocks": ((latest.get("hemicycle") or [{}])[-1].get("blocks")),
        "majority": ((latest.get("hemicycle") or [{}])[-1].get("majority")),
    }))
    fp = fingerprint(latest)
    prev_state = {}
    try:
        prev_state = json.loads(STATE.read_text(encoding="utf-8"))
    except Exception:
        pass
    prev = prev_state.get("snapshot") if isinstance(prev_state, dict) else None
    why = reason(prev, cur)

    if a.to:
        subject, html, text = render(latest, {"id": "test"}, why)
        if a.subject:
            subject = a.subject
        print(f"prueba a {a.to}: {subject}")
        if a.dry_run:
            return 0
        return 0 if send(a.to, subject, html, text) else 1

    if a.seed or not prev_state:
        if not a.dry_run:
            STATE.parent.mkdir(parents=True, exist_ok=True)
            STATE.write_text(json.dumps({"fingerprint": fp, "snapshot": cur,
                                         "seeded_at": datetime.now(timezone.utc).isoformat()},
                                        ensure_ascii=False), encoding="utf-8")
        print(f"estado sembrado: n_polls={cur['n_polls']} ({why})")
        return 0

    changed = a.force or prev_state.get("fingerprint") != fp
    if not changed:
        print(f"sin cambios ({cur['n_polls']} sondeos)")
        return 0

    ensure_schema()
    con = sqlite3.connect(DB, timeout=15)
    con.row_factory = sqlite3.Row
    rows = con.execute(
        "SELECT id,email,last_sent_fingerprint FROM subscribers WHERE status='confirmed' ORDER BY created_at"
    ).fetchall()
    if a.limit:
        rows = rows[:a.limit]
    print(f"cambio: {why} · confirmados: {len(rows)}")
    if a.dry_run:
        con.close()
        print("dry-run: no se envía")
        return 0
    sent = 0
    for row in rows:
        if not a.force and row["last_sent_fingerprint"] == fp:
            continue
        subject, html, text = render(latest, dict(row), why)
        if a.subject:
            subject = a.subject
        if send(row["email"], subject, html, text, row["id"]):
            con.execute("UPDATE subscribers SET last_sent_at=?, last_sent_fingerprint=? WHERE id=?",
                        (datetime.now(timezone.utc).isoformat(timespec="seconds"), fp, row["id"]))
            con.commit()
            sent += 1
        else:
            print(f"fallo: {row['id']}", file=sys.stderr)
    con.close()
    if sent:
        STATE.parent.mkdir(parents=True, exist_ok=True)
        STATE.write_text(json.dumps({"fingerprint": fp, "snapshot": cur,
                                     "sent_at": datetime.now(timezone.utc).isoformat()},
                                    ensure_ascii=False), encoding="utf-8")
    print(f"enviados: {sent}/{len(rows)}")
    return 0 if sent or not rows else 1


if __name__ == "__main__":
    raise SystemExit(main())
