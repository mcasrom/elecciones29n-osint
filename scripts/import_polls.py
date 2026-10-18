#!/usr/bin/env python3
"""Importa sondeos desde data/entrada_sondeos.csv a data/polls_history.csv.

Formato (una fila por sondeo):
  pollster,date,sample,source_url,values

`values` usa punto y coma: PP=31.8;PSOE=27.1;VOX=18.9
La fila con pollster=EJEMPLO se ignora.

Tras importar, archiva el CSV en data/entrada_sondeos.procesado_<fecha>.csv
y deja una plantilla vacía. Valida partidos, rango y suma (90–110 %).
"""
from __future__ import annotations

import csv
import os
import shutil
from datetime import datetime

INBOX = "data/entrada_sondeos.csv"
HIST = "data/polls_history.csv"
PARTIES = {"PP", "PSOE", "VOX", "SUMAR", "Podemos", "ERC", "Junts", "Bildu", "PNV", "Cs", "SAF", "Otros"}
HEADER = ["pollster", "date", "sample", "source_url", "values"]


def load_done() -> set[tuple[str, str, str]]:
    if not os.path.exists(HIST):
        return set()
    with open(HIST, encoding="utf-8", newline="") as f:
        return {(r["party"], r["date"], r.get("pollster", "")) for r in csv.DictReader(f)}


def parse_values(raw: str) -> dict[str, float]:
    out = {}
    for part in raw.replace(",", ";").split(";"):
        part = part.strip()
        if not part:
            continue
        if "=" not in part:
            raise ValueError(f"formato inválido: {part!r}")
        k, v = part.split("=", 1)
        k = k.strip()
        if k not in PARTIES:
            raise ValueError(f"partido desconocido: {k}")
        val = float(v.strip().replace(",", "."))
        if not (0 <= val <= 100):
            raise ValueError(f"valor fuera de 0–100: {part!r}")
        out[k] = val
    return out


def main() -> int:
    if not os.path.exists(INBOX):
        print("no existe", INBOX)
        return 1
    done = load_done()
    added = 0
    errors = []
    with open(INBOX, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        print("inbox vacío")
        return 0

    os.makedirs("data", exist_ok=True)
    new = not os.path.exists(HIST)
    with open(HIST, "a", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["party", "date", "value", "source_url", "sample", "pollster", "kind"])
        for i, r in enumerate(rows, start=2):
            pollster = (r.get("pollster") or "").strip()
            if not pollster or pollster.upper() == "EJEMPLO":
                continue
            date = (r.get("date") or "").strip()
            url = (r.get("source_url") or "").strip()
            sample = (r.get("sample") or "").strip()
            try:
                datetime.strptime(date, "%Y-%m-%d")
                values = parse_values(r.get("values") or "")
                if not values:
                    raise ValueError("sin valores")
                if sample and not (200 <= int(sample) <= 20000):
                    raise ValueError(f"muestra fuera de 200–20000: {sample}")
            except Exception as e:
                errors.append(f"fila {i}: {e}")
                continue
            total = round(sum(values.values()), 2)
            if not (90 <= total <= 110):
                errors.append(f"fila {i}: suma {total}% fuera de 90–110%")
                continue
            for party, val in values.items():
                key = (party, date, pollster)
                if key in done:
                    continue
                w.writerow([party, date, val, url, sample, pollster, "tracking"])
                done.add(key)
                added += 1

    if errors:
        print("ERRORES (no importados):")
        for e in errors:
            print(" -", e)
    print(f"importados: {added} filas")
    if added:
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        shutil.move(INBOX, f"data/entrada_sondeos.procesado_{stamp}.csv")
        with open(INBOX, "w", encoding="utf-8", newline="") as f:
            csv.writer(f).writerow(HEADER)
        print("inbox archivado; plantilla vacía creada")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
