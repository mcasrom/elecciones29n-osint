#!/usr/bin/env python3
"""Tarjeta 1200x630 de robustez del dato (para RRSS).

Uso: /usr/bin/python3 gen/gen_card_robustez.py --data web/data/latest.json --out web/og-robustez.png
"""
from __future__ import annotations

import argparse
import json
import os

from PIL import Image, ImageDraw, ImageFont

BG = (15, 16, 38)
PANEL = (24, 26, 54)
PANEL2 = (31, 34, 66)
FG = (238, 240, 246)
MUTED = (167, 171, 196)
ACCENT = (255, 90, 31)
OK = (61, 220, 151)
LINE = (48, 52, 88)


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


def fmt(v, dec=0):
    if v is None:
        return "—"
    s = f"{v:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="web/data/latest.json")
    ap.add_argument("--out", default="web/og-robustez.png")
    a = ap.parse_args()

    with open(a.data, encoding="utf-8") as f:
        d = json.load(f)
    h = d.get("health") or {}
    parties = {p["party"]: p for p in d.get("parties", [])}

    img = Image.new("RGB", (1200, 630), BG)
    # halo suave sobre capa RGBA (en RGB el alfa se ignora y sale un circulo solido)
    overlay = Image.new("RGBA", (1200, 630), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for r in range(420, 0, -10):
        alpha = int(16 * (1 - r / 420) ** 2)
        od.ellipse([960 - r, -180 - r, 960 + r, -180 + r], fill=(255, 90, 31, alpha))
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    dr = ImageDraw.Draw(img)

    # cabecera
    dr.rectangle([0, 0, 10, 630], fill=ACCENT)
    dr.text((52, 38), "elecciones29n-osint", font=font(28, True), fill=FG)
    dr.text((52, 76), "Robustez del dato · sondeos 29N 2026", font=font(22), fill=MUTED)

    dr.text((52, 132), "Lo que sostiene la media", font=font(58, True, serif=True), fill=FG)
    dr.rectangle([54, 206, 190, 211], fill=ACCENT)
    dr.text((52, 226), "Cinco indicadores descriptivos. Sin nota agregada, sin pronóstico.",
            font=font(23), fill=MUTED)

    # cinco tarjetas
    tiles = [
        (fmt(h.get("n_polls")), "sondeos"),
        (fmt(h.get("n_pollsters")), "casas"),
        (fmt(h.get("days_since_last")), "días desde el último"),
        (fmt(h.get("sample_pct")) + "%", "con muestra declarada"),
        (fmt(h.get("dispersion_iqr"), 1) + " pp", "dispersión (IQR)"),
    ]
    x0, y0, gap, tw, th = 52, 300, 14, 208, 128
    for i, (val, lab) in enumerate(tiles):
        x = x0 + i * (tw + gap)
        dr.rounded_rectangle([x, y0, x + tw, y0 + th], radius=14, fill=PANEL, outline=LINE, width=1)
        dr.text((x + 16, y0 + 18), val, font=font(38, True), fill=OK)
        # etiqueta en dos lineas si hace falta
        f_lab = font(17)
        words = lab.split()
        lineas, cur = [], ""
        for w in words:
            test = (cur + " " + w).strip()
            if dr.textlength(test, font=f_lab) > tw - 32:
                lineas.append(cur)
                cur = w
            else:
                cur = test
        if cur:
            lineas.append(cur)
        for j, ln in enumerate(lineas[:2]):
            dr.text((x + 16, y0 + 68 + j * 21), ln, font=f_lab, fill=MUTED)

    # linea de partidos
    py = 468
    dr.rounded_rectangle([52, py, 760, py + 54], radius=27, fill=PANEL2, outline=LINE, width=1)
    top = []
    for name in ("PP", "PSOE", "VOX"):
        if name in parties:
            top.append(f"{name} {fmt(parties[name]['mean'], 1)} %")
    if top:
        dr.text((76, py + 13), "  ·  ".join(top), font=font(24, True), fill=FG)

    # sello sin pronostico
    dr.rounded_rectangle([790, py, 1148, py + 54], radius=27, outline=OK, width=2, fill=(16, 58, 46))
    dr.text((814, py + 13), "Sin pronóstico · con rango", font=font(22, True), fill=OK)

    # pie
    dr.text((52, 566), "elecciones29n.pruebapublica.com", font=font(21), fill=MUTED)
    dr.text((700, 566), "media de sondeos publicados · no intención de voto",
            font=font(18), fill=(120, 126, 155))

    img.save(a.out, "PNG", optimize=True)
    print("ok", a.out, img.size)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
