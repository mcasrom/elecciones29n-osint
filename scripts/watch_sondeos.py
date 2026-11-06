#!/usr/bin/env python3
"""watch_sondeos.py — detecta sondeos nuevos en prensa y los deja en cola.

No inventa porcentajes ni publica: escribe `data/candidatos_sondeos.csv` para
revisión humana. Las fuentes con datos estructurados (Electomania/Onda Cero) sí
se ingieren automáticamente en `scripts/refresh_polls.sh`.

Uso:
  .venv/bin/python scripts/watch_sondeos.py
  .venv/bin/python scripts/watch_sondeos.py --json
"""
from __future__ import annotations

import csv
import hashlib
import html
import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "candidatos_sondeos.csv"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126 Safari/537.36"

FEEDS = {
    "El Mundo": "https://www.elmundo.es/rss/portada.xml",
    "El Español": "https://www.elespanol.com/rss/",
    "elDiario.es": "https://www.eldiario.es/rss/",
    "La Razón": "https://news.google.com/rss/search?q=site%3Alarazon.es%20encuesta%2029N&hl=es&gl=ES&ceid=ES:ES",
}
POLLSTERS = ("Sigma Dos", "SocioMétrica", "Sociométrica", "NC Report", "Ateneo del Dato",
             "GAD3", "40dB", "DYM", "IMOP", "Target Point", "Celeste-Tel", "Invymark",
             "SW Demoscopia", "More In Common")
SIGNAL = re.compile(r"\b(encuesta|sondeo|barómetro)\b", re.I)
ELECTION = re.compile(r"\b(29N|29-N|elecciones generales|PP|PSOE|Vox)\b", re.I)


def norm_title(title: str) -> str:
    """Clave estable para no repetir la misma pieza con otra URL (p. ej. Google News)."""
    return re.sub(r"\s+", " ", re.sub(r"[^\wáéíóúüñ]+", " ", (title or "").lower())).strip()


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "ignore")


MASTODON_ACCOUNTS = (
    ("Electomania", "masto.ai", "109364349372541380"),
)
MASTODON_MIN_DATE = "2026-10-01"


def mastodon_items() -> list[dict]:
    """Posts públicos como senal de descubrimiento. No son datos canonicos."""
    out = []
    for name, host, account_id in MASTODON_ACCOUNTS:
        url = (
            f"https://{host}/api/v1/accounts/{account_id}/statuses"
            "?limit=40&exclude_replies=true"
        )
        try:
            data = json.loads(fetch(url))
        except Exception as e:  # noqa: BLE001
            print(f"[watch] Mastodon {name}: {e}")
            continue
        for status in data:
            created = status.get("created_at") or ""
            if created < MASTODON_MIN_DATE:
                continue
            text = html.unescape(re.sub("<[^>]+>", " ", status.get("content") or ""))
            text = re.sub(r"\s+", " ", text).strip()
            card = status.get("card") or {}
            out.append({
                "title": text,
                "url": (card.get("url") or status.get("url") or "").strip(),
                "pub": status.get("created_at") or "",
                "medio": f"Mastodon · @{name}",
            })
    return out


def known_poll_urls() -> set[str]:
    path = ROOT / "data" / "polls_history.csv"
    if not path.exists():
        return set()
    with path.open(encoding="utf-8", newline="") as f:
        return {(r.get("source_url") or "").strip().rstrip("/") for r in csv.DictReader(f) if r.get("source_url")}


def known_poll_keys() -> set[tuple[str, str]]:
    path = ROOT / "data" / "polls_history.csv"
    if not path.exists():
        return set()
    with path.open(encoding="utf-8", newline="") as f:
        return {(r.get("pollster") or "", r.get("date") or "") for r in csv.DictReader(f)}


def items(xml: str) -> list[dict]:
    try:
        root = ET.fromstring(xml.encode("utf-8"))
    except ET.ParseError:
        return []
    out = []
    for it in root.findall(".//item"):
        title = html.unescape((it.findtext("title") or "").strip())
        link = (it.findtext("link") or "").strip()
        date = (it.findtext("pubDate") or "").strip()
        out.append({"title": title, "url": link, "pub": date})
    return out


def main() -> int:
    rows = []
    for medio, url in FEEDS.items():
        try:
            for it in items(fetch(url)):
                title = it["title"]
                pollster = next((p for p in POLLSTERS if p.lower() in title.lower()), "")
                is_poll_url = "/encuestas/" in it["url"].lower() or "/encuesta/" in it["url"].lower()
                if not ((SIGNAL.search(title) or pollster or is_poll_url) and ELECTION.search(title)):
                    continue
                rows.append({
                    "detectado": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
                    "medio": medio,
                    "pollster": pollster,
                    "titulo": title,
                    "url": it["url"],
                    "pub": it["pub"],
                    "estado": "pendiente_revision",
                })
        except Exception as e:  # noqa: BLE001
            print(f"[watch] {medio}: {e}")
    for it in mastodon_items():
        title = it["title"]
        pollster = next((p for p in POLLSTERS if p.lower() in title.lower()), "")
        is_poll_url = "/encuesta/" in it["url"].lower() or "/encuestas/" in it["url"].lower()
        if (SIGNAL.search(title) or pollster or is_poll_url) and ELECTION.search(title):
            rows.append({
                "detectado": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
                "medio": it["medio"],
                "pollster": pollster,
                "titulo": title,
                "url": it["url"],
                "pub": it["pub"],
                "estado": "pendiente_revision",
            })
    # dedup por URL estable
    seen = set()
    seen_titles = set()
    known_urls = known_poll_urls()
    known_keys = known_poll_keys()
    if OUT.exists():
        with OUT.open(encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                seen.add(hashlib.sha256((r.get("url") or "").encode()).hexdigest())
                seen_titles.add(norm_title(r.get("titulo") or ""))
    new = []
    for r in rows:
        key = hashlib.sha256(r["url"].encode()).hexdigest()
        tkey = norm_title(r["titulo"])
        key_poll = (r.get("pollster") or "", (r.get("pub") or "")[:10])
        if (
            r["url"].rstrip("/") in known_urls
            or (key_poll[0] and key_poll in known_keys)
            or key in seen
            or tkey in seen_titles
        ):
            continue
        seen.add(key)
        seen_titles.add(tkey)
        new.append(r)
    if new:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        fields = ["detectado", "medio", "pollster", "titulo", "url", "pub", "estado"]
        write_header = not OUT.exists()
        with OUT.open("a", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            if write_header:
                w.writeheader()
            w.writerows(new)
    print(f"[watch] {len(rows)} candidatos · {len(new)} nuevos · cola {OUT}")
    if new:
        for r in new:
            print(f"  - {r['medio']} · {r['pollster'] or 'casa por identificar'} · {r['titulo'][:120]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
