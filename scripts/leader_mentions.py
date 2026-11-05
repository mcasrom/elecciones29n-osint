#!/usr/bin/env python3
"""Menciones de líderes en titulares recientes. Solo lectura de intelligence-hub.

No mide actos, intención de voto ni apoyo: cuenta artículos cuyo titular o
sumario menciona un alias del líder, en ventanas de 24 h y 7 días.
"""
from __future__ import annotations
import argparse, json, re, sqlite3, unicodedata
from datetime import datetime, timedelta, timezone
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

DB = "/home/deploy/intelligence-hub/data/news.db"
OUT_DEFAULT = "/var/www/elecciones29n"
ALIASES = {
    "Pedro Sánchez": ["pedro sanchez", "sanchez"],
    "Feijóo": ["feijoo", "alberto nunez feijoo"],
    "Abascal": ["abascal", "santiago abascal"],
    "Yolanda Díaz": ["yolanda diaz", "yolanda"],
}
WINDOWS = (1, 7)

def norm(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", (s or "").lower()) if unicodedata.category(c) != "Mn")

def hit(text: str, aliases: list[str]) -> bool:
    t = norm(text)
    return any(re.search(r"(?<![a-z0-9])" + re.escape(a) + r"(?![a-z0-9])", t) for a in aliases)

def collect() -> dict:
    now = datetime.now(timezone.utc)
    con = sqlite3.connect("file:%s?mode=ro" % DB, uri=True)
    con.row_factory = sqlite3.Row
    out = {"generated_at": now.isoformat(timespec="seconds"), "source": "intelligence-hub/news.db", "source_label": "Titulares y sumarios de prensa española", "query": "lang=es · country=espana", "windows": {}}
    for days in WINDOWS:
        cut = (now - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%S")
        rows = con.execute("SELECT title, summary, published FROM articles WHERE lang='es' AND country='espana' AND published>=?", (cut,)).fetchall()
        counts = {k: 0 for k in ALIASES}
        day_sets = {k: set() for k in ALIASES}
        for r in rows:
            text = (r["title"] or "") + " " + (r["summary"] or "")
            day = (r["published"] or "")[:10]
            for k, aliases in ALIASES.items():
                if hit(text, aliases):
                    counts[k] += 1
                    day_sets[k].add(day)
        n = len(rows)
        leaders = [
            {"name": k, "articles": counts[k], "share_pct": round(100 * counts[k] / n, 1) if n else 0, "days": len(day_sets[k])}
            for k in ALIASES
        ]
        leaders.sort(key=lambda x: (-x["articles"], x["name"]))
        out["windows"][str(days)] = {"n_articles": n, "leaders": leaders}
    con.close()
    return out

def font(size: int, bold: bool = False):
    return ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-%s.ttf" % ("Bold" if bold else "Regular"), size)

def chart(window: dict, days: int, path: Path) -> None:
    W, H = 1000, 520
    bg, ink, muted, orange = "#ffffff", "#172033", "#64748b", "#ff5a1f"
    im = Image.new("RGB", (W, H), bg); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 10], fill=orange)
    d.text((54, 42), "Menciones de líderes · %s" % ("24 horas" if days == 1 else "7 días"), font=font(32, True), fill=ink)
    d.text((54, 88), "Artículos cuyo titular o sumario menciona al líder · n=%d" % window["n_articles"], font=font(18), fill=muted)
    leaders = window["leaders"]
    maxv = max((x["articles"] for x in leaders), default=1) or 1
    y = 155
    for x in leaders:
        name, val = x["name"], x["articles"]
        d.text((54, y), name, font=font(24, True), fill=ink)
        bw = int(560 * val / maxv) if maxv else 0
        d.rounded_rectangle([320, y + 2, 980, y + 34], radius=6, fill="#f1f5f9")
        if bw:
            d.rounded_rectangle([320, y + 2, 320 + bw, y + 34], radius=6, fill=orange)
        d.text((985, y + 4), "%d · %.1f%%" % (val, x["share_pct"]), font=font(18, True), fill=ink, anchor="ra")
        d.text((320, y + 42), "días con mención: %d" % x["days"], font=font(14), fill=muted)
        y += 82
    d.text((54, H - 34), "Fuente: titulares de prensa · no es intención de voto ni actos de campaña", font=font(14), fill=muted)
    im.save(path, optimize=True)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=OUT_DEFAULT)
    a = ap.parse_args()
    out = Path(a.out); (out / "data").mkdir(parents=True, exist_ok=True); (out / "img").mkdir(parents=True, exist_ok=True)
    data = collect()
    (out / "data" / "menciones.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    for days in WINDOWS:
        chart(data["windows"][str(days)], days, out / "img" / ("lideres-%dd.png" % days))
    print("menciones ok", out, "1d", data["windows"]["1"]["n_articles"], "7d", data["windows"]["7"]["n_articles"])

if __name__ == "__main__": main()
