#!/usr/bin/env python3
"""Pizarra y eventos de campaña 29N (9–23 nov).

Pizarra lunes y viernes; eventos solo si hay un sondeo nuevo o Δ≥0,5 pp
en un partido principal. Encola en social-poster (Mastodon/Bluesky/Telegram/X manual).
Sin evento ni pizarra: silencio. No publica del 24 al 28 (blackout).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import shutil
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Europe/Madrid")
ROOT = Path(__file__).resolve().parent.parent
LATEST = ROOT / "web" / "data" / "latest.json"
STATE = ROOT / "data" / "campaign_digest_state.json"
SP = Path("/home/deploy/social-poster")
URL = "https://elecciones29n.pruebapublica.com/robustez.html"
IMG = "https://elecciones29n.pruebapublica.com/og-robustez.png"
LEADERS = ROOT / "data" / "cis_lideres_2026.json"
INFOG = ROOT / "gen" / "gen_infografia_29n.py"
PUBLIC_OG = Path("/var/www/elecciones29n/og")
MAIN = ("PP", "PSOE", "VOX", "SUMAR")
MESES = ("ene","feb","mar","abr","may","jun","jul","ago","sep","oct","nov","dic")
START = date(2026, 11, 9)
END = date(2026, 11, 23)
WEEKLY_DAYS = {0, 4}  # lunes y viernes


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
        "n_houses": int((latest.get("health") or {}).get("n_pollsters") or 0),
        "iqr": (latest.get("health") or {}).get("dispersion_iqr"),
        "last_poll_date": latest.get("last_poll_date"),
        "ranges": {p.get("party"): [p.get("min"), p.get("max")] for p in latest.get("parties", [])},
        "parties": parties,
        "seats": seats,
        "blocks": hem.get("blocks") or {},
        "block_gap": (int((hem.get("blocks") or {}).get("right") or 0) - int((hem.get("blocks") or {}).get("left") or 0)),
        "health_status": (latest.get("health") or {}).get("status"),
        "leaders": _leaders_snapshot(),
        "majority": hem.get("majority"),
        "hem_date": hem.get("date"),
    }


def _leaders_snapshot() -> dict:
    try:
        data = json.loads(LEADERS.read_text(encoding="utf-8"))
        return {x.get("name"): round(float(x.get("mean") or 0), 2) for x in data.get("leaders", [])}
    except (OSError, ValueError):
        return {}


def detect(prev: dict, cur: dict) -> list[str]:
    if not prev:
        return ["inicio del parte"]
    reasons = []
    if cur.get("n_polls") != prev.get("n_polls") or cur.get("last_poll_date") != prev.get("last_poll_date"):
        reasons.append("nuevo sondeo")
    for p in MAIN:
        a = float((cur.get("parties") or {}).get(p) or 0)
        b = float((prev.get("parties") or {}).get(p) or 0)
        if abs(a - b) >= 0.5:
            reasons.append(f"{p} {a - b:+.1f} pp")
    # Un cambio de bloques o de valoración de líderes también merece una imagen.
    a = (cur.get("blocks") or {}); b = (prev.get("blocks") or {})
    if a and b and abs(int(a.get("right") or 0) - int(b.get("right") or 0)) >= 1:
        reasons.append("cambio de bloques")
    if cur.get("health_status") != prev.get("health_status") and prev.get("health_status"):
        reasons.append("salud de la muestra")
    for name, value in (cur.get("leaders") or {}).items():
        old = (prev.get("leaders") or {}).get(name)
        if old is not None and abs(float(value) - float(old)) >= 0.2:
            reasons.append(f"líderes: {name} {float(value)-float(old):+.2f}")
    return reasons


def build_text(cur: dict, prev: dict, weekly: bool = False) -> str:
    d = datetime.strptime(cur["date"], "%Y-%m-%d")
    ranges = cur.get("ranges") or {}
    values = cur.get("parties") or {}
    parts = []
    for party in MAIN:
        value = values.get(party)
        if value is None:
            continue
        low, high = (ranges.get(party) or ["—", "—"])[:2]
        parts.append(f"{party} {value:.1f}%")
    last = cur.get("last_poll_date") or "—"
    head = "Pizarra semanal 29N" if weekly else "Actualización 29N"
    detail = "Sin sondeos nuevos; " if weekly and not cur.get("changed") else ""
    return (
        f"{head} · {d.day} {MESES[d.month-1]}\n"
        + " · ".join(parts)
        + f"\n{detail}{cur.get('n_polls', 0)} sondeos/{cur.get('n_houses', 0)} casas · IQR {cur.get('iqr') or '—'} pp · último {last} · sin pronóstico.\n{{url}}\n#29N #Sondeos"
    )


def build_event_text(cur: dict, reasons: list[str]) -> str:
    return build_text(cur, {}, weekly=False).replace("Pizarra semanal 29N", "Nuevo sondeo 29N").replace(
        "Sin sondeos nuevos; ", ""
    )


def make_infografia(tag: str) -> str:
    """Genera el resumen y lo publica como estático; devuelve su URL."""
    out = ROOT / "web" / "og" / f"29n-infografia-{tag}.png"
    linkedin = ROOT / "web" / "og" / f"29n-infografia-{tag}-linkedin.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    r = subprocess.run(
        ["/usr/bin/python3", str(INFOG), "--out", str(out), "--linkedin", str(linkedin)],
        cwd=str(ROOT), capture_output=True, text=True, timeout=120,
    )
    if r.returncode != 0:
        raise RuntimeError((r.stdout + r.stderr)[-500:])
    PUBLIC_OG.mkdir(parents=True, exist_ok=True)
    shutil.copy2(out, PUBLIC_OG / out.name)
    shutil.copy2(linkedin, PUBLIC_OG / linkedin.name)
    return f"https://elecciones29n.pruebapublica.com/og/{out.name}"


def enqueue(item_id: str, text: str, image: str, account: str = "electoralhub") -> int:
    py = "/usr/bin/python3"
    add = [py, "social_queue.py", "add", "--id", item_id,
           "--when", datetime.now(TZ).isoformat(timespec="seconds"),
           "--channels", "mastodon,bluesky,telegram,x,linkedin",
           "--text", text, "--image", image, "--url", URL,
           "--campaign", "29n-campaign"]
    if account:
        add += ["--account", account]
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
    ap.add_argument("--account", default="electoralhub",
                    help="cuenta de Bluesky en social-poster (por defecto electoralhub)")
    a = ap.parse_args()

    now = datetime.now(TZ)
    if now.date() >= date(2026, 11, 24):
        print("[digest] blackout 24-28 nov: silencio")
        return 0
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
    weekly = now.weekday() in WEEKLY_DAYS
    if not reasons and not weekly:
        print("[digest] sin cambios relevantes y fuera de pizarra semanal; no se publica")
        return 0
    cur["changed"] = bool(reasons)
    text = build_text(cur, prev, weekly=weekly) if not reasons else build_event_text(cur, reasons)
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
    try:
        image = make_infografia(digest)
    except Exception as ex:
        print(f"[digest] no se pudo generar la infografía: {ex}", file=sys.stderr)
        return 1
    if enqueue(item_id, text, image, account=a.account) != 0:
        return 1
    cur["queued_id"] = item_id
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(cur, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"[digest] encolado {item_id}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
