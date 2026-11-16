#!/usr/bin/env python3
"""Importa trackings diarios publicados por Electomanía.

No son sondeos independientes: se guardan con un nombre de casa terminado en
" tracking" para que la media agregada los excluya. La fuente es el artículo
de Electomanía, que replica la ficha publicada por cada casa.
"""
from __future__ import annotations

import csv
import html
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from datetime import datetime

API = "https://electomania.es/wp-json/wp/v2/posts?per_page=20&search={q}&_fields=title,content,link,date&page={page}"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"
HIST = "data/polls_history.csv"
START = "2026-11-13"

QUERIES = (
    ('40dB tracking', '"tracking 40dB"'),
    ('Sigma Dos tracking', '"tracking Sigma Dos"'),
    ('SW Demoscopia', '"tracking SW Demoscopia"'),
)

PARTY_PATTERNS = {
    "PP": r"\bPP\b",
    "PSOE": r"\bPSOE\b",
    "VOX": r"\bVox\b",
    "SUMAR": r"\b(?:Frente Amplio|Sumar)\b",
}


def fetch(query: str, max_pages: int = 3) -> list[dict]:
    out = []
    for page in range(1, max_pages + 1):
        url = API.format(q=urllib.parse.quote(query), page=page)
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                batch = json.loads(r.read().decode())
        except Exception:
            break
        if not isinstance(batch, list) or not batch:
            break
        out.extend(batch)
        if len(batch) < 20:
            break
    return out


def clean(raw: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", " ", raw))


def parse_values(text: str) -> dict[str, float]:
    # Recorta desde la tabla de la ficha; así no se confunde con la entradilla.
    i = text.find("Partido")
    tail = text[i:] if i >= 0 else text
    vals = {}
    for party, pat in PARTY_PATTERNS.items():
        m = re.search(pat + r".{0,240}?(\d{1,2}[.,]\d)\s*%", tail, re.S)
        if not m:
            continue
        try:
            v = float(m.group(1).replace(",", "."))
        except ValueError:
            continue
        if 0 < v < 45:
            vals[party] = v
    return vals


def pollster_of(title: str) -> str | None:
    t = html.unescape(title).lower()
    if "40db" in t:
        return "40dB tracking"
    if "sigma dos" in t:
        return "Sigma Dos tracking"
    if "sw demoscopia" in t:
        return "SW Demoscopia"
    return None


def main() -> int:
    seen = set()
    if os.path.exists(HIST):
        with open(HIST, encoding="utf-8", newline="") as f:
            for row in csv.DictReader(f):
                seen.add((row.get("party"), row.get("date"), row.get("pollster")))

    new_file = not os.path.exists(HIST)
    rows = []
    for pollster, query in QUERIES:
        for post in fetch(query):
            date = (post.get("date") or "")[:10]
            if not date or date < START:
                continue
            title = post.get("title", {}).get("rendered", "")
            house = pollster_of(title)
            if house != pollster:
                continue
            values = parse_values(clean(post.get("content", {}).get("rendered", "")))
            if len(values) < 4 or not (80 <= sum(values.values()) <= 110):
                continue
            for party, val in values.items():
                key = (party, date, house)
                if key in seen:
                    continue
                seen.add(key)
                rows.append([party, date, val, post.get("link", ""), "", house, "tracking"])

    if rows:
        with open(HIST, "a", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            if new_file:
                w.writerow(["party", "date", "value", "source_url", "sample", "pollster", "kind"])
            w.writerows(rows)
    print(f"[tracking_electomania] {len(rows)} filas nuevas")
    return 0


if __name__ == "__main__":
    sys.exit(main())
