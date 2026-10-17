from __future__ import annotations

import csv
import html
import json
import os
import re
import sys
import urllib.request
from datetime import date

API = "https://electomania.es/wp-json/wp/v2/posts?per_page=20&search=electopanel&_fields=title,content,link,date"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

HIST = "data/polls_history.csv"

PARTIES = {
    "PP": r"\bPP\b",
    "PSOE": r"\bPSOE\b",
    "VOX": r"\bVox\b",
    "SUMAR": r"\bSumar\b",
    "PODEMOS": r"\bPodemos\b",
    "ERC": r"\bERC\b",
    "JUNTS": r"\bJunts\b",
    "BILDU": r"\bEH Bildu\b",
    "PNV": r"\bPNV\b",
    "SAF": r"Se Acab[oó] la Fiesta",
}


def fetch_posts() -> list[dict]:
    req = urllib.request.Request(API, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


def strip_html(raw: str) -> str:
    return html.unescape(re.sub("<[^>]+>", " ", raw))


def extract_poll(post: dict) -> dict | None:
    title = html.unescape(re.sub("<[^>]+>", "", post["title"]["rendered"]))
    tl = title.lower()
    if "adelanto" in tl or "autonómico" in tl or "rioja" in tl:
        return None

    text = strip_html(post["content"]["rendered"])
    found: dict[str, float] = {}
    for party, pat in PARTIES.items():
        m = re.search(pat + r"[^.]{0,60}?(\d{1,2}[.,]\d)\s*%", text)
        if m and m.group(1):
            try:
                val = float(m.group(1).replace(",", "."))
            except ValueError:
                continue
            if 0 < val < 45:
                found[party] = val

    total = sum(found.values())
    if not (90 <= total <= 110 and len(found) >= 6):
        return None

    return {
        "date": post["date"][:10],
        "source_url": post["link"],
        "values": found,
    }


def append_rows(poll: dict) -> int:
    new = not os.path.exists(HIST)
    n = 0
    with open(HIST, "a", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["party", "date", "value", "source_url", "sample"])
        for party, val in sorted(poll["values"].items()):
            w.writerow([party, poll["date"], val, poll["source_url"], ""])
            n += 1
    return n


def seen_dates() -> set[str]:
    if not os.path.exists(HIST):
        return set()
    with open(HIST, encoding="utf-8") as f:
        return {row["date"] for row in csv.DictReader(f)}


def main() -> int:
    posts = fetch_posts()
    done = seen_dates()
    added = 0
    for post in posts:
        poll = extract_poll(post)
        if not poll or poll["date"] in done:
            continue
        n = append_rows(poll)
        print(f"{poll['date']}  {len(poll['values'])} partidos  {poll['source_url']}")
        added += n

    print(f"[electomania] {added} filas nuevas")
    return 0


if __name__ == "__main__":
    sys.exit(main())
