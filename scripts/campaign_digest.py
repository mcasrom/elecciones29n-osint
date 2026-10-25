#!/usr/bin/env python3
"""Parte matinal de campaña 29N (13–23 nov).

Solo actúa si hay un cambio relevante frente al estado anterior:
nuevo sondeo, cambio de bloque/mayoría, Δ≥1 pp en un partido principal
o Δ≥3 escaños. Encola en social-poster (Mastodon/Bluesky/Telegram/X manual).
Sin cambio: silencio. No publica del 24 al 28 (blackout).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Europe/Madrid")
ROOT = Path(__file__).resolve().parent.parent
LATEST = ROOT / "web" / "data" / "latest.json"
STATE = ROOT / "data" / "campaign_digest_state.json"
SP = Path("/home/deploy/social-poster")
URL = "https://elecciones29n.pruebapublica.com/hemiciclo.html"
IMG = "https://elecciones29n.pruebapublica.com/og-hemiciclo.png"
MAIN = ("PP", "PSOE", "VOX", "SUMAR")
MESES = ("ene","feb","mar","abr","may","jun","jul","ago","sep","oct","nov","dic")
START = date(2026, 11, 13)
END = date(2026, 11, 23)


def in_campaign(d: date) -> bool:
    return START <= d <= END


def load_state() -> dict:
    try:
        return json.loads(STATE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def snapshot(latest: dict) -> dict:
    parties = {p.get("party"): round(float(p.get("mean") or 0), 2) for p in latest.get("parties", [])}
    hem = (latest.get("hemicycle") or [{}])[-1]
    seats = {r.get("party"): int(r.get("seats") or 0) for r in hem.get("seats", [])}
    return {
        "date": datetime.now(TZ).strftime("%Y-%m-%d"),
        "n_polls": int(latest.get("n_polls") or 0),
        "last_poll_date": latest.get("last_poll_date"),
        "parties": parties,
        "seats": seats,
        "blocks": hem.get("blocks") or {},
        "majority": hem.get("majority"),
        "hem_date": hem.get("date"),
    }


def detect(prev: dict, cur: dict) -> list[str]:
    if not prev:
        return ["inicio del parte"]
    reasons = []
    if cur.get("n_polls") != prev.get("n_polls") or cur.get("last_poll_date") != prev.get("last_poll_date"):
        reasons.append("nuevo sondeo")
    if cur.get("blocks") != prev.get("blocks") or cur.get("majority") != prev.get("majority"):
        reasons.append("cambio de bloque o mayoría")
    for p in MAIN:
        a = float((cur.get("parties") or {}).get(p) or 0)
        b = float((prev.get("parties") or {}).get(p) or 0)
        if abs(a - b) >= 1.0:
            reasons.append(f"{p} {a - b:+.1f} pp")
    for p in MAIN:
        a = int((cur.get("seats") or {}).get(p) or 0)
        b = int((prev.get("seats") or {}).get(p) or 0)
        if abs(a - b) >= 3:
            reasons.append(f"{p} {a - b:+d} escaños")
    return reasons


def build_text(cur: dict, prev: dict) -> str:
    d = datetime.strptime(cur["date"], "%Y-%m-%d")
    seats = cur.get("seats") or {}
    parts = " · ".join(f"{p} {seats[p]}" for p in MAIN if p in seats)
    blocks = cur.get("blocks") or {}
    delta = []
    if prev:
        for p in MAIN:
            a = float((cur.get("parties") or {}).get(p) or 0)
            b = float((prev.get("parties") or {}).get(p) or 0)
            if abs(a - b) >= 0.5:
                delta.append(f"{p} {a - b:+.1f}")
    reason = " · ".join(detect(prev, cur)[:3])
    tail = f" Δ: {' · '.join(delta)}." if delta else ""
    return (
        f"Parte 29N · {d.day} {MESES[d.month-1]}: {parts}. Bloques {blocks.get('right', '—')}/{blocks.get('left', '—')}. "
        f"{reason}.{tail} Simulación, no pronóstico.\n{{url}}\n#29N #Sondeos"
    )


def enqueue(item_id: str, text: str) -> int:
    py = "/usr/bin/python3"
    add = [py, "social_queue.py", "add", "--id", item_id,
           "--when", datetime.now(TZ).isoformat(timespec="seconds"),
           "--channels", "mastodon,bluesky,telegram,x",
           "--text", text, "--image", IMG, "--url", URL,
           "--campaign", "29n-campaign"]
    r = subprocess.run(add, cwd=str(SP), capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        print(r.stdout + r.stderr, file=sys.stderr)
        return r.returncode
    r = subprocess.run([py, "social_queue.py", "approve", item_id], cwd=str(SP),
                       capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        print(r.stdout + r.stderr, file=sys.stderr)
    return r.returncode


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--force", action="store_true", help="ignora la ventana de campaña (pruebas)")
    a = ap.parse_args()

    now = datetime.now(TZ)
    if not a.force and not in_campaign(now.date()):
        print(f"[digest] fuera de campaña ({now.date()}); silencio")
        return 0
    try:
        latest = json.loads(LATEST.read_text(encoding="utf-8"))
    except (OSError, ValueError) as ex:
        print(f"[digest] no puedo leer {LATEST}: {ex}", file=sys.stderr)
        return 1
    cur = snapshot(latest)
    prev = load_state()
    reasons = detect(prev, cur)
    if not reasons:
        print("[digest] sin cambios relevantes; no se publica")
        return 0
    text = build_text(cur, prev)
    x_url = URL + "?utm_source=x&utm_medium=social&utm_campaign=29n-campaign"
    if len(text.replace("{url}", x_url)) > 280:
        print(f"[digest] texto X demasiado largo ({len(text.replace('{url}', x_url))}), no se encola", file=sys.stderr)
        return 1
    digest = hashlib.sha1((cur["date"] + text).encode()).hexdigest()[:6]
    item_id = f"campaign-{cur['date'].replace('-', '')}-{digest}"
    print(f"[digest] {item_id}\n{text}\n")
    if a.dry:
        print("[digest] dry: no se encola")
        return 0
    if enqueue(item_id, text) != 0:
        return 1
    cur["queued_id"] = item_id
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(cur, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"[digest] encolado {item_id}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
