#!/usr/bin/env python3
"""Agregado diario de accesos 29N: humano vs máquina, sin IP en claro.

Uso:
  python3 scripts/accesos_29n.py --yesterday --tg   # cron diario
  python3 scripts/accesos_29n.py --all              # backfill
  python3 scripts/accesos_29n.py --day 2026-11-13   # un día
  python3 scripts/accesos_29n.py --week --tg        # semana móvil de 7 días
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import sqlite3
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlsplit

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
CREATE TABLE IF NOT EXISTS weekly (
  week_end TEXT PRIMARY KEY,
  week_start TEXT NOT NULL,
  human_ips INTEGER NOT NULL,
  strict_ips INTEGER NOT NULL,
  recurrent_ips INTEGER NOT NULL,
  external_domains INTEGER NOT NULL,
  external_top TEXT NOT NULL DEFAULT '[]',
  top_pages TEXT NOT NULL DEFAULT '[]',
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

    weekly = {}
    today = datetime.now(timezone.utc).date().isoformat()
    complete_days = sorted({r["dia"] for r in recs if r["dia"] < today})
    if complete_days:
        end = complete_days[-1]
        start = (date.fromisoformat(end) - timedelta(days=6)).isoformat()
        human_week = set()
        strict_days = collections.defaultdict(set)
        external = collections.Counter()
        pages_week = collections.Counter()
        for r in recs:
            if r["dia"] < start or r["cat"] != "HUMANO_PROBABLE" or not r["page"]:
                continue
            human_week.add(r["ip"])
            path = r["ruta"].split("?")[0]
            pages_week[path] += 1
            if pages_by_ip[(r["dia"], r["ip"])] >= 2:
                strict_days[r["ip"]].add(r["dia"])
            ref = r.get("referer") or "-"
            if ref and ref != "-":
                host = urlsplit(ref if "://" in ref else "http://" + ref).hostname or ""
                if host and not host.endswith("pruebapublica.com"):
                    external[host] += 1
        weekly = {
            "week_end": end,
            "week_start": start,
            "human_ips": len(human_week),
            "strict_ips": len(strict_days),
            "recurrent_ips": sum(1 for days in strict_days.values() if len(days) >= 2),
            "external": external,
            "pages": pages_week,
        }
    return daily, ips, pages, weekly


def upsert(con, daily, ips, pages, weekly):
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
    if weekly:
        con.execute(
            "INSERT OR REPLACE INTO weekly(week_end,week_start,human_ips,strict_ips,"
            "recurrent_ips,external_domains,external_top,top_pages,updated_at)"
            " VALUES (?,?,?,?,?,?,?,?,?)",
            (weekly["week_end"], weekly["week_start"], weekly["human_ips"],
             weekly["strict_ips"], weekly["recurrent_ips"], len(weekly["external"]),
             json.dumps(weekly["external"].most_common(10), ensure_ascii=False),
             json.dumps(weekly["pages"].most_common(10), ensure_ascii=False),
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


def report_week(con, week_end):
    r = con.execute("SELECT * FROM weekly WHERE week_end=?", (week_end,)).fetchone()
    if not r:
        return None
    keys = [d[0] for d in con.execute("SELECT * FROM weekly LIMIT 0").description]
    d = dict(zip(keys, r))
    top = json.loads(d["external_top"])
    pages = json.loads(d["top_pages"])
    lines = [
        f"📊 29N · semana {d['week_start']} → {d['week_end']}",
        f"Humanos {d['human_ips']} IPs · estrictos {d['strict_ips']} · recurrentes {d['recurrent_ips']}",
        f"Dominios externos {d['external_domains']}: " + " · ".join(f"{h} {n}" for h, n in top[:6]),
    ]
    if pages:
        lines.append("Top: " + " · ".join(f"{p} {n}" for p, n in pages[:3]))
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
    ap.add_argument("--week", nargs="?", const="latest")
    ap.add_argument("--tg", action="store_true")
    a = ap.parse_args()
    daily, ips, pages, weekly = collect()
    con = sqlite3.connect(DB)
    upsert(con, daily, ips, pages, weekly)
    days = sorted(daily)
    if a.all:
        for d in days:
            mark_alerts(con, d)
        print(f"backfill {len(days)} días · {DB}")
        return 0
    if a.week:
        target_week = (weekly.get("week_end") if a.week == "latest" else a.week)
        text = report_week(con, target_week)
        if not text:
            print(f"sin semana para {target_week}", file=sys.stderr)
            return 1
        print(text)
        if a.tg:
            return 0 if send_tg(text) else 1
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
