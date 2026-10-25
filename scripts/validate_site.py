#!/usr/bin/env python3
"""Valida el sitio generado antes de publicarlo.

Si algo falta, sale con código 1 y NO se publica: se conserva la última
versión buena. Evita fallos silenciosos como el gráfico vacío del 18-oct.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from metrics import moving_average, series_span  # noqa: E402

REQUIRED = [
    "index.html", "metodologia.html", "fuentes.html", "about.html", "caveat.html",
    "robots.txt", "sitemap.xml", "llms.txt", "favicon.svg",
    "cambios.xml", "data/latest.json", "data/robustez.json", "css/main.css", "glosario.html", "robustez.html", "hemiciclo.html", "como-leer.html", "novedades.html",
    "electorado.html", "data/censo-2026.json", "data/censo-provincias.csv",
    "participacion.html", "data/participacion.json", "data/participacion.csv",
    "territorio.html", "data/escanos-2026.json", "data/escanos-2026.csv",
    "circunscripciones.html", "data/congreso-oficial.json", "circunscripcion/madrid.html",
    "apoyo.html", "sobre-mi.html", "privacidad.html", "noche-electoral.html", "en.html", "embed/medias.html", "en/method.html", "en/hemicycle.html", "en/robustness.html", "en/limits.html", "en/data.html",
    "manifest.webmanifest", "sw.js", "icons/icon-192.png", "icons/icon-512.png",
    "factores.html", "comportamiento.html", "version.json", "favicon.ico",
    "data/participacion-provincial.json", "data/resultados-2023.csv", "data/status.json", "data/changelog.json", "data/v1/latest.json", "data/v1/robustez.json", "data/v1/status.json",
    "data/m5-results.json", "data/cis-m4-2026.json", "data/cis-m4-2023.csv",
    "data/meteo-electoral.json", "data/meteo-electoral.csv", "data/meteo-electoral-provincias.csv",
]


def validate_blackout(d: str) -> int:
    errors: list[str] = []
    warns: list[str] = []
    required = [
        "index.html", "metodologia.html", "fuentes.html", "about.html", "caveat.html",
        "glosario.html", "electorado.html", "participacion.html", "territorio.html",
        "circunscripciones.html", "noche-electoral.html", "factores.html",
        "comportamiento.html", "como-leer.html", "hemiciclo.html", "apoyo.html", "sobre-mi.html", "privacidad.html",
        "robots.txt", "sitemap.xml", "llms.txt", "favicon.svg",
        "cambios.xml", "css/main.css", "sw.js", "manifest.webmanifest", "version.json",
        "data/blackout.json", "data/censo-2026.json", "data/participacion.json",
        "data/escanos-2026.json", "data/congreso-oficial.json",
    ]
    for f in required:
        path = os.path.join(d, f)
        if not os.path.exists(path):
            errors.append(f"falta {f}")
        elif os.path.getsize(path) == 0:
            errors.append(f"{f} vacío")

    for rel in ("data/latest.json", "data/robustez.json", "data/status.json", "data/changelog.json", "data/v1/latest.json", "data/v1/robustez.json", "data/v1/status.json", "og-robustez.png", "og.png", "og-hemiciclo.png", "en.html", "en/method.html", "en/hemicycle.html", "en/robustness.html", "en/limits.html", "en/data.html", "embed/medias.html"):
        if os.path.exists(os.path.join(d, rel)):
            errors.append(f"blackout: {rel} sigue publicado")

    idx = os.path.join(d, "index.html")
    if os.path.exists(idx):
        h = open(idx, encoding="utf-8", errors="ignore").read()
        if len(h) < 1500:
            errors.append(f"index.html demasiado pequeño ({len(h)} bytes)")
        for needle in ("Blackout electoral", "24 al 28 de noviembre", "69.7"):
            if needle not in h:
                errors.append(f"index.html sin «{needle}»")
        if 'class="chart"' in h:
            errors.append("index.html todavía muestra el gráfico de sondeos")
        if 'rel="canonical"' not in h:
            errors.append("index.html sin canonical")

    for page in ("robustez.html", "novedades.html", "hemiciclo.html"):
        path = os.path.join(d, page)
        if os.path.exists(path):
            h = open(path, encoding="utf-8", errors="ignore").read()
            if "Blackout" not in h:
                errors.append(f"{page} no muestra el aviso de blackout")

    for page in ("metodologia.html", "caveat.html", "glosario.html"):
        path = os.path.join(d, page)
        if os.path.exists(path):
            h = open(path, encoding="utf-8", errors="ignore").read()
            if "se retiran" not in h and "se retira" not in h:
                errors.append(f"{page} no explica que el agregado se retira")

    marker = os.path.join(d, "data/blackout.json")
    if os.path.exists(marker):
        try:
            m = json.load(open(marker, encoding="utf-8"))
            if not m.get("active"):
                errors.append("data/blackout.json no está activo")
            if m.get("start") != "2026-11-24" or m.get("end") != "2026-11-28":
                errors.append("data/blackout.json con fechas distintas de 24–28 nov")
        except Exception as e:
            errors.append(f"data/blackout.json inválido: {e}")

    sm = os.path.join(d, "sitemap.xml")
    if os.path.exists(sm):
        try:
            ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
            urls = ET.parse(sm).getroot().findall(".//s:loc", ns)
            if len(urls) < 10:
                errors.append(f"sitemap con {len(urls)} URLs (esperadas >=10)")
            for el in urls:
                u = (el.text or "").strip()
                if "latest.json" in u or "robustez.json" in u:
                    errors.append(f"sitemap: {u} no debe publicarse en blackout")
                path = u.split("elecciones29n.pruebapublica.com", 1)[-1].lstrip("/") or "index.html"
                fp = os.path.join(d, path)
                if not os.path.exists(fp):
                    errors.append(f"sitemap: falta {path}")
        except Exception as e:
            errors.append(f"sitemap inválido: {e}")

    for name in ("cambios.xml",):
        path = os.path.join(d, name)
        if os.path.exists(path):
            h = open(path, encoding="utf-8", errors="ignore").read()
            if "Blackout" not in h:
                errors.append(f"{name} sin aviso de blackout")
            try:
                ET.fromstring(h)
            except Exception as e:
                errors.append(f"{name} inválido: {e}")

    llms = os.path.join(d, "llms.txt")
    if os.path.exists(llms):
        h = open(llms, encoding="utf-8", errors="ignore").read()
        if "Blackout" not in h or "latest.json" in h.split("## Qué sigue disponible", 1)[-1]:
            errors.append("llms.txt no declara el blackout correctamente")

    for w in warns:
        print(f"WARN  {w}")
    for e in errors:
        print(f"FAIL  {e}")
    if errors:
        return 1
    print(f"validación blackout OK · {d} · agregado y JSON retirados")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("dir", nargs="?", default="web")
    a = ap.parse_args()
    d = a.dir
    if os.path.exists(os.path.join(d, "data/blackout.json")):
        return validate_blackout(d)
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
        if "Robustez del dato" not in html:
            errors.append("index.html sin panel de robustez del dato")
        if "cambios.xml" not in html:
            warns.append("index.html no enlaza cambios.xml")
        if 'href="/hemiciclo.html"' not in html:
            errors.append("index.html sin enlace visible al hemiciclo")

    hemi_path = os.path.join(d, "hemiciclo.html")
    if os.path.exists(hemi_path):
        hh = open(hemi_path, encoding="utf-8", errors="ignore").read()
        if "Hemiciclo simulado" not in hh:
            errors.append("hemiciclo.html sin título")
        if hh.count('class="hemi-seat"') < 350:
            errors.append(f"hemiciclo.html con {hh.count('class="hemi-seat"')} escaños (esperados >=350)")
        if "No es una proyección" not in hh:
            errors.append("hemiciclo.html sin aviso de no proyección")
        if "og-hemiciclo.png" not in hh:
            errors.append("hemiciclo.html sin OG propio")
        if not os.path.exists(os.path.join(d, "og-hemiciclo.png")):
            errors.append("falta og-hemiciclo.png")

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
            hem = data.get("hemicycle") or []
            if not hem:
                errors.append("latest.json sin hemiciclo")
            for e in hem:
                if sum(int(r.get("seats") or 0) for r in e.get("seats", [])) != 350:
                    errors.append(f"hemiciclo {e.get('date')} no suma 350")
                    break
            if int(data.get("n_polls", 0)) < 1:
                errors.append("latest.json sin sondeos (n_polls=0)")
            if data.get("parties") and "class=\"spark\"" not in (open(idx_path, encoding="utf-8", errors="ignore").read() if os.path.exists(idx_path) else ""):
                errors.append("index.html sin minigráficos (spark)")

    pp = os.path.join(d, "data/participacion-provincial.json")
    if os.path.exists(pp):
        try:
            pdata = json.load(open(pp, encoding="utf-8"))
            if len(pdata.get("elecciones", {})) < 15:
                errors.append("participacion-provincial.json con pocas elecciones")
            if "2023-07-23" not in pdata.get("elecciones", {}):
                errors.append("participacion-provincial.json sin 2023")
        except Exception as e:
            errors.append(f"participacion-provincial.json inválido: {e}")
    partp = os.path.join(d, "participacion.html")
    if os.path.exists(partp):
        ph = open(partp, encoding="utf-8", errors="ignore").read()
        if "Participación por provincia" not in ph or "provSel" not in ph:
            errors.append("participacion.html sin selector provincial")
    terr = os.path.join(d, "territorio.html")
    if os.path.exists(terr):
        th = open(terr, encoding="utf-8", errors="ignore").read()
        if "Votos y escaños (2023)" not in th:
            errors.append("territorio.html sin votos/escaños 2023")

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

    nov = os.path.join(d, "novedades.html")
    if os.path.exists(nov):
        nh = open(nov, encoding="utf-8", errors="ignore").read()
        if "Novedades" not in nh:
            errors.append("novedades.html sin título")
        if "0.9.0" not in nh:
            errors.append("novedades.html sin la versión 0.9.0")
        if 'href="/novedades.html"' not in nh:
            warns.append("novedades.html no está enlazada desde la propia página")

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

    facp = os.path.join(d, "factores.html")
    if os.path.exists(facp):
        fh = open(facp, encoding="utf-8", errors="ignore").read()
        if "Resultados (v1)" not in fh:
            errors.append("factores.html sin resultados M5")
        if "Datos meteorológicos usados" not in fh:
            errors.append("factores.html sin anexo meteorológico")

    comp = os.path.join(d, "comportamiento.html")
    if os.path.exists(comp):
        ch = open(comp, encoding="utf-8", errors="ignore").read()
        if "Recuerdo de voto 2023" not in ch or "Por edad" not in ch:
            errors.append("comportamiento.html sin tablas M4")
        if "Módulo en preparación" in ch:
            errors.append("comportamiento.html sigue en diseño")

    pp = os.path.join(d, "privacidad.html")
    if os.path.exists(pp):
        ph = open(pp, encoding="utf-8", errors="ignore").read()
        if "Privacidad" not in ph or "info.elecciones29n@pruebapublica.com" not in ph:
            errors.append("privacidad.html sin contenido esperado")

    for page, needle in (
        ("participacion.html", "Participación en las elecciones generales"),
        ("territorio.html", "Escaños por provincia"),
        ("factores.html", "M5 · Meteorología"),
        ("comportamiento.html", "CIS 3582"),
    ):
        pp = os.path.join(d, page)
        if os.path.exists(pp):
            ph = open(pp, encoding="utf-8", errors="ignore").read()
            if needle not in ph:
                errors.append(f"{page} sin JSON-LD esperado ({needle})")

    co_path = os.path.join(d, "data/congreso-oficial.json")
    if os.path.exists(co_path):
        try:
            co = json.load(open(co_path, encoding="utf-8"))
            for fecha in ("2019-11-10", "2023-07-23"):
                bloque = co.get("elecciones", {}).get(fecha, {})
                provs = bloque.get("provincias", [])
                if len(provs) != 52:
                    errors.append(f"congreso-oficial {fecha}: {len(provs)} provincias")
                total = sum(int(c.get("escanos", 0)) for p in provs for c in p.get("candidaturas", []))
                if total != 350:
                    errors.append(f"congreso-oficial {fecha}: {total} escaños")
                for p in provs:
                    if not p.get("candidaturas"):
                        errors.append(f"congreso-oficial {fecha} {p.get('nombre')}: sin candidaturas")
                    if p.get("candidaturas") and sum(c.get("votos", 0) for c in p["candidaturas"]) + p.get("blancos", 0) != p.get("validos", 0):
                        errors.append(f"congreso-oficial {fecha} {p.get('nombre')}: válidos no cuadran")
            if any(c.get("acronimo") == "SUMAR" for p in co.get("elecciones", {}).get("2019-11-10", {}).get("provincias", []) for c in p.get("candidaturas", [])):
                errors.append("congreso-oficial 2019 contiene SUMAR (etiqueta anacrónica)")
        except Exception as e:
            errors.append(f"congreso-oficial.json inválido: {e}")
    home = os.path.join(d, "index.html")
    if os.path.exists(home):
        hh = open(home, encoding="utf-8", errors="ignore").read()
        if hh.count('href="/circunscripciones.html"') < 2:
            errors.append("index.html sin enlace visible a circunscripciones (nav y portada)")
    ci = os.path.join(d, "circunscripciones.html")
    if os.path.exists(ci):
        ch = open(ci, encoding="utf-8", errors="ignore").read()
        if ch.count("/circunscripcion/") < 52:
            errors.append("circunscripciones.html con menos de 52 enlaces")
        for needle_txt in ("Las 52 circunscripciones", "D'Hondt"):
            if needle_txt not in ch:
                errors.append(f"circunscripciones.html sin «{needle_txt}»")
    if os.path.exists(co_path):
        try:
            vistos = set()
            cdir = os.path.join(d, "circunscripcion")
            for f in (os.listdir(cdir) if os.path.isdir(cdir) else []):
                if f.endswith(".html"):
                    vistos.add(f[:-5])
            if len(vistos) < 52:
                errors.append(f"circunscripcion: {len(vistos)} fichas (esperadas 52)")
            for slug in vistos:
                fh = open(os.path.join(d, "circunscripcion", slug + ".html"), encoding="utf-8", errors="ignore").read()
                if "Calculadora D'Hondt" not in fh:
                    errors.append(f"circunscripcion/{slug}.html sin calculadora")
                if "escaño marginal" not in fh:
                    errors.append(f"circunscripcion/{slug}.html sin escaño marginal")
        except Exception as e:
            errors.append(f"fichas de circunscripción inválidas: {e}")

    sm = os.path.join(d, "sitemap.xml")
    if os.path.exists(sm):
        try:
            ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
            urls = ET.parse(sm).getroot().findall(".//s:loc", ns)
            if len(urls) < 13:
                errors.append(f"sitemap con {len(urls)} URLs (esperadas >=13)")
            # indexabilidad: cada URL del sitemap debe existir, ser self-canonical y no noindex
            for el in urls:
                u = (el.text or "").strip()
                if not u:
                    continue
                path = u.split("elecciones29n.pruebapublica.com", 1)[-1].lstrip("/") or "index.html"
                if path.endswith("/") or path == "":
                    path += "index.html"
                fp = os.path.join(d, path)
                if not os.path.exists(fp):
                    errors.append(f"sitemap: falta {path}")
                    continue
                h = open(fp, encoding="utf-8", errors="ignore").read()
                m = re.search(r'<link rel="canonical" href="([^"]+)"', h)
                if not m:
                    errors.append(f"{path}: sin canonical")
                elif m.group(1) != u:
                    errors.append(f"{path}: canonical {m.group(1)} != {u}")
                if re.search(r'<meta name="robots" content="[^"]*noindex', h, re.I):
                    errors.append(f"{path}: noindex en una URL del sitemap")
        except Exception as e:
            errors.append(f"sitemap inválido: {e}")

    rb_path = os.path.join(d, "robots.txt")
    if os.path.exists(rb_path):
        rb = open(rb_path, encoding="utf-8", errors="ignore").read()
        if re.search(r"(?im)^\s*disallow:\s*/\s*$", rb):
            errors.append("robots.txt bloquea todo (Disallow: /)")
        if "sitemap:" not in rb.lower():
            errors.append("robots.txt sin Sitemap:")

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

    if data and os.path.exists(idx_path):
        idxh = open(idx_path, encoding="utf-8", errors="ignore").read()
        series_long = data.get("series_long", {})
        for party in ("PP", "PSOE"):
            ma = moving_average(series_long.get(party, []))
            if not ma:
                continue
            m = re.search(r'<div class="sparkhead"><span>' + party + r'</span><b>([0-9.]+)%', idxh)
            if not m:
                errors.append(f"index sin sparkline de {party}")
                continue
            expected = round(ma[-1]["value"], 1)
            if abs(float(m.group(1)) - expected) > 0.05:
                errors.append(f"sparkline {party}={m.group(1)} != MA {expected}")
        span = series_span(series_long)
        if span and span not in idxh:
            errors.append(f"index sin periodo real de la serie ({span})")
        if "media móvil de 14 días" not in idxh:
            errors.append("index sin etiqueta de media móvil")

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
