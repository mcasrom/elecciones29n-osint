from __future__ import annotations

import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timezone

BOE_URL = "https://www.boe.es/diario_boe/txt.php?id=BOE-A-2026-20742"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"
OUT = "data/escanos_2026.json"
CENSO = "data/censo_2026.json"

NUMS = {
    "uno": 1, "dos": 2, "tres": 3, "cuatro": 4, "cinco": 5, "seis": 6, "siete": 7,
    "ocho": 8, "nueve": 9, "diez": 10, "once": 11, "doce": 12, "trece": 13,
    "catorce": 14, "quince": 15, "dieciséis": 16, "diecisiete": 17, "dieciocho": 18,
    "diecinueve": 19, "veinte": 20, "veintiuno": 21, "veintidós": 22, "veintitrés": 23,
    "veinticuatro": 24, "veinticinco": 25, "veintiséis": 26, "veintisiete": 27,
    "veintiocho": 28, "veintinueve": 29, "treinta": 30, "treinta y uno": 31,
    "treinta y dos": 32, "treinta y tres": 33, "treinta y cuatro": 34,
    "treinta y cinco": 35, "treinta y seis": 36, "treinta y siete": 37,
    "treinta y ocho": 38,
}
WORDS = sorted(NUMS, key=len, reverse=True)

# BOE (RD 806/2026) → nombre del censo (INE)
MAP = {
    "Coruña (A)": "Coruña, A",
    "Palmas (Las)": "Palmas, Las",
    "Balears (Illes)": "Balears, Illes",
    "Rioja (La)": "Rioja, La",
    "Valencia/València": "Valencia / València",
    "Alicante/Alacant": "Alicante / Alacant",
    "Castellón/Castelló": "Castellón / Castelló",
}


def fetch() -> str:
    req = urllib.request.Request(BOE_URL, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=40) as r:
        return r.read().decode("utf-8", "ignore")


def parse(html: str) -> list[dict]:
    i = html.find("ANEXO")
    seg = html[i:i + 9000]
    seg = re.sub(r"<[^>]+>", " ", seg)
    seg = re.sub(r"\s+", " ", seg)
    pattern = re.compile(
        r"([A-ZÁÉÍÓÚÑ][A-Za-zÁÉÍÓÚÜÑáéíóúüñèòàìù/()\- ]*?)\.\s+(" + "|".join(WORDS) + r")\.",
        re.IGNORECASE,
    )
    out = []
    for m in pattern.finditer(seg):
        name = m.group(1).strip()
        if name.upper().startswith("ANEXO"):
            name = re.sub(r"^ANEXO.*?Diputados\s+", "", name, flags=re.IGNORECASE).strip()
        word = m.group(2).lower()
        if name.lower() in ("circunscripción", "diputados"):
            continue
        if name not in MAP and not name[0].isupper():
            continue
        out.append({"boe": name, "escanos": NUMS[word]})
    # dedup preservando orden
    seen = set()
    uniq = []
    for r in out:
        if r["boe"] in seen:
            continue
        seen.add(r["boe"])
        uniq.append(r)
    return uniq


def main() -> int:
    rows = parse(fetch())
    if len(rows) != 52:
        print(f"VALIDACIÓN FALLIDA: {len(rows)} circunscripciones (esperadas 52)")
        print([r["boe"] for r in rows])
        return 1
    total = sum(r["escanos"] for r in rows)
    if total != 350:
        print(f"VALIDACIÓN FALLIDA: {total} escaños (esperados 350)")
        return 1

    censo = json.load(open(CENSO, encoding="utf-8"))
    elect = {p["nombre"]: p["total"] for p in censo["provincias"]}
    provincias = []
    for r in rows:
        nombre = MAP.get(r["boe"], r["boe"])
        if nombre not in elect:
            print("VALIDACIÓN FALLIDA: provincia sin censo:", r["boe"], "->", nombre)
            return 1
        provincias.append({
            "nombre": nombre,
            "escanos": r["escanos"],
            "electores": elect[nombre],
            "electores_por_escanos": round(elect[nombre] / r["escanos"], 0),
        })

    data = {
        "meta": {
            "fuente": "BOE · Real Decreto 806/2026, de 5 de octubre (anexo)",
            "url": BOE_URL,
            "descargado": datetime.now(timezone.utc).isoformat(),
        },
        "total_escanos": total,
        "provincias": sorted(provincias, key=lambda p: -p["escanos"]),
    }
    os.makedirs("data", exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"escaños OK · {total} diputados · {len(provincias)} circunscripciones")
    return 0


if __name__ == "__main__":
    sys.exit(main())
