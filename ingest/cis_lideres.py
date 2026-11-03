#!/usr/bin/env python3
"""Extrae la valoración 1-10 de líderes del barómetro CIS 3582.

Una sola casa, una sola ola. No se agrega con otros sondeos ni con intención
de voto. No crea páginas.
"""
import argparse
import json
from pathlib import Path

from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data/raw/cis_3582_multi.xlsx"
OUT = ROOT / "data/cis_lideres_2026.json"
URL = "https://www.cis.es/es/w/avance-de-resultados-del-estudio-3582-barómetro-de-octubre-2026-"
PARTY = {
    "Pedro Sánchez": "PSOE",
    "Alberto Núñez Feijóo": "PP",
    "Yolanda Díaz": "SUMAR",
    "Santiago Abascal": "VOX",
}
HEADER = ["1 Muy mal", "2", "3", "4", "5", "6", "7", "8", "9", "10 Muy bien", "N.S.", "N.C.", "(N)", "Media", "Desviación típica", "N"]


def extract(src):
    wb = load_workbook(src, read_only=True, data_only=True)
    ws = wb["Resultados"]
    rows = list(ws.iter_rows(values_only=True))
    # Localizar la pregunta 20a y su cabecera.
    start = None
    for i, row in enumerate(rows):
        if row and str(row[0] or "").strip() == "Pregunta 20a":
            start = i
            break
    if start is None:
        raise SystemExit("No se encontró Pregunta 20a")
    header_idx = None
    for i in range(start, min(start + 5, len(rows))):
        if len(rows[i]) > 1 and str(rows[i][1] or "").strip() == HEADER[0]:
            header_idx = i
            break
    if header_idx is None:
        raise SystemExit("No se encontró la cabecera de P20a")
    header = [str(x).strip() if x is not None else "" for x in rows[header_idx][1:1 + len(HEADER)]]
    if header[:len(HEADER)] != HEADER:
        raise SystemExit(f"Cabecera inesperada: {header}")
    leaders = []
    for row in rows[header_idx + 1:header_idx + 1 + len(PARTY)]:
        name = str(row[0] or "").strip()
        if name not in PARTY:
            continue
        vals = [float(x) for x in row[1:11]]
        total = sum(vals)
        if total <= 0:
            raise SystemExit(f"Distribución vacía: {name}")
        weighted = sum((i + 1) * v for i, v in enumerate(vals)) / total
        median = None
        acc = 0.0
        for i, v in enumerate(vals, start=1):
            acc += v
            if acc >= total / 2:
                median = i
                break
        leaders.append({
            "name": name,
            "party": PARTY[name],
            "mean": round(weighted, 2),
            "median": median,
            "sd": float(row[15]),
            "n_known": int(row[13]),
            "n_valid": int(row[16]),
            "distribution_pct": {str(i + 1): round(v, 2) for i, v in enumerate(vals)},
            "coverage_pct": round(total, 2),
        })
    if len(leaders) != 4:
        raise SystemExit(f"Se esperaban 4 líderes, hay {len(leaders)}")
    return {
        "meta": {
            "source": "CIS · Estudio 3582, barómetro de octubre de 2026",
            "source_url": URL,
            "question": "¿Qué valoración le merece cada uno/a? Puntúelos/as de 1 a 10.",
            "scale": "1-10",
            "date": "2026-10",
            "house": "CIS",
            "note": "Una sola casa y una sola ola. 1=muy mal, 10=muy bien. No es intención de voto ni aprobación comparable entre casas.",
        },
        "leaders": sorted(leaders, key=lambda x: x["mean"], reverse=True),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", type=Path, default=SRC)
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()
    data = extract(args.src)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    for x in data["leaders"]:
        print(f'{x["name"]}: {x["mean"]} (mediana {x["median"]}, n={x["n_valid"]})')
    print(args.out)


if __name__ == "__main__":
    main()
