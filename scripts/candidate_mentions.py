#!/usr/bin/env python3
"""Menciones de cabezas de lista del 29N en titulares recientes.

Fuente de los nombres: BOE-A-2026-23103 / JEC, candidaturas proclamadas
(3-nov-2026). Fuente de las menciones: titulares y sumarios de prensa
española en intelligence-hub. No mide intención de voto ni actos.
"""
from __future__ import annotations
import argparse, json, re, sqlite3, unicodedata
from datetime import datetime, timedelta, timezone
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

DB = "/home/deploy/intelligence-hub/data/news.db"
OUT_DEFAULT = "/var/www/elecciones29n"
PDF = "https://www.boe.es/boe/dias/2026/11/03/pdfs/BOE-A-2026-23103.pdf"
BOE_HTML = "https://www.boe.es/diario_boe/txt.php?id=BOE-A-2026-23103"
ALIASES = {
    "Pedro Sánchez": ["pedro sanchez", "sanchez"],
    "Feijóo": ["feijoo", "alberto nunez feijoo"],
    "Abascal": ["abascal", "santiago abascal"],
    "Gabriel Rufián": ["gabriel rufian", "rufian"],
    "Míriam Nogueras": ["miriam nogueras", "nogueras"],
    "Oihana Etxebarrieta": ["oihana etxebarrieta", "etxebarrieta"],
    "Idoia Sagastizabal": ["idoia sagastizabal", "sagastizabal"],
    "Néstor Rego": ["nestor rego", "rego"],
    "Leticia San Martín": ["leticia san martin"],
    "Ada Colau": ["ada colau", "colau"],
    "Emilio Delgado": ["emilio delgado"],
    "Irene Montero": ["irene montero"],
    "Alvise Pérez": ["alvise perez", "alvise"],
}
IDS = {
    "Pedro Sánchez": "psoe-pedro-sanchez",
    "Feijóo": "pp-alberto-nunez-feijoo",
    "Abascal": "vox-santiago-abascal",
    "Gabriel Rufián": "erc-gabriel-rufian",
    "Míriam Nogueras": "junts-miriam-nogueras",
    "Oihana Etxebarrieta": "ehbildu-oihana-etxebarrieta",
    "Idoia Sagastizabal": "pnv-idoia-sagastizabal",
    "Néstor Rego": "bng-nestor-rego",
    "Leticia San Martín": "upn-leticia-san-martin",
    "Ada Colau": "comuns-ada-colau",
    "Emilio Delgado": "frente-amplio-emilio-delgado",
    "Irene Montero": "podemos-irene-montero",
    "Alvise Pérez": "salf-alvise-perez",
}
META = {
    "Pedro Sánchez": ("PSOE", "Madrid"),
    "Feijóo": ("PP", "Madrid"),
    "Abascal": ("VOX", "Madrid"),
    "Gabriel Rufián": ("ERC", "Barcelona"),
    "Míriam Nogueras": ("Junts", "Barcelona"),
    "Oihana Etxebarrieta": ("EH Bildu", "Gipuzkoa"),
    "Idoia Sagastizabal": ("PNV", "Bizkaia"),
    "Néstor Rego": ("BNG", "A Coruña"),
    "Leticia San Martín": ("UPN-PP", "Navarra"),
    "Ada Colau": ("Frente Amplio / Comuns", "Barcelona"),
    "Emilio Delgado": ("Frente Amplio", "Madrid"),
    "Irene Montero": ("Podemos", "Madrid"),
    "Alvise Pérez": ("SALF", "Madrid"),
}
WINDOWS = (1, 7)
ELECT = ("29n","29-n","elecciones","eleccion","electoral","campaña","campana","candidat","mitin","voto","votos","sondeo","encuesta","debate","escaño","escano","investidura","urnas","mesa electoral","colegio electoral","papeleta")

