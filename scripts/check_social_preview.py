#!/usr/bin/env python3
"""Comprueba que una URL tiene una tarjeta social válida.

Uso: python3 scripts/check_social_preview.py "https://.../robustez.html?v=..."
Sale 0 si og/twitter card e imagen responden 200. No publica nada.
"""
import re
import sys
import urllib.request

UA = "Twitterbot/1.0"


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.status, r.read().decode("utf-8", "ignore"), r.headers.get("content-type", "")


def meta(html, attr, key):
    m = re.search(
        r"<meta[^>]+" + attr + r"=[\"']" + re.escape(key) + r"[\"'][^>]+content=[\"']([^\"']+)",
        html,
        re.I,
    )
    return m.group(1).strip() if m else ""


def main():
    if len(sys.argv) != 2:
        print("uso: check_social_preview.py <url>")
        return 2
    url = sys.argv[1]
    code, html, _ = get(url)
    card = meta(html, "name", "twitter:card")
    img = meta(html, "name", "twitter:image") or meta(html, "property", "og:image")
    if code != 200:
        print("ERROR url", code)
        return 1
    if card != "summary_large_image":
        print("ERROR twitter:card", repr(card))
        return 1
    if not img:
        print("ERROR sin twitter:image/og:image")
        return 1
    if img.rstrip("/").endswith("og.png") or "og-robustez.png" in img:
        print("ERROR imagen genérica:", img)
        return 1
    icode, _, ctype = get(img)
    if icode != 200 or not ctype.startswith("image/"):
        print("ERROR imagen", icode, ctype, img)
        return 1
    print("OK", card, img)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
