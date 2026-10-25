#!/usr/bin/env python3
"""Tarjeta OG 1200x630 del hemiciclo simulado (29N).

Uso: /usr/bin/python3 gen/gen_card_hemiciclo.py --data web/data/latest.json --out web/og-hemiciclo.png
"""
from __future__ import annotations

import argparse
import json
import math
import os
from datetime import datetime

from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 630
BG = (15, 16, 38)
PANEL = (24, 26, 54)
FG = (238, 240, 246)
MUTED = (167, 171, 196)
ACCENT = (255, 90, 31)
OK = (61, 220, 151)
LINE = (48, 52, 88)
COLORS = {
    "PP": (59, 130, 246),
    "PSOE": (239, 68, 68),
    "VOX": (34, 197, 94),
    "SUMAR": (217, 70, 239),
    "PODEMOS": (124, 58, 237),
    "Otros": (148, 163, 184),
}
ORDER = ["PODEMOS", "SUMAR", "PSOE", "PP", "VOX"]


def font(size, bold=False, serif=False):
    if serif:
        cands = [
            "/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
        ]
    elif bold:
        cands = [
            "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ]
    else:
        cands = [
            "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
    for c in cands:
        if os.path.exists(c):
            return ImageFont.truetype(c, size)
    return ImageFont.load_default()


def fmt_date(iso):
    try:
        d = datetime.strptime(str(iso)[:10], "%Y-%m-%d")
        return f"{d.day} {['ene','feb','mar','abr','may','jun','jul','ago','sep','oct','nov','dic'][d.month-1]} {d.year}"
    except Exception:
        return str(iso)


def rows(total=350, nrows=9, inner=50.0, outer=150.0, cx=850.0, cy=545.0):
    radii = [inner + i * (outer - inner) / (nrows - 1) for i in range(nrows)]
    raw = [total * r / sum(radii) for r in radii]
    counts = [int(x) for x in raw]
    falta = total - sum(counts)
    for i in sorted(range(nrows), key=lambda i: raw[i] - counts[i], reverse=True)[:falta]:
        counts[i] += 1
    out = []
    for r, n in zip(radii, counts):
        row = []
        for i in range(n):
            ang = math.pi - (i + 0.5) * math.pi / n
            row.append((cx + r * math.cos(ang), cy - r * math.sin(ang)))
        out.append(row)
    return out


def order_for(seats):
    left = [p for p in ("PODEMOS", "SUMAR", "PSOE") if seats.get(p)]
    right = [p for p in ("PP", "VOX") if seats.get(p)]
    center = sorted(
        [p for p, n in seats.items() if n and p not in left + right],
        key=lambda p: (-seats[p], p),
    )
    return left + center + right


def alloc_rows(seats, row_sizes):
    order = order_for(seats)
    remaining = dict(seats)
    out = []
    for idx, n in enumerate(row_sizes):
        if idx == len(row_sizes) - 1:
            block = {p: remaining[p] for p in order if remaining.get(p)}
        else:
            remtot = sum(remaining.values())
            q = {p: n * remaining.get(p, 0) / remtot for p in order}
            block = {p: int(math.floor(q[p])) for p in order}
            left = n - sum(block.values())
            for p in sorted(order, key=lambda p: (q[p] - block[p], -order.index(p)), reverse=True)[:left]:
                block[p] += 1
        for p in order:
            remaining[p] -= block.get(p, 0)
        out.append({p: k for p, k in block.items() if k})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="web/data/latest.json")
    ap.add_argument("--out", default="web/og-hemiciclo.png")
    a = ap.parse_args()

    with open(a.data, encoding="utf-8") as f:
        data = json.load(f)
    h = data["hemicycle"][-1]
    seats = {str(s["party"]): int(s["seats"]) for s in h.get("seats", []) if int(s.get("seats") or 0) > 0}
    total = sum(seats.values())
    if total < 350:
        seats["Otros"] = seats.get("Otros", 0) + 350 - total
    elif total > 350:
        seats = {p: n for p, n in seats.items() if n}
    seats = {p: n for p, n in seats.items() if n}
    right = sum(seats.get(p, 0) for p in ("PP", "VOX"))
    left = sum(seats.get(p, 0) for p in ("PSOE", "SUMAR", "PODEMOS"))
    n_polls = h.get("n_polls", 0)
    n_houses = h.get("n_houses", 0)
    date = fmt_date(h.get("date", ""))
    window = h.get("window_start", "")
    majority = h.get("majority", "")
    right_need = max(0, 176 - right)
    left_need = max(0, 176 - left)

    img = Image.new("RGB", (W, H), BG)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    for r in range(460, 0, -10):
        alpha = int(15 * (1 - r / 460) ** 2)
        od.ellipse([1040 - r, 80 - r, 1040 + r, 80 + r], fill=(255, 90, 31, alpha))
    img = Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")
    d = ImageDraw.Draw(img)

    d.rectangle([0, 0, 10, H], fill=ACCENT)
    d.text((52, 36), "elecciones29n-osint", font=font(28, True), fill=FG)
    d.text((52, 74), "Hemiciclo simulado · Elecciones Generales 29N 2026", font=font(22), fill=MUTED)

    d.text((52, 122), "350 escaños, fecha a fecha", font=font(54, True, serif=True), fill=FG)
    d.rectangle([54, 196, 190, 201], fill=ACCENT)
    d.text((52, 214), "D'Hondt nacional sobre la media · simulación mecánica, no proyección",
           font=font(21), fill=MUTED)
    d.text((52, 250), f"Último dato: {date} · {n_polls} sondeos · {n_houses} casas",
           font=font(20, True), fill=OK)

    # Bloques
    bx, by, bw, bh = 52, 300, 262, 118
    right_win = majority == "right"
    left_win = majority == "left"
    d.rounded_rectangle([bx, by, bx + bw, by + bh], radius=14, fill=PANEL,
                        outline=ACCENT if right_win else LINE, width=2 if right_win else 1)
    d.text((bx + 18, by + 14), "PP + VOX", font=font(19, True), fill=MUTED)
    d.text((bx + 18, by + 40), str(right), font=font(50, True), fill=ACCENT if right_win else FG)
    d.text((bx + 18, by + 92),
           "mayoría en la simulación" if right_win else f"a {right_need} de 176",
           font=font(15), fill=MUTED)

    bx2 = 340
    d.rounded_rectangle([bx2, by, bx2 + bw, by + bh], radius=14, fill=PANEL,
                        outline=ACCENT if left_win else LINE, width=2 if left_win else 1)
    d.text((bx2 + 18, by + 14), "PSOE + Sumar", font=font(19, True), fill=MUTED)
    d.text((bx2 + 18, by + 40), str(left), font=font(50, True), fill=ACCENT if left_win else FG)
    d.text((bx2 + 18, by + 92),
           "mayoría en la simulación" if left_win else f"a {left_need} de 176",
           font=font(15), fill=MUTED)

    # Leyenda de partidos
    lx, ly = 52, 452
    for p in ("PP", "PSOE", "VOX", "SUMAR"):
        if p not in seats:
            continue
        c = COLORS.get(p, COLORS["Otros"])
        d.ellipse([lx, ly + 4, lx + 12, ly + 16], fill=c)
        label = f"{p} {seats[p]}"
        d.text((lx + 18, ly), label, font=font(20, True), fill=FG)
        lx += 18 + int(d.textlength(label, font=font(20, True))) + 22

    # Mini hemiciclo
    row_pos = rows()
    blocks = alloc_rows(seats, [len(r) for r in row_pos])
    order = order_for(seats)
    for positions, block in zip(row_pos, blocks):
        seq = []
        for p in order:
            seq.extend([p] * block.get(p, 0))
        for (x, y), p in zip(positions, seq):
            c = COLORS.get(p, COLORS["Otros"])
            d.ellipse([x - 3.2, y - 3.2, x + 3.2, y + 3.2], fill=c)
    d.text((700, 566), "Izquierda", font=font(15), fill=MUTED)
    d.text((1000, 566), "Derecha", font=font(15), fill=MUTED, anchor="ra")

    d.rectangle([52, 586, 1148, 587], fill=LINE)
    d.text((52, 600), "No es una proyección ni el Congreso real", font=font(20, True), fill=FG)
    d.text((1148, 602), "elecciones29n.pruebapublica.com/hemiciclo.html",
           font=font(17), fill=MUTED, anchor="ra")

    img.save(a.out, "PNG", optimize=True)
    print("ok", a.out)


if __name__ == "__main__":
    main()
