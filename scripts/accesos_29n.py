#!/usr/bin/env python3
"""Agregado diario de accesos 29N: humano vs máquina, sin IP en claro.

Uso:
  python3 scripts/accesos_29n.py --yesterday --tg   # cron diario
  python3 scripts/accesos_29n.py --all              # backfill
  python3 scripts/accesos_29n.py --day 2026-11-13   # un día
"""
from __future__ import annotations

import argparse
import collections
import os
import sqlite3
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path("/home/deploy/elecciones29n-osint")
FIMI = Path("/home/deploy/hybrid-fimi-radar")
SOCIAL = Path("/home/deploy/social-poster")
DB = ROOT / "data" / "accesos_29n.db"
HOST = "elecciones29n.pruebapublica.com"

os.environ.setdefault("FIMI_DATA", str(FIMI / "data"))
os.chdir(FIMI)
sys.path.insert(0, str(FIMI))
from detection import accesos as A  # noqa: E402

DDL = """
CREATE TABLE IF NOT EXISTS daily (
  day TEXT PRIMARY KEY,
  total INTEGER NOT NULL,
  human INTEGER NOT NULL,
  human_ips INTEGER NOT NULL,
  strict_ips INTEGER NOT NULL,
  owner INTEGER NOT NULL,
  ia_gente INTEGER NOT NULL,
  bots INTEGER NOT NULL,
  ia_bot INTEGER NOT NULL,
  api INTEGER NOT NULL,
  internal INTEGER NOT NULL,
  human_share REAL NOT NULL,
  top_pages TEXT NOT NULL DEFAULT '[]',
  human_alert INTEGER NOT NULL DEFAULT 0,
  bot_alert INTEGER NOT NULL DEFAULT 0,
  updated_at TEXT NOT NULL
);
"""


def collect():
    recs = []
    for f in A.ficheros_log(max_rot=14):
        try:
            fh = A._abrir(f)
        except OSError:
            continue
        for ln in fh:
            r = A.parse_line(ln)
            if not r or r["host"] != HOST:
                continue
            r["ip"] = ln.split(None, 1)[0]
            cat, scan, _ = A.clasificar(r["ip"], r["ruta"], r["status"], r["ua"])
            if cat == "HUMANO_PROBABLE" and scan:
                cat = "BOT"
            if cat == "ASISTENTE_IA" and A.es_ia_gente(r["ua"]):
                cat = "IA_GENTE"
            r["cat"] = cat
            r["scan"] = scan
            r["page"] = int((not scan and r["status"] == 200))
            recs.append(r)
        try:
            fh.close()
        except Exception:
            pass

    pages_by_ip = collections.Counter(
        (r["dia"], r["ip"]) for r in recs
        if r["cat"] == "HUMANO_PROBABLE" and r["page"]
    )
    for r in recs:
        if r["cat"] == "HUMANO_PROBABLE" and pages_by_ip[(r["dia"], r["ip"])] > 15:
            r["cat"] = "BOT"

    daily = collections.defaultdict(lambda: collections.Counter())
    ips = collections.defaultdict(lambda: {"hum": set(), "strict": set()})
    pages = collections.defaultdict(collections.Counter)
    for r in recs:
        c = daily[r["dia"]]
        c["total"] += 1
        c[r["cat"]] += 1
        if r["cat"] == "HUMANO_PROBABLE":
            ips[r["dia"]]["hum"].add(r["ip"])
            if r["page"]:
                pages[r["dia"]][r["ruta"].split("?")[0]] += 1
                if pages_by_ip[(r["dia"], r["ip"])] >= 2:
                    ips[r["dia"]]["strict"].add(r["ip"])
    return daily, ips, pages


def upsert(con, daily, ips, pages):
    con.executescript(DDL)
    for day in sorted(daily):
        c = daily[day]
        human = c["HUMANO_PROBABLE"]
        total = c["total"]
        top = [{"path": p, "n": n} for p, n in pages[day].most_common(5)]
        con.execute(
            "INSERT OR REPLACE INTO daily(day,total,human,human_ips,strict_ips,owner,"
            "ia_gente,bots,ia_bot,api,internal,human_share,top_pages,updated_at)"
            " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (day, total, human, len(ips[day]["hum"]), len(ips[day]["strict"]),
             c["DUENO"], c["IA_GENTE"], c["BOT"], c["ASISTENTE_IA"],
             c["API"], c["INTERNAL"], round(100 * human / max(1, total), 1),
             __import__("json").dumps(top, ensure_ascii=False),
             datetime.now(timezone.utc).isoformat(timespec="seconds")),
        )
    con.commit()


def prior_median(con, day, col):
    rows = con.execute(
        f"SELECT {col} FROM daily WHERE day < ? ORDER BY day DESC LIMIT 7", (day,)
    ).fetchall()
    vals = sorted(r[0] for r in rows if r[0] is not None)
    if not vals:
        return 0
    return vals[len(vals) // 2]


def mark_alerts(con, day):
    row = con.execute(
        "SELECT human,bots FROM daily WHERE day=?", (day,)
    ).fetchone()
    if not row:
        return False, False
    human, bots = row
    hmed = prior_median(con, day, "human")
    bmed = prior_median(con, day, "bots")
    human_alert = human == 0
    bot_alert = bots > max(500, 3 * bmed) and bmed > 0
    con.execute("UPDATE daily SET human_alert=?,bot_alert=? WHERE day=?",
                (int(human_alert), int(bot_alert), day))
    con.commit()
    return human_alert, bot_alert


def report(con, day):
    r = con.execute("SELECT * FROM daily WHERE day=?", (day,)).fetchone()
    if not r:
        return None
    keys = [d[0] for d in con.execute("SELECT * FROM daily LIMIT 0").description]
    d = dict(zip(keys, r))
    top = __import__("json").loads(d["top_pages"])
    lines = [
        f"📊 29N · accesos {day}",
        f"Humanos {d['human']} · {d['human_ips']} IPs · {d['strict_ips']} con ≥2 págs.",
        f"Dueño {d['owner']} · IA gente {d['ia_gente']} · Bots {d['bots']} · IA crawler {d['ia_bot']}",
        f"API {d['api']} · interno {d['internal']} · {d['human_share']}% humano",
    ]
    if top:
        lines.append("Top: " + " · ".join(f"{x['path']} {x['n']}" for x in top[:3]))
    if d["human_alert"]:
        lines.append("⚠️ 0 accesos humanos en un día completo")
    if d["bot_alert"]:
        lines.append("⚠️ Bots por encima de 3× la mediana de 7 días")
    return "\n".join(lines)


def send_tg(text):
    sys.path.insert(0, str(SOCIAL))
    import social_queue as q
    env = q.load_env()
    chat = env.get("FIMI_OWNER_CHAT", "")
    ok = q.send_tg(chat, text)
    print("telegram", "ok" if ok else "fallo")
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--yesterday", action="store_true")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--day")
    ap.add_argument("--tg", action="store_true")
    a = ap.parse_args()
    daily, ips, pages = collect()
    con = sqlite3.connect(DB)
    upsert(con, daily, ips, pages)
    days = sorted(daily)
    if a.all:
        for d in days:
            mark_alerts(con, d)
        print(f"backfill {len(days)} días · {DB}")
        return 0
    if a.day:
        target = a.day
    else:
        target = (datetime.now(timezone.utc).date() - timedelta(days=1)).isoformat()
    if target not in daily:
        print(f"sin datos para {target}", file=sys.stderr)
        return 1
    mark_alerts(con, target)
    text = report(con, target)
    print(text)
    if a.tg:
        return 0 if send_tg(text) else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
