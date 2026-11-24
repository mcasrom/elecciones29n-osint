#!/usr/bin/env python3
"""Sonda de fuentes oficiales de resultados. No publica ni modifica datos."""
import urllib.request
SOURCES = [
    "https://descargas.interior.gob.es/datasets/resultados_electorales/Elecciones-Congreso.xlsx",
    "https://resultados.elecciones.gob.es/",
    "https://infoelectoral.interior.gob.es/",
    "https://www.interior.gob.es/opencms/es/servicios-al-ciudadano/resultados-electorales/",
    "https://www.juntaelectoralcentral.es/",
]
for url in SOURCES:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as r:
            print(f"{r.status:3d} {r.headers.get('content-type','?')[:45]:45s} {url}")
    except Exception as e:
        print(f"ERR {type(e).__name__}: {str(e)[:70]} {url}")