def norm(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", (s or "").lower()) if unicodedata.category(c) != "Mn")

def electoral_context(text: str) -> bool:
    t = norm(text)
    return any(x in t for x in ELECT)

def hit(text: str, aliases: list[str]) -> bool:
    t = norm(text)
    return any(re.search(r"(?<![a-z0-9])" + re.escape(a) + r"(?![a-z0-9])", t) for a in aliases)

def collect() -> dict:
    now = datetime.now(timezone.utc)
    con = sqlite3.connect("file:%s?mode=ro" % DB, uri=True)
    con.row_factory = sqlite3.Row
    out = {"generated_at": now.isoformat(timespec="seconds"), "source": "intelligence-hub/news.db", "source_label": "Titulares y sumarios de prensa española", "candidates_source": "BOE-A-2026-23103 · JEC · candidaturas proclamadas 3-nov-2026", "candidates_pdf": PDF, "candidates_html": BOE_HTML, "note": "Cabezas de lista proclamados en el BOE; no son necesariamente los líderes del partido. No se incluye Sumar como marca propia: aparece integrada en Frente Amplio/Comuns. Yolanda Díaz no figura como candidata.", "windows": {}}
    for days in WINDOWS:
        cut = (now - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%S")
        rows = con.execute("SELECT title, summary, published FROM articles WHERE lang='es' AND country='espana' AND published>=?", (cut,)).fetchall()
        counts = {k: 0 for k in ALIASES}; electoral = {k: 0 for k in ALIASES}; day_sets = {k: set() for k in ALIASES}; electoral_days = {k: set() for k in ALIASES}
        n_electoral = 0
        for r in rows:
            text = (r["title"] or "") + " " + (r["summary"] or "")
            day = (r["published"] or "")[:10]
            is_electoral = electoral_context(text)
            if is_electoral: n_electoral += 1
            for k, aliases in ALIASES.items():
                if hit(text, aliases):
                    counts[k] += 1; day_sets[k].add(day)
                    if is_electoral: electoral[k] += 1; electoral_days[k].add(day)
        n = len(rows)
        src_rows = con.execute("SELECT source, COUNT(*) AS n FROM articles WHERE lang='es' AND country='espana' AND published>=? GROUP BY source ORDER BY n DESC", (cut,)).fetchall()
        sources = [{"name": r["source"], "articles": r["n"]} for r in src_rows]
        leaders = []
        for k in ALIASES:
            party, province = META[k]
            leaders.append({"id": IDS[k], "name": k, "party": party, "province": province, "articles": counts[k], "share_pct": round(100 * counts[k] / n, 1) if n else 0, "days": len(day_sets[k]), "electoral": electoral[k], "electoral_share_pct": round(100 * electoral[k] / n_electoral, 1) if n_electoral else 0, "electoral_days": len(electoral_days[k])})
        leaders.sort(key=lambda x: (-x["electoral"], -x["articles"], x["name"]))
        out["windows"][str(days)] = {"n_articles": n, "n_electoral": n_electoral, "sources": sources, "leaders": leaders}
    con.close()
    top_ids = [x["id"] for x in out["windows"]["7"]["leaders"][:10]]
    out["top_ids"] = top_ids
    out["top_note"] = "Se muestran los 10 con más menciones a 7 días; el JSON conserva los 13."
    out["top_note"] = "Top 10 por menciones en contexto electoral a 7 días; el JSON conserva los 13 y ambos totales."
    return out

def font(size: int, bold: bool = False):
    return ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-%s.ttf" % ("Bold" if bold else "Regular"), size)

def chart(window: dict, days: int, path: Path, top_ids: list[str]) -> None:
    W, H = 1000, max(640, 130 + 52 * len(window["leaders"]) + 40)
    bg, ink, muted, orange = "#ffffff", "#172033", "#64748b", "#ff5a1f"
    im = Image.new("RGB", (W, H), bg); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 10], fill=orange)
    d.text((54, 38), "Cabezas de lista · contexto electoral · top 10 · %s" % ("24 h" if days == 1 else "7 días"), font=font(28, True), fill=ink)
    d.text((54, 82), "Solo artículos con contexto electoral · n=%d de %d" % (window["n_electoral"], window["n_articles"]), font=font(17), fill=muted)
    by = {x["id"]: x for x in window["leaders"]}
    leaders = [by[i] for i in top_ids if i in by]
    maxv = max((x["electoral"] for x in leaders), default=1) or 1
    y = 130
    for x in leaders:
        name, val = x["name"], x["electoral"]
        d.text((54, y), name, font=font(19, True), fill=ink)
        d.text((54, y + 22), "%s · %s" % (x["party"], x["province"]), font=font(13), fill=muted)
        bw = int(470 * val / maxv) if maxv else 0
        d.rounded_rectangle([330, y + 2, 850, y + 30], radius=6, fill="#f1f5f9")
        if bw: d.rounded_rectangle([330, y + 2, 330 + bw, y + 30], radius=6, fill=orange)
        d.text((985, y + 4), "%d · %.1f%%" % (val, x["electoral_share_pct"]), font=font(16, True), fill=ink, anchor="ra")
        y += 52
    d.text((54, H - 28), "Fuente: titulares de prensa · cabezas de lista BOE/JEC · no es intención de voto", font=font(13), fill=muted)
    im.save(path, optimize=True)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default=OUT_DEFAULT); a = ap.parse_args()
    out = Path(a.out); (out / "data").mkdir(parents=True, exist_ok=True); (out / "img").mkdir(parents=True, exist_ok=True)
    data = collect()
    (out / "data" / "candidatos.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    for days in WINDOWS: chart(data["windows"][str(days)], days, out / "img" / ("candidatos-%dd.png" % days), data["top_ids"])
    print("candidatos ok", out, "1d", data["windows"]["1"]["n_articles"], "7d", data["windows"]["7"]["n_articles"])

if __name__ == "__main__": main()
