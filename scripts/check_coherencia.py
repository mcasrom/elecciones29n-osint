#!/usr/bin/env python3
"""Gate de coherencia 29N: evita publicar páginas con contadores viejos."""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else "web")
    errors: list[str] = []
    latest = json.loads((root / "data" / "latest.json").read_text(encoding="utf-8"))
    robust = json.loads((root / "data" / "robustez.json").read_text(encoding="utf-8"))
    n = int(latest.get("n_polls") or 0)
    h = int((latest.get("health") or {}).get("n_pollsters") or 0)
    if n <= 0:
        errors.append("latest.n_polls vacío")
    if h <= 0:
        errors.append("latest.health.n_pollsters vacío")
    if int(robust.get("n_polls") or 0) != n:
        errors.append(f"robustez.n_polls={robust.get('n_polls')} != latest.n_polls={n}")
    rh = robust.get("health") or {}
    if int(rh.get("n_polls") or 0) != n:
        errors.append(f"robustez.health.n_polls={rh.get('n_polls')} != {n}")
    if int(rh.get("n_pollsters") or 0) != h:
        errors.append(f"robustez.health.n_pollsters={rh.get('n_pollsters')} != {h}")

    expected = f"Media: {n} sondeos · {h} casas"
    for name in ("cis-3584.html", "cis-3584-indecisos.html"):
        p = root / name
        if not p.exists():
            errors.append(f"falta {name}")
            continue
        text = p.read_text(encoding="utf-8")
        if expected not in text:
            errors.append(f"{name}: no contiene «{expected}»")
        if "Media 14 d" not in text:
            errors.append(f"{name}: no contiene «Media 14 d»")

    esc = root / "escenarios.html"
    if esc.exists():
        text = esc.read_text(encoding="utf-8")
        if f"{n} sondeos · {h} casas" not in text:
            errors.append(f"escenarios.html: no muestra la media actual {n}/{h}")

    if errors:
        print("COHERENCIA FALLIDA", file=sys.stderr)
        for e in errors:
            print(f"- {e}", file=sys.stderr)
        return 1
    print(f"coherencia OK · media {n} sondeos · {h} casas")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
