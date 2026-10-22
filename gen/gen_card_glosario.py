#!/usr/bin/env python3
"""Tarjeta 1200x630: glosario + ficha por provincia (29N)."""
import argparse
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 630
BG = (15, 16, 38)
PANEL = (24, 26, 54)
FG = (238, 240, 246)
MUTED = (167, 171, 196)
ACCENT = (255, 90, 31)
OK = (61, 220, 151)
LINE = (48, 52, 88)


def f(size, bold=False, serif=False):
    if serif:
        c = ["/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf",
             "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"]
    elif bold:
        c = ["/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
             "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"]
    else:
        c = ["/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
             "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"]
    for p in c:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


img = Image.new("RGB", (W, H), BG)
ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
od = ImageDraw.Draw(ov)
for r in range(420, 0, -10):
    a = int(14 * (1 - r / 420) ** 2)
    od.ellipse([980 - r, -200 - r, 980 + r, -200 + r], fill=ACCENT + (a,))
img = Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")
d = ImageDraw.Draw(img)

d.rectangle([0, 0, 10, H], fill=ACCENT)
d.text((52, 36), "elecciones29n-osint", font=f(28, True), fill=FG)
d.text((52, 74), "Glosario y ficha por provincia", font=f(52, True, serif=True), fill=FG)
d.rectangle([54, 150, 190, 155], fill=ACCENT)
d.text((52, 174), "Dos formas nuevas de entrar en los datos del 29N", font=f(24), fill=MUTED)

tiles = [("30+", "términos"), ("52", "provincias"), ("2026", "censo y escaños"), ("2023", "resultado")]
x0, y0, gap, tw, th = 52, 250, 14, 262, 120
for i, (v, lab) in enumerate(tiles):
    x = x0 + i * (tw + gap)
    d.rounded_rectangle([x, y0, x + tw, y0 + th], radius=14, fill=PANEL, outline=LINE, width=1)
    d.text((x + 16, y0 + 18), v, font=f(38, True), fill=OK)
    d.text((x + 16, y0 + 74), lab, font=f(17), fill=MUTED)

d.text((52, 420), "Sondeo · muestra · IQR · D'Hondt · blackout", font=f(21), fill=FG)
d.text((52, 456), "Censo, escaños y participación por provincia", font=f(21), fill=FG)
d.text((52, 520), "Sin pronóstico · con fuente y fecha", font=f(22, True), fill=OK)

d.text((52, 574), "elecciones29n.pruebapublica.com", font=f(20), fill=MUTED)
d.text((820, 574), "datos abiertos · CC BY", font=f(17), fill=(126, 140, 160))

ap = argparse.ArgumentParser()
ap.add_argument("--out", default="web/og-glosario.png")
a = ap.parse_args()
img.save(a.out, "PNG", optimize=True)
print("ok")
