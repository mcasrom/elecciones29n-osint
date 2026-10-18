#!/usr/bin/env python3
"""Informe de salud de la muestra a partir de web/data/latest.json."""
from __future__ import annotations

import argparse
import json
import sys

LABELS = {"ok": "Muestra suficiente", "warn": "Muestra frágil", "bad": "Muestra insuficiente"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default="web/data/latest.json")
    ap.add_argument("--strict", action="store_true", help="sale 1 si no es 'ok'")
    a = ap.parse_args()
    try:
        d = json.load(open(a.file, encoding="utf-8"))
    except Exception as e:
        print("error leyendo", a.file, e)
        return 2
    h = d.get("health") or {}
    status = h.get("status", "?")
    print(f"Salud de la muestra: {LABELS.get(status, status)}")
    print(f"  sondeos: {h.get('n_polls')} · encuestadoras: {h.get('n_pollsters')} "
          f"({', '.join(h.get('pollsters') or []) or '—'}) · días desde el último: {h.get('days_since_last')}")
    for r in h.get("reasons") or []:
        print("  -", r)
    if status == "ok":
        print("  OK")
        return 0
    print("  Revisa la rutina semanal: docs/RUTINA-SEMANAL.md")
    return 1 if a.strict else 0


if __name__ == "__main__":
    sys.exit(main())
