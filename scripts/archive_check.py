#!/usr/bin/env python3
"""Comprueba instantáneas de Archive.org del observatorio 29N. Solo lectura.

Uso: python3 scripts/archive_check.py
Salida: 0 = sin instantáneas; 1 = hay instantáneas; 2 = consulta incompleta.
"""
from __future__ import annotations

import json
import sys
import urllib.error
import urllib.parse
import urllib.request

DOMAIN = "elecciones29n.pruebapublica.com"
PATHS = ["", "data/latest.json", "data/robustez.json", "og.png",
         "og-hemiciclo.png", "og-robustez.png", "hemiciclo.html", "robustez.html"]
UA = "Mozilla/5.0 (compatible; 29N-archive-check/1.0)"
TIMEOUT = 25


def get(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")
    except Exception as e:
        return None, str(e)


def cdx(path: str):
    url = "https://web.archive.org/cdx/search/cdx?" + urllib.parse.urlencode({
        "url": DOMAIN + ("/" + path if path else ""),
        "output": "json",
        "fl": "timestamp,original,statuscode,mimetype",
        "filter": "statuscode:200",
        "limit": "50",
    })
    code, body = get(url)
    if code != 200:
        return None, f"HTTP {code}: {body[:120]}"
    try:
        rows = json.loads(body)
    except Exception:
        return None, f"respuesta no JSON: {body[:120]}"
    return rows[1:] if rows else [], None


def main() -> int:
    errors = []
    found = []
    print(f"dominio: {DOMAIN}\n")
    for path in PATHS:
        rows, err = cdx(path)
        label = "/" + path if path else "/"
        if err:
            errors.append(f"{label}: {err}")
            print(f"ERROR  {label:28} {err}")
            continue
        if rows:
            for r in rows:
                found.append((label, r[0], r[1], r[2], r[3] if len(r) > 3 else ""))
                print(f"CAPTURA {label:28} {r[0]} {r[1]} {r[2]}")
        else:
            print(f"vacío  {label}")

    # Consulta de disponibilidad (más ligera) como contraste.
    for path in ("", "data/latest.json", "data/robustez.json"):
        u = "https://archive.org/wayback/available?" + urllib.parse.urlencode({
            "url": DOMAIN + ("/" + path if path else "")
        })
        code, body = get(u)
        if code != 200:
            errors.append(f"availability {path or '/'}: HTTP {code}")
        else:
            try:
                snap = json.loads(body).get("archived_snapshots") or {}
                if snap:
                    found.append(("availability", path or "/", json.dumps(snap)[:200], "", ""))
                    print(f"CAPTURA availability {path or '/'}: {snap}")
            except Exception:
                errors.append(f"availability {path or '/'}: JSON inválido")

    print("\nresumen: capturas=%d errores=%d" % (len(found), len(errors)))
    if found:
        return 1
    if errors:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
