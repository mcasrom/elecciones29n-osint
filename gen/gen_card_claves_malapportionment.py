#!/usr/bin/env python3
"""Tarjeta 1200x630: coste de escaño (malapportionment), Claves 29N."""
from __future__ import annotations

import argparse
import json
import os

from PIL import Image, ImageDraw, ImageFont

BG = (15, 16, 38)
PANEL = (24, 26, 54)
FG = (238, 240, 246)
MUTED = (167, 171, 196)
ACCENT = (255, 90, 31)
OK = (61, 220, 151)
LINE = (48, 52, 88)
TRACK = (38, 42, 74)


def font(size, bold=False, serif=False):
    cands = []
    if serif:
        cands += ["/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf",
                  "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"]
    if bold:
        cands += ["/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
                  "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
                  "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]
    else:
        cands += ["/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
                  "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                  "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
    for c in cands:
        if os.path.exists(c):
            return ImageFont.truetype(c, size)
    return ImageFont.load_default()


def fmt(n):
    return f"{n:,.0f}".replace(",", ".")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/escanos_2026.json")
    ap.add_argument("--out", default="web/og-claves-malapportionment.png")
    a = ap.parse_args()
    d = json.load(open(a.data, encoding="utf-8"))
    by = {p["nombre"]: p for p in d["provincias"]}
    teruel = by["Teruel"]
    madrid = by["Madrid"]
    ratio = madrid["electores_por_escanos"] / teruel["electores_por_escanos"]

    img = Image.new("RGB", (1200, 630), BG)
    ov = Image.new("RGBA", (1200, 630), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    for r in range(460, 0, -10):
        alpha = int(16 * (1 - r / 460) ** 2)
        od.ellipse([1080 - r, -210 - r, 1080 + r, -210 + r], fill=(255, 90, 31, alpha))
    img = Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")
    dr = ImageDraw.Draw(img)
    dr.rectangle([0, 0, 10, 630], fill=ACCENT)
    dr.text((52, 34), "elecciones29n-osint", font=font(28, True), fill=FG)
    dr.text((52, 72), "Claves 29N · estructura del sistema", font=font(21), fill=MUTED)

    dr.text((52, 150), "El coste de un escaño", font=font(52, True, serif=True), fill=FG)
    dr.rectangle([54, 205, 190, 210], fill=ACCENT)
    dr.text((52, 218), "no es igual en todas las provincias", font=font(27), fill=MUTED)

    dr.text((52, 255), f"{ratio:.1f}×".replace(".", ","), font=font(100, True), fill=OK)
    dr.text((330, 270), "menos electores por escaño", font=font(29, True), fill=FG)
    dr.text((330, 310), "en Teruel que en Madrid", font=font(25), fill=MUTED)

    # barras
    x0, x1 = 52, 1148
    maxv = madrid["electores_por_escanos"]
    for i, (p, color, label) in enumerate([
        (teruel, OK, "Teruel"),
        (madrid, ACCENT, "Madrid"),
    ]):
        y = 390 + i * 50
        w = max(8, int((x1 - x0) * p["electores_por_escanos"] / maxv))
        dr.text((x0, y - 26), label, font=font(20, True), fill=FG)
        dr.text((x1, y - 26), f"{fmt(p['electores_por_escanos'])} electores/escaño", font=font(19), fill=MUTED, anchor="ra")
        dr.rounded_rectangle([x0, y, x1, y + 20], radius=10, fill=TRACK, outline=LINE, width=1)
        dr.rounded_rectangle([x0, y, x0 + w, y + 20], radius=10, fill=color)

    dr.text((52, 520), "No es un voto ponderado: es coste de escaño.", font=font(22, True), fill=FG)
    dr.text((52, 570), "elecciones29n.pruebapublica.com/claves.html", font=font(18), fill=MUTED)
    img.save(a.out, "PNG", optimize=True)
    print("ok", a.out, img.size)


if __name__ == "__main__":
    main()
