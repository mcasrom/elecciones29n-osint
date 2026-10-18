#!/usr/bin/env python3
"""Importa participación provincial desde data/participacion_provincial.csv.

Formato: eleccion,provincia,censo,votantes,participacion,fuente_url
La fila EJEMPLO se ignora. Valida provincias, rangos y coherencia con el
dato nacional cuando esté disponible.
"""
from __future__ import annotations

import csv
import json
import os
import sys

INBOX = "data/participacion_provincial.csv"
OUT = "data/participacion_provincial.json"
CENSO = "data/censo_2026.json"


def norm(s: str) -> str:
    return " ".join(s.strip().lower().split())


def main() -> int:
    if not os.path.exists(INBOX):
        print("no existe", INBOX)
        return 1
    provincias = set()
    if os.path.exists(CENSO):
        provincias = {norm(p["nombre"]) for p in json.load(open(CENSO, encoding="utf-8"))["provincias"]}
    rows = []
    errors = []
    with open(INBOX, encoding="utf-8-sig", newline="") as f:
        for i, r in enumerate(csv.DictReader(f), start=2):
            if (r.get("eleccion") or "").strip().upper() == "EJEMPLO":
                continue
            eleccion = (r.get("eleccion") or "").strip()
            provincia = (r.get("provincia") or "").strip()
            fuente = (r.get("fuente_url") or "").strip()
            try:
                censo = int((r.get("censo") or "0").replace(".", "").replace(",", ""))
                votantes = (r.get("votantes") or "").strip()
                votantes = int(votantes.replace(".", "").replace(",", "")) if votantes else None
                part = (r.get("participacion") or "").strip().replace("%", "").replace(",", ".")
                part = float(part) if part else (100.0 * votantes / censo if votantes and censo else None)
                if not eleccion or not provincia or not fuente:
                    raise ValueError("faltan eleccion/provincia/fuente_url")
                if not (0 < censo < 10_000_000):
                    raise ValueError(f"censo fuera de rango: {censo}")
                if votantes is not None and not (0 <= votantes <= censo):
                    raise ValueError("votantes > censo")
                if part is None or not (0 <= part <= 100):
                    raise ValueError("participación inválida")
                if provincias and norm(provincia) not in provincias:
                    raise ValueError(f"provincia no reconocida: {provincia}")
                rows.append({
                    "eleccion": eleccion, "provincia": provincia, "censo": censo,
                    "votantes": votantes, "participacion": round(part, 2), "fuente_url": fuente,
                })
            except Exception as e:
                errors.append(f"fila {i}: {e}")

    if errors:
        print("ERRORES (no se escribe):")
        for e in errors:
            print(" -", e)
        return 1
    if not rows:
        print("sin filas válidas (¿solo EJEMPLO?)")
        return 1

    by = {}
    for r in rows:
        by.setdefault(r["eleccion"], []).append(r)
    for e, rs in by.items():
        # coherencia ponderada por censo
        tot_c = sum(r["censo"] for r in rs)
        if any(r["votantes"] for r in rs):
            tot_v = sum((r["votantes"] or 0) for r in rs)
            p = 100.0 * tot_v / tot_c if tot_c else 0
        else:
            p = sum(r["participacion"] * r["censo"] for r in rs) / tot_c if tot_c else 0
        print(f"{e}: {len(rs)} provincias · participación ponderada {p:.2f}%")

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"elecciones": by}, f, ensure_ascii=False, indent=2)
    print("escrito", OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
