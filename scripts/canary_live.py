#!/usr/bin/env python3
"""Canario del sitio publicado: comprueba que el gráfico y los metadatos
esenciales están en vivo. Si falla, avisa (el build local puede estar bien
pero el despliegue no)."""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
BASE = "https://elecciones29n.pruebapublica.com"


def get(url: str, tries: int = 3) -> tuple[int, str]:
    last = (0, "")
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Cache-Control": "no-cache"})
            with urllib.request.urlopen(req, timeout=25) as r:
                return r.status, r.read().decode("utf-8", "ignore")
        except Exception as e:
            last = (0, str(e))
            time.sleep(3)
    return last



def status(url: str) -> int:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Cache-Control": "no-cache"})
        with urllib.request.urlopen(req, timeout=25) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:
        return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=BASE)
    a = ap.parse_args()
    base = a.base.rstrip("/")
    errors = []

    code, marker = get(base + "/data/blackout.json?canary=1")
    if code == 200:
        if '"active": true' not in marker:
            errors.append("data/blackout.json sin active=true")
        code, html = get(base + "/?canary=1")
        if code != 200:
            errors.append(f"blackout home HTTP {code}")
        else:
            if "Blackout electoral" not in html:
                errors.append("blackout home sin aviso")
            if 'class="chart"' in html:
                errors.append("blackout home sigue mostrando el gráfico")
        for path in ("/data/latest.json", "/data/robustez.json", "/og-robustez.png"):
            c = status(base + path + "?canary=1")
            if c not in (404, 410):
                errors.append(f"blackout: {path} sigue publicado (HTTP {c})")
        for path in ("/robustez.html", "/novedades.html"):
            c, h = get(base + path + "?canary=1")
            if c != 200:
                errors.append(f"blackout {path} HTTP {c}")
            elif "Blackout" not in h:
                errors.append(f"blackout {path} sin aviso")
        c, h = get(base + "/metodologia.html?canary=1")
        if c != 200 or "se retiran" not in h:
            errors.append("blackout metodologia.html sin método actualizado")
        c, h = get(base + "/glosario.html?canary=1")
        if c != 200 or "se retiran" not in h:
            errors.append("blackout glosario.html sin blackout actualizado")
        c, h = get(base + "/cambios.xml?canary=1")
        if c != 200 or "Blackout" not in h:
            errors.append("blackout cambios.xml sin aviso")
        c, h = get(base + "/sitemap.xml?canary=1")
        if c != 200 or "latest.json" in h or "robustez.json" in h:
            errors.append("blackout sitemap.xml con datos retirados")
        for path, needle in (
            ("/electorado.html", "38.728.356"),
            ("/participacion.html", "66,59"),
            ("/territorio.html", "Teruel"),
            ("/circunscripciones.html", "Las 52 circunscripciones"),
            ("/noche-electoral.html", "Noche electoral"),
            ("/comportamiento.html", "Recuerdo de voto 2023"),
            ("/factores.html", "Factores y participación"),
        ):
            c, h = get(base + path + "?canary=1")
            if c != 200:
                errors.append(f"blackout {path} HTTP {c}")
            elif needle not in h:
                errors.append(f"blackout {path} sin «{needle}»")
        for p in ("/version.json", "/favicon.ico", "/manifest.webmanifest", "/sw.js", "/og.png"):
            c = status(base + p + "?canary=1")
            if c != 200:
                errors.append(f"blackout {p} HTTP {c}")
        if errors:
            print("CANARIO BLACKOUT FALLIDO:")
            for e in errors:
                print(" -", e)
            return 1
        print("canario OK · blackout activo · agregado y JSON retirados")
        return 0

    code, html = get(base + "/?canary=1")
    if code != 200:
        errors.append(f"home HTTP {code} ({html[:120]})")
    else:
        if 'class="chart"' not in html:
            errors.append("home sin gráfico")
        elif html.count("<circle") < 1:
            errors.append("gráfico sin puntos")
        if "media móvil de 14 días" not in html:
            errors.append("home sin etiqueta de media móvil")
        if "Robustez del dato" not in html:
            errors.append("home sin panel de robustez del dato")
        if 'id="tab-evolucion"' not in html:
            errors.append("sin pestaña Evolución")
        if 'property="og:image"' not in html:
            errors.append("sin og:image")

    code, raw = get(base + "/data/latest.json?canary=1")
    if code != 200:
        errors.append(f"latest.json HTTP {code}")
    else:
        try:
            d = json.loads(raw)
            if not d.get("parties"):
                errors.append("latest.json sin partidos")
            if not d.get("series_long"):
                errors.append("latest.json sin series_long")
        except Exception as e:
            errors.append(f"latest.json inválido: {e}")

    for _path, _needle in (("/glosario.html", "Glosario"),
                           ("/robustez.html", "Robustez del dato"),
                           ("/como-leer.html", "Cómo leer la media"),
                           ("/novedades.html", "Novedades")):
        _c, _h = get(base + _path + "?canary=1")
        if _c != 200:
            errors.append(f"{_path} HTTP {_c}")
        elif _needle not in _h:
            errors.append(f"{_path} sin «{_needle}»")

    code, eh = get(base + "/electorado.html?canary=1")
    if code != 200:
        errors.append(f"electorado.html HTTP {code}")
    elif "38.728.356" not in eh:
        errors.append("electorado.html sin la cifra del censo")

    code, ph = get(base + "/participacion.html?canary=1")
    if code != 200:
        errors.append(f"participacion.html HTTP {code}")
    elif "66,59" not in ph:
        errors.append("participacion.html sin la cifra de 2023")

    code, cih = get(base + "/circunscripciones.html?canary=1")
    if code != 200:
        errors.append(f"circunscripciones.html HTTP {code}")
    elif "Las 52 circunscripciones" not in cih or "D'Hondt" not in cih:
        errors.append("circunscripciones.html sin índice ni calculadora")

    code, cmh = get(base + "/circunscripcion/madrid.html?canary=1")
    if code != 200:
        errors.append(f"circunscripcion/madrid.html HTTP {code}")
    elif "Calculadora D'Hondt" not in cmh or "escaño marginal" not in cmh:
        errors.append("circunscripcion/madrid.html sin calculadora o marginal")

    code, th = get(base + "/territorio.html?canary=1")
    if code != 200:
        errors.append(f"territorio.html HTTP {code}")
    elif "Teruel" not in th or "350" not in th:
        errors.append("territorio.html sin datos de escaños")

    for path, needle in (("/apoyo.html", "ko-fi.com/m_castillo"), ("/sobre-mi.html", "Miguel Castillo")):
        code, ph = get(base + path + "?canary=1")
        if code != 200:
            errors.append(f"{path} HTTP {code}")
        elif needle not in ph:
            errors.append(f"{path} sin contenido esperado")

    code, nh = get(base + "/noche-electoral.html?canary=1")
    if code != 200:
        errors.append(f"noche-electoral.html HTTP {code}")
    elif ("Sin datos electorales todavía" not in nh) and ("Participación" not in nh):
        errors.append("noche-electoral.html sin estado ni resultados")

    code, vj = get(base + "/version.json?canary=1")
    if code != 200:
        errors.append(f"version.json HTTP {code}")
    elif '"version"' not in vj:
        errors.append("version.json sin version")

    for p in ("/favicon.ico", "/manifest.webmanifest", "/sw.js"):
        code, _ = get(base + p + "?canary=1")
        if code != 200:
            errors.append(f"{p} HTTP {code}")

    code, ch = get(base + "/comportamiento.html?canary=1")
    if code != 200:
        errors.append(f"comportamiento.html HTTP {code}")
    elif "Recuerdo de voto 2023" not in ch or "Por edad" not in ch:
        errors.append("comportamiento.html sin tablas M4")

    code, fh = get(base + "/factores.html?canary=1")
    if code != 200:
        errors.append(f"factores.html HTTP {code}")
    elif "Factores y participación" not in fh:
        errors.append("factores.html sin título esperado")
    elif "Resultados (v1)" not in fh:
        errors.append("factores.html sin resultados M5")
    elif "Datos meteorológicos usados" not in fh:
        errors.append("factores.html sin anexo meteorológico")

    code, _ = get(base + "/og.png?canary=1")
    if code != 200:
        errors.append(f"og.png HTTP {code}")

    if errors:
        print("CANARIO FALLIDO:")
        for e in errors:
            print(" -", e)
        return 1
    print("canario OK · gráfico y metadatos en vivo")
    return 0


if __name__ == "__main__":
    sys.exit(main())
