#!/usr/bin/env python3
"""Valida el sitio generado antes de publicarlo.

Si algo falta, sale con código 1 y NO se publica: se conserva la última
versión buena. Evita fallos silenciosos como el gráfico vacío del 18-oct.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import xml.etree.ElementTree as ET

REQUIRED = [
    "index.html", "metodologia.html", "fuentes.html", "about.html", "caveat.html",
    "robots.txt", "sitemap.xml", "llms.txt", "favicon.svg", "og.png",
    "cambios.xml", "data/latest.json", "css/main.css",
    "electorado.html", "data/censo-2026.json", "data/censo-provincias.csv",
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("dir", nargs="?", default="web")
    a = ap.parse_args()
    d = a.dir
    errors: list[str] = []
    warns: list[str] = []

    for f in REQUIRED:
        p = os.path.join(d, f)
        if not os.path.exists(p):
            errors.append(f"falta {f}")
        elif os.path.getsize(p) == 0:
            errors.append(f"{f} vacío")

    idx_path = os.path.join(d, "index.html")
    if os.path.exists(idx_path):
        html = open(idx_path, encoding="utf-8", errors="ignore").read()
        if len(html) < 5000:
            errors.append(f"index.html demasiado pequeño ({len(html)} bytes)")
        if 'class="chart"' not in html:
            errors.append("index.html sin gráfico (class=chart)")
        if html.count("<circle") < 1:
            errors.append("gráfico sin puntos")
        for tab in ("tab-evolucion", "tab-congreso", "tab-senado"):
            if f'id="{tab}"' not in html:
                errors.append(f"falta la pestaña {tab}")
        for meta in ('property="og:image"', 'name="twitter:card"', 'rel="canonical"', "application/ld+json"):
            if meta not in html:
                errors.append(f"falta meta {meta}")
        if "cambios.xml" not in html:
            warns.append("index.html no enlaza cambios.xml")

    data_path = os.path.join(d, "data/latest.json")
    data = {}
    if os.path.exists(data_path):
        try:
            data = json.load(open(data_path, encoding="utf-8"))
        except Exception as e:
            errors.append(f"latest.json inválido: {e}")
        else:
            if not data.get("parties"):
                errors.append("latest.json sin partidos")
            if not data.get("updated_at_iso"):
                errors.append("latest.json sin updated_at_iso")
            if not data.get("series_long"):
                errors.append("latest.json sin series_long")
            if int(data.get("n_polls", 0)) < 1:
                errors.append("latest.json sin sondeos (n_polls=0)")
            if data.get("parties") and "class=\"spark\"" not in (open(idx_path, encoding="utf-8", errors="ignore").read() if os.path.exists(idx_path) else ""):
                errors.append("index.html sin minigráficos (spark)")

    censo_path = os.path.join(d, "data/censo-2026.json")
    if os.path.exists(censo_path):
        try:
            cen = json.load(open(censo_path, encoding="utf-8"))
            if int(cen.get("total", 0)) != 38_728_356:
                errors.append("censo: total distinto de 38.728.356")
            if int(cen.get("cer", 0)) + int(cen.get("cera", 0)) != int(cen.get("total", 0)):
                errors.append("censo: CER + CERA != total")
        except Exception as e:
            errors.append(f"censo-2026.json inválido: {e}")
    elec_path = os.path.join(d, "electorado.html")
    if os.path.exists(elec_path):
        eh = open(elec_path, encoding="utf-8", errors="ignore").read()
        if "38.728.356" not in eh:
            errors.append("electorado.html sin la cifra total del censo")
        if len(eh) < 5000:
            errors.append(f"electorado.html demasiado pequeño ({len(eh)} bytes)")

    sm = os.path.join(d, "sitemap.xml")
    if os.path.exists(sm):
        try:
            ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
            urls = ET.parse(sm).getroot().findall(".//s:loc", ns)
            if len(urls) < 6:
                errors.append(f"sitemap con {len(urls)} URLs (esperadas >=6)")
        except Exception as e:
            errors.append(f"sitemap inválido: {e}")

    cx = os.path.join(d, "cambios.xml")
    if os.path.exists(cx) and data.get("n_polls", 0) > 0:
        try:
            items = ET.parse(cx).getroot().findall("./channel/item")
            if not items:
                errors.append("cambios.xml sin items")
        except Exception as e:
            errors.append(f"cambios.xml inválido: {e}")

    og = os.path.join(d, "og.png")
    if os.path.exists(og):
        with open(og, "rb") as f:
            magic = f.read(8)
        if magic != b"\x89PNG\r\n\x1a\n":
            errors.append("og.png no es PNG")
        elif os.path.getsize(og) < 10000:
            errors.append(f"og.png demasiado pequeño ({os.path.getsize(og)} bytes)")

    for w in warns:
        print("WARN", w)
    if errors:
        print("VALIDACIÓN FALLIDA:")
        for e in errors:
            print(" -", e)
        return 1
    print(f"validación OK · {d} · n_polls={data.get('n_polls')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
