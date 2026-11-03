#!/usr/bin/env python3
"""OG 1200x630 para la referencia de Onda Cero (29N)."""
from __future__ import annotations

import argparse
import os

from PIL import Image, ImageDraw, ImageFont

BG = (15, 16, 38)
PANEL = (24, 26, 54)
FG = (238, 240, 246)
MUTED = (185, 189, 210)
ACCENT = (255, 90, 31)
OK = (61, 220, 151)
LINE = (48, 52, 88)


def font(size, bold=False, serif=False):
    cands = []
    if serif:
        cands += ["/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"]
    if bold:
        cands += ["/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"]
    else:
        cands += ["/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"]
    for c in cands:
        if os.path.exists(c):
            return ImageFont.truetype(c, size)
    return ImageFont.load_default()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="web/og-ondacero-guias.png")
    a = ap.parse_args()
    img = Image.new("RGB", (1200, 630), BG)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 12, 630], fill=ACCENT)
    d.rectangle([0, 0, 1200, 8], fill=ACCENT)

    d.text((52, 38), "elecciones29n-osint", font=font(28, True), fill=FG)
    d.text((52, 76), "Referencia externa · 29N 2026", font=font(22), fill=MUTED)
    d.text((52, 132), "Guías prácticas", font=font(60, True, serif=True), fill=FG)
    d.rectangle([54, 208, 190, 213], fill=ACCENT)
    d.text((52, 230), "Mesa electoral, sorteo, retribución y plazos", font=font(30, True), fill=FG)
    d.text((52, 274), "Onda Cero reúne las piezas prácticas del 29N.", font=font(24), fill=MUTED)

    items = [("01", "Mesa electoral"), ("02", "Sorteo"), ("03", "Retribución"), ("04", "Plazos")]
    y = 348
    for n, label in items:
        d.rounded_rectangle([52, y, 1148, y + 54], radius=10, fill=PANEL, outline=LINE)
        d.text((76, y + 11), n, font=font(24, True), fill=ACCENT)
        d.text((132, y + 11), label, font=font(26, True), fill=FG)
        y += 64

    d.text((52, 574), "No es un dato del observatorio: enlace a la fuente.", font=font(22), fill=MUTED)
    d.text((875, 574), "elecciones29n.pruebapublica.com", font=font(18), fill=OK)
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    img.save(a.out, optimize=True)
    print("og ok", a.out, img.size)


if __name__ == "__main__":
    main()
