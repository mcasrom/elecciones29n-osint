#!/usr/bin/env python3
"""Genera OG 1200x630 por circunscripción (resultado oficial 2023)."""
from __future__ import annotations

import argparse
import json
import os
import sys
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from gen import circunscripciones  # noqa: E402

W, H = 1200, 630
BG = (15, 16, 38)
PANEL = (24, 26, 54)
FG = (238, 240, 246)
MUTED = (167, 171, 196)
ACCENT = (255, 90, 31)
OK = (61, 220, 151)
LINE = (48, 52, 88)


def font(size, bold=False, serif=False):
    if serif:
        cands = ["/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf",
                 "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"]
    elif bold:
        cands = ["/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
                 "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
                 "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]
    else:
        cands = ["/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
                 "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                 "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
    for c in cands:
        if os.path.exists(c):
            return ImageFont.truetype(c, size)
    return ImageFont.load_default()


def fmt_int(n):
    if n is None:
        return "—"
    return f"{int(n):,}".replace(",", ".")


def fmt_pct(n):
    if n is None:
        return "—"
    return f"{n:.2f}".replace(".", ",")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="web/og")
    ap.add_argument("--slug", help="genera solo una provincia")
    a = ap.parse_args()

    oficial = json.loads((ROOT / "data/congreso-oficial.json").read_text(encoding="utf-8"))
    escanos = json.loads((ROOT / "data/escanos_2026.json").read_text(encoding="utf-8"))
    censo = {}
    cp = ROOT / "data/censo_2026.json"
    if cp.exists():
        censo = json.loads(cp.read_text(encoding="utf-8"))
    pages = circunscripciones.build_pages(oficial, escanos, censo)
    out = ROOT / a.out if not os.path.isabs(a.out) else Path(a.out)
    out.mkdir(parents=True, exist_ok=True)

    for p in pages:
        if a.slug and p["slug"] != a.slug:
            continue
        img = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(img)
        d.rectangle([0, 0, 10, H], fill=ACCENT)
        d.text((52, 36), "elecciones29n-osint", font=font(28, True), fill=FG)
        d.text((52, 74), "29N · Elecciones generales · 29 de noviembre de 2026", font=font(21), fill=MUTED)

        name = p.get("nombre") or "?"
        size = 58 if len(name) <= 22 else 46
        lines = textwrap.wrap(name, width=26 if size == 58 else 30)[:2]
        y = 122
        for ln in lines:
            d.text((52, y), ln, font=font(size, True, serif=True), fill=FG)
            y += size + 8
        d.rectangle([54, y + 4, 190, y + 9], fill=ACCENT)
        y += 28

        seats = p.get("escanos_2026")
        elect = p.get("electores_2026")
        part = p.get("participacion_2023")
        d.text((52, y), f"{seats or '—'}", font=font(54, True), fill=ACCENT)
        d.text((52, y + 62), "diputados", font=font(20), fill=MUTED)
        d.text((300, y), fmt_int(elect), font=font(40, True), fill=FG)
        d.text((300, y + 58), "electores 2026", font=font(20), fill=MUTED)
        d.text((660, y), f"{fmt_pct(part)}%", font=font(40, True), fill=OK)
        d.text((660, y + 58), "participación 2023", font=font(20), fill=MUTED)

        res = (p.get("resultados") or [{}])[0]
        cands = sorted(res.get("candidaturas") or [], key=lambda c: -c.get("votos", 0))
        top = cands[:2]
        if len(top) >= 2:
            v1, v2 = top[0].get("votos", 0), top[1].get("votos", 0)
            validos = res.get("validos") or sum(c.get("votos", 0) for c in cands) or 1
            marg = 100.0 * (v1 - v2) / validos
            d.text((52, 430), f"2023: {top[0].get('acronimo')} {top[0].get('escanos', 0)} · {top[1].get('acronimo')} {top[1].get('escanos', 0)}", font=font(26, True), fill=FG)
            d.text((52, 468), f"Margen entre los dos primeros: {fmt_pct(marg)} pp", font=font(22), fill=MUTED)
        mar = (p.get("marginales") or {}).get("2023-07-23") or {}
        if mar.get("ultimo"):
            u = mar["ultimo"]
            label = (u.get("etiqueta") or "").split(" - ")[-1][:28]
            if mar.get("margen_votos") is not None:
                txt = f"Último escaño 2023: {label} por {fmt_int(mar.get('margen_votos'))} votos"
            else:
                txt = f"Último escaño 2023: {label} · sin siguiente"
            d.text((52, 512), txt, font=font(20), fill=MUTED)

        d.rectangle([52, 574, 1148, 575], fill=LINE)
        d.text((52, 590), "Resultado oficial 2023 · no es una proyección", font=font(19, True), fill=FG)
        d.text((1148, 592), "elecciones29n.pruebapublica.com", font=font(16), fill=MUTED, anchor="ra")

        path = out / f"provincia-{p['slug']}.png"
        img.save(path, "PNG", optimize=True)
        print("og", path.name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
