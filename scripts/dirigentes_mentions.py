#!/usr/bin/env python3
"""Cuenta menciones de dirigentes/candidatos del 29N. Registro con estados."""
from __future__ import annotations
import argparse, json, re, sqlite3, unicodedata
from datetime import datetime, timedelta, timezone
from pathlib import Path

DB = "/home/deploy/intelligence-hub/data/news.db"
ROOT = Path(__file__).resolve().parent.parent
REG = Path(__file__).resolve().parent / "dirigentes-29n.json"

def norm(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", (s or "").lower()) if unicodedata.category(c) != "Mn")

def hit(text: str, aliases: list[str]) -> bool:
    t = norm(text)
    return any(re.search(r"(?<![a-z0-9])" + re.escape(norm(a)) + r"(?![a-z0-9])", t) for a in aliases)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); a = ap.parse_args()
    reg = json.loads(REG.read_text(encoding="utf-8"))
    now = datetime.now(timezone.utc)
    con = sqlite3.connect("file:%s?mode=ro" % DB, uri=True); con.row_factory = sqlite3.Row
    windows = {}
    for days in (1, 7):
        cut = (now - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%S")
        rows = con.execute("SELECT title, summary, published, source FROM articles WHERE lang='es' AND country='espana' AND published>=?", (cut,)).fetchall()
        counts = {p["id"]: 0 for p in reg["people"]}; day_sets = {p["id"]: set() for p in reg["people"]}
        src = {}
        for r in rows:
            text = (r["title"] or "") + " " + (r["summary"] or ""); day = (r["published"] or "")[:10]
            src[r["source"]] = src.get(r["source"], 0) + 1
            for p in reg["people"]:
                if hit(text, p["aliases"]):
                    counts[p["id"]] += 1; day_sets[p["id"]].add(day)
        n = len(rows)
        out_people = []
        for p in reg["people"]:
            q = dict(p); q["articles"] = counts[p["id"]]; q["share_pct"] = round(100 * counts[p["id"]] / n, 1) if n else 0; q["days"] = len(day_sets[p["id"]])
            out_people.append(q)
        out_people.sort(key=lambda x: (-x["articles"], x["full_name"]))
        windows[str(days)] = {"n_articles": n, "sources": [{"name": k, "articles": v} for k, v in sorted(src.items(), key=lambda kv: -kv[1])], "people": out_people}
    con.close()
    out = {"generated_at": now.isoformat(timespec="seconds"), "source": "intelligence-hub/news.db", "candidates_source": reg["candidates_source"], "candidates_url": reg["candidates_url"], "note": reg["note"], "windows": windows}
    outdir = Path(a.out); (outdir / "data").mkdir(parents=True, exist_ok=True)
    (outdir / "data" / "dirigentes.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print("dirigentes ok", outdir, "1d", windows["1"]["n_articles"], "7d", windows["7"]["n_articles"])

if __name__ == "__main__": main()
