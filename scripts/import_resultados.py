#!/usr/bin/env python3
"""Importa resultados oficiales del 29N desde data/entrada_resultados.csv.

Formato:
  tipo,clave,valor,fuente_url
  participacion,,66.50,https://…
  diputados,PP,137,https://…
  votos,PP,8160837,https://…

Escribe data/resultados_29n.json. No inventa: si falta la fuente, avisa.
La fila EJEMPLO se ignora.
"""
from __future__ import annotations

import csv
import json
import os
from datetime import datetime, timezone

INBOX = "data/entrada_resultados.csv"
OUT = "data/resultados_29n.json"
PARTIES = {"PP", "PSOE", "VOX", "SUMAR", "Podemos", "ERC", "Junts", "Bildu", "PNV", "Cs", "SAF", "Otros"}


def main() -> int:
    if not os.path.exists(INBOX):
        print("no existe", INBOX)
        return 1
    with open(INBOX, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        print("inbox vacío")
        return 0

    part = None
    seats: dict[str, int] = {}
    votes: dict[str, int] = {}
    fuente = ""
    errors = []
    for i, r in enumerate(rows, start=2):
        tipo = (r.get("tipo") or "").strip().lower()
        clave = (r.get("clave") or "").strip()
        val = (r.get("valor") or "").strip()
        url = (r.get("fuente_url") or "").strip()
        if not tipo or tipo == "ejemplo":
            continue
        if url:
            fuente = url
        try:
            if tipo == "participacion":
                v = float(val.replace(",", "."))
                if not (0 <= v <= 100):
                    raise ValueError("participación fuera de 0–100")
                part = v
            elif tipo == "diputados":
                if clave not in PARTIES:
                    raise ValueError(f"partido desconocido: {clave}")
                v = int(val)
                if not (0 <= v <= 350):
                    raise ValueError("escaños fuera de 0–350")
                seats[clave] = v
            elif tipo == "votos":
                if clave not in PARTIES:
                    raise ValueError(f"partido desconocido: {clave}")
                votes[clave] = int(val)
            else:
                raise ValueError(f"tipo desconocido: {tipo}")
        except Exception as e:
            errors.append(f"fila {i}: {e}")

    total = sum(seats.values())
    if seats and total > 350:
        errors.append(f"suma de escaños {total} > 350")
    if errors:
        print("ERRORES (no se publica):")
        for e in errors:
            print(" -", e)
        return 1
    if part is None and not seats and not votes:
        print("sin datos válidos")
        return 1
    if not fuente:
        print("AVISO: sin fuente_url; no se publicará como oficial")
        return 1

    data = {
        "meta": {
            "fuente": "Ministerio del Interior / JEC",
            "url": fuente,
            "actualizado": datetime.now(timezone.utc).isoformat(),
        },
        "participacion": part,
        "diputados": dict(sorted(seats.items(), key=lambda kv: -kv[1])),
        "votos": dict(sorted(votes.items(), key=lambda kv: -kv[1])),
    }
    os.makedirs("data", exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"resultados OK · participación={part} · escaños={total} · partidos={len(seats)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
