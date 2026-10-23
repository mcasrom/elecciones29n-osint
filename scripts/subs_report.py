#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = Path(__file__).resolve().parent.parent / "data" / "subs.db"


def rows(conn: sqlite3.Connection, sql: str, args: tuple = ()) -> list[sqlite3.Row]:
    return list(conn.execute(sql, args))


def report(path: Path, days: int = 14) -> dict:
    conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True, timeout=5)
    conn.row_factory = sqlite3.Row
    out: dict = {"db": str(path), "days": days}
    out["total"] = conn.execute("SELECT COUNT(*) FROM subscribers").fetchone()[0]
    out["status"] = {r["status"]: r["n"] for r in rows(conn, "SELECT status, COUNT(*) n FROM subscribers GROUP BY status")}
    out["sources"] = [dict(r) for r in rows(conn, "SELECT source, COUNT(*) n FROM subscribers GROUP BY source ORDER BY n DESC")]
    out["consent_versions"] = [dict(r) for r in rows(conn, "SELECT COALESCE(NULLIF(consent_version,''),'(sin versión)') consent_version, COUNT(*) n FROM subscribers GROUP BY consent_version ORDER BY n DESC")]
    out["pages"] = [dict(r) for r in rows(conn, "SELECT COALESCE(NULLIF(page,''),'(sin página)') page, COUNT(*) n FROM subscribers GROUP BY page ORDER BY n DESC LIMIT 12")]
    out["utm"] = [dict(r) for r in rows(conn, "SELECT COALESCE(NULLIF(utm_source,''),'(directo)') utm_source, COUNT(*) n FROM subscribers GROUP BY utm_source ORDER BY n DESC")]
    out["referrers"] = [dict(r) for r in rows(conn, "SELECT COALESCE(NULLIF(referrer_host,''),'(sin referrer)') referrer_host, COUNT(*) n FROM subscribers GROUP BY referrer_host ORDER BY n DESC LIMIT 12")]
    out["daily"] = [dict(r) for r in rows(conn, "SELECT substr(created_at,1,10) dia, COUNT(*) n FROM subscribers WHERE created_at >= date('now', ?) GROUP BY dia ORDER BY dia", (f"-{days} days",))]
    out["funnel"] = {
        "pendientes": out["status"].get("pending", 0),
        "confirmados": out["status"].get("confirmed", 0),
        "bajas": out["status"].get("unsubscribed", 0),
    }
    if out["total"]:
        out["funnel"]["tasa_confirmacion_pct"] = round(100 * out["funnel"]["confirmados"] / out["total"], 1)
    conn.close()
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", type=Path, default=DB_PATH)
    ap.add_argument("--days", type=int, default=14)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    if not args.db.exists():
        print(f"sin base de datos: {args.db}")
        return 1
    data = report(args.db, args.days)
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 0
    print(f"base: {data['db']}")
    print(f"total: {data['total']} · pendientes {data['funnel']['pendientes']} · confirmados {data['funnel']['confirmados']} · bajas {data['funnel']['bajas']} · confirmación {data['funnel'].get('tasa_confirmacion_pct', 0)}%")
    for key, title in (("sources", "fuente"), ("pages", "página"), ("utm", "utm_source"), ("referrers", "referrer")):
        if data[key]:
            print(f"\n{title}:")
            for r in data[key]:
                print(f"  {r[list(r)[0]]}: {r['n']}")
    if data["daily"]:
        print("\núltimos días:")
        for r in data["daily"]:
            print(f"  {r['dia']}: {r['n']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
