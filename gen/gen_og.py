#!/usr/bin/env python3
"""Genera web/og.png (1200x630) con la media agregada. Usa PIL del sistema."""
from __future__ import annotations

import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont


OUT = "web/og.png"  # se puede cambiar con --out
BG = (15, 16, 38)
FG = (231, 231, 234)
MUTED = (185, 185, 195)
ACCENT = (255, 90, 31)
OK = (61, 220, 151)


def find_font(size: int, bold: bool = False):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for c in candidates:
        if os.path.exists(c):
            return ImageFont.truetype(c, size)
    return ImageFont.load_default()


def main() -> int:
    global OUT
    data = {"parties": [], "updated_at": ""}
    latest_src = os.path.join(os.path.dirname(OUT), "data/latest.json")
    if os.path.exists(latest_src):
        with open(latest_src, encoding="utf-8") as f:
            data = json.load(f)

    img = Image.new("RGB", (1200, 630), BG)
    d = ImageDraw.Draw(img)

    # barra de acento
    d.rectangle([0, 0, 1200, 10], fill=ACCENT)

    # marca
    d.text((56, 44), "elecciones29n-osint", font=find_font(30, True), fill=FG)
    d.text((56, 86), "Media agregada de sondeos · Elecciones Generales 29N 2026", font=find_font(24), fill=MUTED)

    # cifras
    parties = data.get("parties", [])[:4]
    y = 170
    if parties:
        for i, p in enumerate(parties):
            name = str(p.get("party", "?"))
            mean = p.get("mean", 0)
            lo = p.get("min", mean)
            hi = p.get("max", mean)
            n = p.get("n", 0)
            d.text((56, y), name, font=find_font(34, True), fill=FG)
            d.text((300, y - 2), f"{mean:.1f}%", font=find_font(34, True), fill=ACCENT)
            d.text((470, y + 4), f"rango {lo:.1f}–{hi:.1f} · n={n}", font=find_font(22), fill=MUTED)
            y += 62
    else:
        d.text((56, 200), "Sin datos en la ventana de 14 días", font=find_font(28), fill=MUTED)

    # pie
    d.rectangle([56, 486, 1144, 488], fill=(42, 43, 69))
    d.text((56, 510), "No es un pronóstico: es media con rango mínimo–máximo.", font=find_font(26, True), fill=FG)
    d.text((56, 552), "Datos abiertos · AGPL-3.0 · Miguel Castillo", font=find_font(20), fill=MUTED)
    d.text((760, 552), "elecciones29n.pruebapublica.com", font=find_font(20), fill=OK)

    os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
    img.save(OUT, optimize=True)
    print("og ok", OUT)
    return 0


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="web/og.png")
    a = ap.parse_args()
    OUT = a.out
    sys.exit(main())
