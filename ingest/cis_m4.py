from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import sys
import unicodedata

import openpyxl

SRC = "data/raw/cis_3582_multi.xlsx"
OUT = "data/cis_m4_2026.json"
URL = "https://www.cis.es/es/w/avance-de-resultados-del-estudio-3582-barómetro-de-octubre-2026-"
TOP = ["PP", "PSOE", "VOX", "SUMAR"]
MIN_N = 30


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", str(s or ""))
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", s.strip().upper())


def num(v) -> float | None:
    if v is None or v == "":
        return None
    try:
        return float(str(v).replace(",", "."))
    except ValueError:
        return None


def find_block(rows):
    start = None
    for i, r in enumerate(rows):
        if "RECUERDO DE PARTICIPACION" in norm(r[0] if r else ""):
            start = i
            break
    if start is None:
        raise ValueError("bloque de recuerdo no encontrado")
    header = None
    for j in range(start, min(start + 6, len(rows))):
        if len(rows[j]) > 1 and norm(rows[j][1]) == "TOTAL":
            header = j
            break
    if header is None:
        raise ValueError("cabecera TOTAL no encontrada")
    cats = []
    for c in range(2, len(rows[header])):
        label = str(rows[header][c] or "").strip()
        if label and norm(label) != "N.C.":
            cats.append((c, label))
    data = {}
    nrow = None
    for j in range(header + 1, len(rows)):
        label = str(rows[j][0] or "").strip()
        if not label:
            continue
        if norm(label) == "(N)":
            nrow = rows[j]
            break
        data[label] = [num(rows[j][c]) for c, _ in cats]
    if nrow is None:
        raise ValueError("fila (N) no encontrada")
    ns = [num(nrow[c]) or 0 for c, _ in cats]
    return cats, data, ns


def party_rows(data):
    mapping = {
        "PP": "PP", "PSOE": "PSOE", "VOX": "VOX", "SUMAR": "SUMAR",
        "ERC": "Otros", "JUNTS": "Otros", "EH BILDU": "Otros",
        "EAJ-PNV": "Otros", "BNG": "Otros", "CCA": "Otros",
        "UPN": "Otros", "PACMA": "Otros", "OTRO PARTIDO": "Otros",
    }
    out = {p: [] for p in TOP + ["Otros"]}
    for label, vals in data.items():
        key = mapping.get(norm(label))
        if not key:
            continue
        for i, v in enumerate(vals):
            if v is None:
                continue
            out[key].append((i, v))
    return out


def norm_group(rows_by_party, ns):
    """Devuelve, por partido, pct normalizado a voto a partidos + n ponderado."""
    ncat = len(ns)
    totals = [0.0] * ncat
    for party in TOP + ["Otros"]:
        for i, v in rows_by_party[party]:
            totals[i] += v
    out = {}
    for party in TOP + ["Otros"]:
        vals = []
        for i in range(ncat):
            pct = sum(v for j, v in rows_by_party[party] if j == i)
            total = totals[i]
            n = round(pct / 100.0 * ns[i], 0)
            p = round(pct / total * 100, 1) if total else None
            vals.append({"pct": p, "n": int(n), "suppressed": (p is None or n < MIN_N)})
        out[party] = vals
    return out, totals


def build_dim(name, cats, data, ns, groups=None):
    rows_by_party = party_rows(data)
    if groups:
        # agrupar categorías de ideología (1-4, 5-6, 7-10) ponderando por N
        idx_groups = []
        for gname, members in groups:
            idxs = [i for i, (_, label) in enumerate(cats) if any(m in norm(label) for m in members)]
            idx_groups.append((gname, idxs))
        grouped = []
        for gname, idxs in idx_groups:
            n_group = sum(ns[i] for i in idxs)
            vals = {}
            for party in TOP + ["Otros"]:
                pct = 0.0
                for i in idxs:
                    pct += sum(v for j, v in rows_by_party[party] if j == i) * ns[i]
                pct = pct / n_group if n_group else 0.0
                vals.setdefault(party, []).append((0, pct))
            # normalizar
            ids = {p: [(i, v) for i, v in vals[p]] for p in vals}
            nrm, totals = norm_group(ids, [n_group])
            grouped.append({
                "nombre": gname,
                "n_total": int(round(n_group)),
                "n_base": int(round(totals[0] / 100.0 * n_group)),
                "partidos": {p: nrm[p][0] for p in TOP + ["Otros"]},
            })
        return {"grupos": grouped}

    nrm, totals = norm_group(rows_by_party, ns)
    groups_out = []
    for i, (_, label) in enumerate(cats):
        groups_out.append({
            "nombre": label,
            "n_total": int(round(ns[i])),
            "n_base": int(round(totals[i] / 100.0 * ns[i])),
            "partidos": {p: nrm[p][i] for p in TOP + ["Otros"]},
        })
    return {"grupos": groups_out}


def main() -> int:
    if not os.path.exists(SRC):
        print("no existe", SRC)
        return 1
    sha = hashlib.sha256(open(SRC, "rb").read()).hexdigest()
    wb = openpyxl.load_workbook(SRC, read_only=True, data_only=True)
    out = {}
    for sheet, key, groups in (
        ("Edad", "edad", None),
        ("Sexo", "sexo", None),
        ("Escala de ideología", "ideologia",
         [("Izquierda (1–4)", ["1 ", "2", "3", "4"]),
          ("Centro (5–6)", ["5", "6"]),
          ("Derecha (7–10)", ["7", "8", "9", "10"])]),
    ):
        rows = list(wb[sheet].iter_rows(values_only=True))
        cats, data, ns = find_block(rows)
        out[key] = build_dim(key, cats, data, ns, groups)
    wb.close()

    data = {
        "meta": {
            "estudio": "3582",
            "titulo": "Barómetro de octubre 2026",
            "publicacion": "2026-10-14",
            "muestra": 5025,
            "fuente": "CIS",
            "url": URL,
            "fichero_sha256": sha,
            "base": "Voto declarado en las elecciones generales de 2023. Porcentajes sobre voto a partidos (excluye blanco, nulo, no votantes y no respuesta). N ponderado.",
            "nota": "Celdas con n<30 suprimidas. El grupo 18–24 incluye a quienes no podían votar en 2023; por eso la base de votantes es menor.",
        },
        **out,
    }
    os.makedirs("data", exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    with open("data/cis_m4_2023.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["dimension", "grupo", "n_total", "n_base", "partido", "pct", "n_celda", "suprimido"])
        for dim in ("edad", "sexo", "ideologia"):
            for g in data[dim]["grupos"]:
                for p in TOP + ["Otros"]:
                    v = g["partidos"][p]
                    w.writerow([dim, g["nombre"], g["n_total"], g["n_base"], p,
                                "" if v["pct"] is None else v["pct"], v["n"], int(v["suppressed"])])
    print("M4 OK · edad", len(data["edad"]["grupos"]), "sexo", len(data["sexo"]["grupos"]),
          "ideologia", len(data["ideologia"]["grupos"]))
    for g in data["edad"]["grupos"][:2]:
        print(" ", g["nombre"], g["n_base"], {p: g["partidos"][p]["pct"] for p in TOP})
    return 0


if __name__ == "__main__":
    sys.exit(main())
