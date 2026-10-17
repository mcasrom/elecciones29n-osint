#!/usr/bin/env python3
"""Envía las URLs del sitemap a IndexNow (Bing/Yandex/Seznam)."""
from __future__ import annotations

import json
import sys
import urllib.request
import xml.etree.ElementTree as ET

SITE = "https://elecciones29n.pruebapublica.com"
SITEMAP = "web/sitemap.xml"
KEY_FILE = "gen/build.py"


def read_key() -> str:
    import re

    with open(KEY_FILE, encoding="utf-8") as f:
        m = re.search(r'INDEXNOW_KEY = "([^"]+)"', f.read())
    if not m:
        raise SystemExit("no INDEXNOW_KEY en gen/build.py")
    return m.group(1)


def urls() -> list[str]:
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    tree = ET.parse(SITEMAP)
    return [u.text.strip() for u in tree.getroot().findall(".//s:loc", ns) if u.text]


def main() -> int:
    key = read_key()
    host = SITE.split("//", 1)[1].split("/", 1)[0]
    payload = {
        "host": host,
        "key": key,
        "keyLocation": f"{SITE}/{key}.txt",
        "urlList": urls(),
    }
    req = urllib.request.Request(
        "https://api.indexnow.org/indexnow",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            print(f"indexnow {r.status} · {len(payload['urlList'])} URLs")
        return 0
    except urllib.error.HTTPError as e:
        print(f"indexnow HTTP {e.code}: {e.read()[:200]!r}")
        return 1
    except Exception as e:
        print(f"indexnow error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
