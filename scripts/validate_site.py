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
    "participacion.html", "data/participacion.json", "data/participacion.csv",
    "territorio.html", "data/escanos-2026.json", "data/escanos-2026.csv",
    "apoyo.html", "sobre-mi.html", "noche-electoral.html",
    "manifest.webmanifest", "sw.js", "icons/icon-192.png", "icons/icon-512.png",
    "factores.html", "version.json",
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
        if "Salud de la muestra" not in html:
            errors.append("index.html sin panel de salud de la muestra")
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
            if not data.get("health"):
                errors.append("latest.json sin health")
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

    part_path = os.path.join(d, "data/participacion.json")
    if os.path.exists(part_path):
        try:
            par = json.load(open(part_path, encoding="utf-8"))
            els = par.get("elecciones", [])
            if len(els) < 15:
                errors.append(f"participación: {len(els)} elecciones (esperadas >=15)")
            if not any(abs(float(r.get("participacion", 0)) - 66.59) < 0.01 for r in els):
                errors.append("participación: falta el dato de 2023 (66,59)")
        except Exception as e:
            errors.append(f"participacion.json inválido: {e}")
    partp = os.path.join(d, "participacion.html")
    if os.path.exists(partp):
        ph = open(partp, encoding="utf-8", errors="ignore").read()
        if "66,59" not in ph:
            errors.append("participacion.html sin la cifra de 2023")
        if len(ph) < 4000:
            errors.append(f"participacion.html demasiado pequeño ({len(ph)} bytes)")

    esc_path = os.path.join(d, "data/escanos-2026.json")
    if os.path.exists(esc_path):
        try:
            esc = json.load(open(esc_path, encoding="utf-8"))
            provs = esc.get("provincias", [])
            if len(provs) != 52:
                errors.append(f"escaños: {len(provs)} provincias (esperadas 52)")
            if sum(int(p.get("escanos", 0)) for p in provs) != 350:
                errors.append("escaños: la suma no es 350")
        except Exception as e:
            errors.append(f"escanos-2026.json inválido: {e}")
    terr = os.path.join(d, "territorio.html")
    if os.path.exists(terr):
        th = open(terr, encoding="utf-8", errors="ignore").read()
        if "Teruel" not in th or "350" not in th:
            errors.append("territorio.html sin datos de escaños")

    for name, needle in (("apoyo.html", "ko-fi.com/m_castillo"), ("sobre-mi.html", "Miguel Castillo")):
        pp = os.path.join(d, name)
        if os.path.exists(pp):
            ph = open(pp, encoding="utf-8", errors="ignore").read()
            if needle not in ph:
                errors.append(f"{name} sin contenido esperado")
            if len(ph) < 3000:
                errors.append(f"{name} demasiado pequeño ({len(ph)} bytes)")

    ne = os.path.join(d, "noche-electoral.html")
    res_path = os.path.join(d, "data/resultados-29n.json")
    has_results = os.path.exists(res_path)
    if has_results:
        try:
            json.load(open(res_path, encoding="utf-8"))
        except Exception as e:
            errors.append(f"resultados-29n.json inválido: {e}")
    if os.path.exists(ne):
        nh = open(ne, encoding="utf-8", errors="ignore").read()
        if has_results and "Participación" not in nh:
            errors.append("noche-electoral.html sin bloque de resultados")
        if not has_results and "Sin datos electorales todavía" not in nh:
            errors.append("noche-electoral.html sin estado previo")

    man = os.path.join(d, "manifest.webmanifest")
    if os.path.exists(man):
        try:
            m = json.load(open(man, encoding="utf-8"))
            if not m.get("name") or not m.get("icons"):
                errors.append("manifest sin name/icons")
        except Exception as e:
            errors.append(f"manifest inválido: {e}")
    swp = os.path.join(d, "sw.js")
    if os.path.exists(swp) and "CACHE" not in open(swp, encoding="utf-8", errors="ignore").read():
        errors.append("sw.js sin CACHE")

    fac = os.path.join(d, "factores.html")
    if os.path.exists(fac):
        fh = open(fac, encoding="utf-8", errors="ignore").read()
        if "Factores y participación" not in fh:
            errors.append("factores.html sin título esperado")

    vp = os.path.join(d, "version.json")
    if os.path.exists(vp) and os.path.exists(idx_path):
        try:
            ver = json.load(open(vp, encoding="utf-8")).get("version", "")
            idxh = open(idx_path, encoding="utf-8", errors="ignore").read()
            if ver and f"v{ver}" not in idxh:
                errors.append(f"index.html sin versión v{ver}")
        except Exception as e:
            errors.append(f"version.json inválido: {e}")

    sm = os.path.join(d, "sitemap.xml")
    if os.path.exists(sm):
        try:
            ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
            urls = ET.parse(sm).getroot().findall(".//s:loc", ns)
            if len(urls) < 12:
                errors.append(f"sitemap con {len(urls)} URLs (esperadas >=12)")
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
