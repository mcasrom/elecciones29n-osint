from __future__ import annotations

import csv
import json
import os
import re
import sys
import urllib.request

URL = "https://www.ondacero.es/elecciones/generales/encuestas/"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"
HIST = "data/polls_history.csv"

MAP = {"pp": "PP", "psoe": "PSOE", "vox": "VOX", "sumar": "SUMAR",
       "podemos": "PODEMOS", "salf": "SAF", "otros": "Otros"}


def fetch_html() -> str:
    req = urllib.request.Request(URL, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=40) as r:
        return r.read().decode("utf-8", "ignore")


def parse_html(html: str) -> list[dict]:
    i = html.find('"encuestas":[')
    if i < 0:
        raise ValueError("no se encontró el array de encuestas")
    start = html.find("[", i)
    depth = 0
    instr = esc = False
    end = None
    for j in range(start, len(html)):
        c = html[j]
        if instr:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                instr = False
        else:
            if c == '"':
                instr = True
            elif c == "[":
                depth += 1
            elif c == "]":
                depth -= 1
                if depth == 0:
                    end = j + 1
                    break
    if not end:
        raise ValueError("array de encuestas sin cierre")
    return json.loads(html[start:end])


def seen() -> set[tuple[str, str, str]]:
    if not os.path.exists(HIST):
        return set()
    with open(HIST, encoding="utf-8", newline="") as f:
        return {(r["party"], r["date"], r.get("pollster", "")) for r in csv.DictReader(f)}


def main() -> int:
    polls = parse_html(fetch_html())
    done = seen()
    new = not os.path.exists(HIST)
    added = 0
    skipped = 0
    os.makedirs("data", exist_ok=True)
    with open(HIST, "a", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["party", "date", "value", "source_url", "sample", "pollster", "kind"])
        for p in polls:
            pollster = str(p.get("fuente") or "").strip()
            date = str(p.get("pub") or "").strip()
            vals = {MAP[k]: v for k, v in (p.get("v") or {}).items() if k in MAP and v is not None}
            if not pollster or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date) or not vals:
                skipped += 1
                continue
            total = sum(vals.values())
            if not (90 <= total <= 110):
                skipped += 1
                continue
            for party, val in vals.items():
                key = (party, date, pollster)
                if key in done:
                    continue
                w.writerow([party, date, val, URL, "", pollster, "tracking"])
                done.add(key)
                added += 1
    print(f"[ondacero] {len(polls)} encuestas · {added} filas nuevas · {skipped} descartadas")
    return 0


if __name__ == "__main__":
    sys.exit(main())
