from __future__ import annotations

import csv
import html
import json
import os
import re
import sys
import urllib.request

API = "https://electomania.es/wp-json/wp/v2/posts?per_page=20&search=electopanel&_fields=title,content,link,date&page={page}"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

HIST = "data/polls_history.csv"

PARTIES = {
    "PP": r"\bPP\b",
    "PSOE": r"\bPSOE\b",
    "VOX": r"\bVox\b",
    "SUMAR": r"\b(?:Sumar|Frente Amplio)\b",
    "PODEMOS": r"\bPodemos\b",
    "ERC": r"\bERC\b",
    "JUNTS": r"\bJunts\b",
    "BILDU": r"\bEH Bildu\b",
    "PNV": r"\bPNV\b",
    "SAF": r"Se Acab[oó] la Fiesta",
}


def fetch_posts(max_pages: int = 4) -> list[dict]:
    out: list[dict] = []
    for page in range(1, max_pages + 1):
        req = urllib.request.Request(API.format(page=page), headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=12) as resp:
                batch = json.loads(resp.read().decode())
        except Exception:
            break
        if not isinstance(batch, list) or not batch:
            break
        out.extend(batch)
        if len(batch) < 20:
            break
    return out


def strip_html(raw: str) -> str:
    return html.unescape(re.sub("<[^>]+>", " ", raw))


def parse_sample(text: str) -> int | None:
    m = re.search(r"Tamaño muestral:\s*([\d.]+)", text)
    if not m:
        m = re.search(r"([\d.]+)\s+cuestionarios", text)
    if not m:
        return None
    try:
        n = int(m.group(1).replace(".", ""))
    except ValueError:
        return None
    return n if 200 <= n <= 20000 else None


def pollster_of(title: str) -> tuple[str, str]:
    tl = title.lower()
    if "electopromedio" in tl:
        return "ElectoPromedio", "average"
    if "electopanel" in tl:
        return "ElectoPanel", "tracking"
    return "Electomania", "tracking"


def extract_poll(post: dict) -> dict | None:
    title = html.unescape(re.sub("<[^>]+>", "", post["title"]["rendered"]))
    tl = title.lower()
    if "adelanto" in tl or "autonómico" in tl or "rioja" in tl:
        return None

    text = strip_html(post["content"]["rendered"])
    found: dict[str, float] = {}
    for party, pat in PARTIES.items():
        # "Frente Amplio, que concurre por primera vez como coalición estatal,
        # obtiene el 4,9%" deja 66 caracteres hasta la cifra: 60 no bastaban.
        window = 90 if party == "SUMAR" else 60
        m = re.search(pat + rf"[^.]{{0,{window}}}?(\d{{1,2}}[.,]\d)\s*%", text)
        if m and m.group(1):
            try:
                val = float(m.group(1).replace(",", "."))
            except ValueError:
                continue
            if 0 < val < 45:
                found[party] = val

    total = sum(found.values())
    # Los sondeos reales suman ~90-95 % (no listan "otros"/menores). El 18-oct
    # daba 87,3 y se descartaba porque faltaba Frente Amplio (4,9); con FA
    # suma 92,2. 85-110 sigue excluyendo posts que no son intención de voto
    # (p.ej. preferencia de Gobierno, suma 336).
    if not (85 <= total <= 110 and len(found) >= 6):
        return None

    pollster, kind = pollster_of(title)
    return {
        "date": post["date"][:10],
        "source_url": post["link"],
        "values": found,
        "sample": parse_sample(text),
        "pollster": pollster,
        "kind": kind,
    }


def append_rows(poll: dict) -> int:
    new = not os.path.exists(HIST)
    n = 0
    with open(HIST, "a", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["party", "date", "value", "source_url", "sample", "pollster", "kind"])
        for party, val in sorted(poll["values"].items()):
            w.writerow([
                party, poll["date"], val, poll["source_url"],
                poll.get("sample") or "", poll.get("pollster", ""), poll.get("kind", "tracking"),
            ])
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
        print(
            f"{poll['date']}  {len(poll['values'])} partidos  "
            f"{poll.get('pollster','?')}/{poll.get('kind','?')}  "
            f"n={poll.get('sample') or '?'}  {poll['source_url']}"
        )
        added += n

    print(f"[electomania] {added} filas nuevas")
    return 0


if __name__ == "__main__":
    sys.exit(main())
