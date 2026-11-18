#!/usr/bin/env python3
"""Tarjeta 1200x630 con gráfico real para el working paper de sociología 29N."""
import argparse
import json
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path("/home/deploy/elecciones29n-osint")
W, H = 1200, 630
BG = (15, 16, 38)
PANEL = (24, 26, 54)
GRID = (48, 52, 88)
FG = (238, 240, 246)
MUTED = (167, 171, 196)
ACCENT = (255, 90, 31)
OK = (61, 220, 151)
PSOE = (184, 59, 59)
PP = (47, 109, 179)


def font(size, bold=False, serif=False):
    if serif:
        paths = ["/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf", "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"]
    elif bold:
        paths = ["/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"]
    else:
        paths = ["/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"]
    for path in paths:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def wrap(draw, text, face, width, max_lines):
    words = text.split()
    lines, line = [], ""
    for word in words:
        trial = (line + " " + word).strip()
        if draw.textlength(trial, font=face) <= width:
            line = trial
        else:
            if line:
                lines.append(line)
            line = word
            if len(lines) >= max_lines:
                break
    if line and len(lines) < max_lines:
        lines.append(line)
    if len(lines) == max_lines and len(" ".join(lines)) < len(text):
        lines[-1] = lines[-1].rstrip(" .,;:") + "…"
    return lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="web/og-sociologia-29n-v2.png")
    a = ap.parse_args()
    data = json.loads((ROOT / "data" / "cis_m4_2026.json").read_text(encoding="utf-8"))
    groups = data["edad"]["grupos"]

    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 10, H], fill=ACCENT)
    d.text((52, 32), "elecciones29n-osint · sociología del electorado", font=font(20, True), fill=OK)

    title = wrap(d, "Estructura social del voto de 2023", font(48, True, True), 540, 2)
    y = 80
    for line in title:
        d.text((52, y), line, font=font(48, True, True), fill=FG)
        y += 56
    d.text((52, y + 10), "Edad, sexo y autoubicación ideológica", font=font(22), fill=MUTED)
    d.text((52, y + 44), "CIS 3582 · 5.025 entrevistas", font=font(18, True), fill=MUTED)

    d.rectangle([54, y + 92, 190, y + 97], fill=ACCENT)
    d.text((52, y + 116), "Recuerdo declarado, no voto actual", font=font(22, True), fill=FG)
    d.text((52, y + 150), "ni intención de voto de 2026.", font=font(22, True), fill=FG)
    d.text((52, y + 194), "Sin panel: no se calculan fidelidad, trasvases", font=font(17), fill=MUTED)
    d.text((52, y + 219), "ni perfil del indeciso.", font=font(17), fill=MUTED)

    # Panel + gráfico
    d.rounded_rectangle([650, 108, 1150, 520], radius=16, fill=PANEL, outline=GRID, width=1)
    d.text((678, 130), "PSOE y PP por edad", font=font(20, True), fill=FG)
    d.text((678, 158), "Porcentaje del recuerdo de voto 2023", font=font(14), fill=MUTED)
    d.ellipse([678, 192, 688, 202], fill=PSOE)
    d.text((695, 188), "PSOE", font=font(13), fill=MUTED)
    d.ellipse([758, 192, 768, 202], fill=PP)
    d.text((775, 188), "PP", font=font(13), fill=MUTED)

    left, top, barw = 820, 224, 292
    row_h = 39
    max_pct = 65.0
    for i, g in enumerate(groups):
        yy = top + i * row_h
        label = g["nombre"].replace("De ", "").replace(" años", "")
        d.text((678, yy), label, font=font(12), fill=MUTED)
        for j, (party, color) in enumerate((("PSOE", PSOE), ("PP", PP))):
            value = g["partidos"][party]
            by = yy + j * 13
            d.rectangle([left, by, left + barw, by + 8], fill=GRID)
            if not value.get("suppressed"):
                width = max(2, int(barw * value["pct"] / max_pct))
                d.rectangle([left, by, left + width, by + 8], fill=color)
                d.text((left + barw + 8, by - 4), f'{value["pct"]:.0f}%', font=font(11, True), fill=FG)
            else:
                d.text((left + barw + 8, by - 4), "—", font=font(11, True), fill=MUTED)
    # eje de referencia
    d.text((left, 508), "0 %", font=font(10), fill=MUTED)
    d.text((left + barw - 26, 508), "65 %", font=font(10), fill=MUTED)

    d.text((52, 560), "Sin pronóstico · con fuente, n y límites", font=font(20, True), fill=OK)
    d.text((52, 594), "elecciones29n.pruebapublica.com", font=font(16), fill=MUTED)
    d.text((880, 594), "datos abiertos · CC BY", font=font(14), fill=(126, 140, 160))

    img.save(a.out, "PNG", optimize=True)
    print("ok", a.out)


if __name__ == "__main__":
    main()
