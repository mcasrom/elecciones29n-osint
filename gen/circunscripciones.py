from __future__ import annotations

import json
import os
import re
import unicodedata

from agg.dhondt import marginal, reparto

DATA = "data/congreso-oficial.json"
ELECCIONES = ("2023-07-23", "2019-11-10")
SLUGS = {
    "Araba/Álava": "alava",
    "Alicante / Alacant": "alicante",
    "Castellón / Castelló": "castellon",
    "Valencia / València": "valencia",
    "Coruña, A": "a-coruna",
    "Rioja, La": "la-rioja",
    "Palmas, Las": "las-palmas",
    "Balears, Illes": "baleares",
}


def slugify(nombre: str) -> str:
    if nombre in SLUGS:
        return SLUGS[nombre]
    s = unicodedata.normalize("NFKD", nombre).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s or "circunscripcion"


def load(path: str = DATA) -> dict:
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _por_provincia(bloque: dict) -> dict:
    return {p["nombre"]: p for p in bloque.get("provincias", [])}


def _calc_candidaturas(prov: dict) -> list[dict]:
    return [
        {"etiqueta": c["etiqueta"], "acronimo": c["acronimo"], "votos": c["votos"]}
        for c in prov.get("candidaturas", [])
        if c["votos"] > 0 or c["escanos"] > 0
    ]


def build_pages(oficial: dict, escanos: dict, censo: dict | None = None) -> list[dict]:
    if not oficial:
        return []
    bloques = {fecha: _por_provincia(oficial.get("elecciones", {}).get(fecha, {})) for fecha in ELECCIONES}
    esc = {p["nombre"]: p for p in escanos.get("provincias", [])}
    base = escanos.get("provincias", [])
    pages = []
    for i, e in enumerate(base):
        nombre = e["nombre"]
        if nombre not in bloques.get("2023-07-23", {}) or nombre not in bloques.get("2019-11-10", {}):
            raise RuntimeError(f"circunscripción sin histórico: {nombre}")
        resultados = []
        marginales = {}
        calc_years = {}
        for fecha in ELECCIONES:
            p = bloques[fecha][nombre]
            validos = p["validos"]
            m = marginal(p["candidaturas"], sum(c["escanos"] for c in p["candidaturas"]), validos)
            rep = reparto(p["candidaturas"], sum(c["escanos"] for c in p["candidaturas"]), validos)
            oficiales = {c["etiqueta"]: c["escanos"] for c in p["candidaturas"]}
            if rep != oficiales:
                raise RuntimeError(f"D'Hondt no reproduce {fecha} {nombre}")
            cands = []
            for c in p["candidaturas"]:
                cands.append({
                    **c,
                    "pct": round(100.0 * c["votos"] / validos, 3) if validos else None,
                })
            resultados.append({
                "fecha": fecha,
                "anyo": fecha[:4],
                "participacion": p["participacion"],
                "validos": validos,
                "blancos": p["blancos"],
                "nulos": p["nulos"],
                "cera_total": p["cera_total"],
                "candidaturas": cands,
            })
            marginales[fecha] = m
            calc_years[fecha] = {
                "candidaturas": _calc_candidaturas(p),
                "blancos": p["blancos"],
                "validos": validos,
            }
        page = {
            "nombre": nombre,
            "slug": slugify(nombre),
            "escanos_2026": e["escanos"],
            "electores_2026": e["electores"],
            "electores_por_escanos": e["electores_por_escanos"],
            "participacion_2023": resultados[0]["participacion"],
            "resultados": resultados,
            "marginales": marginales,
            "calc": {"escanos": e["escanos"], "years": calc_years},
            "prev": None,
            "next": None,
        }
        pages.append(page)
    orden = sorted(pages, key=lambda p: p["nombre"])
    for i, p in enumerate(orden):
        p["prev"] = orden[i - 1] if i > 0 else None
        p["next"] = orden[i + 1] if i + 1 < len(orden) else None
    return orden


def index_links(pages: list[dict]) -> list[dict]:
    return sorted(pages, key=lambda p: p["nombre"])
