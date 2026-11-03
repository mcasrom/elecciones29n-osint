#!/usr/bin/env python3
"""Vigila piezas de 40dB sobre valoración de líderes.

No publica ni importa datos. Deja candidatos en CSV y avisa al dueño por
Telegram. La primera pasada solo siembra el estado para no enviar histórico.
"""
import csv
import hashlib
import html
import json
import os
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
QUERIES = [
    'site:elpais.com "40dB" "valoración" "líderes"',
    'site:40db.es "valoración" "líderes"',
    '"40dB" "barómetro" "líderes" 29N',
    '"40dB" "nota" "líderes" España',
]
STATE = ROOT / "data/lideres_40db_state.json"
QUEUE = ROOT / "data/candidatos_lideres.csv"
ENV = Path(os.environ.get("FIMI_ENV", "/home/deploy/hybrid-fimi-radar/.env"))
OWNER = os.environ.get("FIMI_OWNER_CHAT", "47652516")


def load_env(path):
    try:
        for line in path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())
    except OSError:
        pass


def fetch(query):
    url = "https://news.google.com/rss/search?" + urllib.parse.urlencode(
        {"q": query, "hl": "es", "gl": "ES", "ceid": "ES:es"}
    )
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=25) as r:
        return ET.fromstring(r.read())


def candidate(item):
    title = (item.findtext("title") or "").strip()
    link = (item.findtext("link") or "").strip()
    pub = (item.findtext("pubDate") or "").strip()
    if not title or not link:
        return None
    low = title.lower()
    if "40db" not in low:
        return None
    if not any(x in low for x in ("valoraci", "lider", "líder", "barometro", "barómetro", "nota")):
        return None
    source = (item.findtext("source") or "").strip() or "Google News"
    key = hashlib.sha256((title + "|" + pub).encode()).hexdigest()[:20]
    return {"key": key, "title": title, "url": link, "pub": pub, "source": source}


def notify(text):
    token = os.environ.get("FIMI_TELEGRAM_BOT_TOKEN", "")
    if not token or ":" not in token:
        print("[watch40] sin token; no se avisa", file=sys.stderr)
        return False
    data = urllib.parse.urlencode({
        "chat_id": OWNER, "text": text, "parse_mode": "HTML",
        "disable_web_page_preview": "true",
    }).encode()
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage", data=data
    )
    try:
        urllib.request.urlopen(req, timeout=20).read()
        return True
    except Exception as exc:
        print(f"[watch40] telegram: {type(exc).__name__}", file=sys.stderr)
        return False


def main(dry=False):
    load_env(ENV)
    state = {"seen": []}
    if STATE.exists():
        try:
            state = json.loads(STATE.read_text())
        except Exception:
            pass
    seen = set(state.get("seen", []))
    first = not seen
    found = []
    for q in QUERIES:
        try:
            root = fetch(q)
        except Exception as exc:
            print(f"[watch40] {q}: {type(exc).__name__}", file=sys.stderr)
            continue
        for item in root.findall("./channel/item")[:12]:
            c = candidate(item)
            if c and c["key"] not in seen:
                found.append(c)
    # dedup por key
    unique = {c["key"]: c for c in found}
    found = list(unique.values())
    if not found:
        print("[watch40] sin novedades")
        return 0
    if first:
        state["seen"] = list(seen | {c["key"] for c in found})[-500:]
        if not dry:
            STATE.parent.mkdir(parents=True, exist_ok=True)
            STATE.write_text(json.dumps(state, ensure_ascii=False))
        print(f"[watch40] primera pasada: {len(found)} piezas sembradas, sin aviso")
        return 0
    write_header = not QUEUE.exists()
    QUEUE.parent.mkdir(parents=True, exist_ok=True)
    with QUEUE.open("a", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        if write_header:
            w.writerow(["detectado", "medio", "titular", "url", "pub", "estado"])
        for c in found:
            w.writerow([datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
                        c["source"], c["title"], c["url"], c["pub"], "pendiente_revision"])
    lines = ["🔎 <b>Posible ficha 40dB · valoración de líderes</b>", ""]
    for c in found[:4]:
        lines.append(f"• {html.escape(c['title'][:180])}")
        lines.append(f"  <a href=\"{html.escape(c['url'])}\">Abrir</a>")
    lines.append("")
    lines.append("No se añade automáticamente. Revisar pregunta, escala, n, campo y tabla.")
    if not dry:
        state["seen"] = list(seen | {c["key"] for c in found})[-500:]
        STATE.write_text(json.dumps(state, ensure_ascii=False))
        notify("\n".join(lines))
    else:
        print("\n".join(lines))
    print(f"[watch40] {len(found)} candidatas")
    return len(found)


if __name__ == "__main__":
    main(dry="--dry" in sys.argv)
