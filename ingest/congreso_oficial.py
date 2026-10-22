from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone

import openpyxl

from ingest.congreso import norm_prov

SRC = "data/raw/elecciones-congreso.xlsx"
OUT = "data/congreso-oficial.json"
ELECCIONES = ("2019-11-10", "2023-07-23")
FUENTE = "Ministerio del Interior / open data (archivo facilitado)"


def acronimo(label: str) -> str:
    return label.rsplit(" - ", 1)[-1].strip() if " - " in label else label.strip()


def etiqueta_candidatura(desc: str) -> str:
    if desc.startswith("Votos (") and desc.endswith(")"):
        return desc[7:-1]
    if desc.startswith("Escaños (") and desc.endswith(")"):
        return desc[9:-1]
    if desc.startswith("Votos CERA (") and desc.endswith(")"):
        return desc[12:-1]
    return ""


def val(v) -> int:
    return int(v) if isinstance(v, (int, float)) else 0


def main() -> int:
    if not os.path.exists(SRC):
        print("no existe", SRC, file=sys.stderr)
        return 1

    sha = hashlib.sha256(open(SRC, "rb").read()).hexdigest()
    wb = openpyxl.load_workbook(SRC, read_only=True, data_only=True)
    ws = wb["Congreso"]
    rows = list(ws.iter_rows(values_only=True))
    wb.close()

    hi = next(i for i, r in enumerate(rows) if str(r[0]).strip() == "Fecha")
    header = rows[hi]
    provincias = [norm_prov(h) for h in header[4:-1]]
    if len(provincias) != 52:
        print(f"VALIDACIÓN FALLIDA: {len(provincias)} provincias", file=sys.stderr)
        return 1

    crudo: dict[str, list[tuple[str, list]]] = {}
    for r in rows[hi + 1:]:
        fecha = str(r[0])[:10]
        if fecha not in ELECCIONES:
            continue
        desc = str(r[3]).strip()
        crudo.setdefault(fecha, []).append((desc, list(r[4:-1])))

    out: dict[str, dict] = {}
    for fecha in ELECCIONES:
        filas = crudo.get(fecha, [])
        if not filas:
            print(f"VALIDACIÓN FALLIDA: falta {fecha}", file=sys.stderr)
            return 1
        metricas = {desc: vals for desc, vals in filas}

        requeridas = ("Electores", "Votantes", "Votos válidos", "Votos nulos", "Votos en blanco")
        faltan = [k for k in requeridas if k not in metricas]
        if faltan:
            print(f"VALIDACIÓN FALLIDA: {fecha} sin {faltan}", file=sys.stderr)
            return 1

        votos: dict[str, list] = {}
        escanos: dict[str, list] = {}
        cera: dict[str, list] = {}

        def acumular(dst: dict[str, list], label: str, vals) -> None:
            # El XLSX repite algunas etiquetas en filas con provincias disjuntas
            # (p.ej. FRENTE OBRERO - FO). Se suman por provincia, nunca se pisa.
            if label not in dst:
                dst[label] = [0] * 52
            actual = dst[label]
            for j, v in enumerate(vals):
                if j < 52:
                    actual[j] += val(v)

        for desc, vals in filas:
            if desc.startswith("Votos CERA ("):
                label = etiqueta_candidatura(desc)
                if label:
                    acumular(cera, label, vals)
            elif desc.startswith("Votos ("):
                label = etiqueta_candidatura(desc)
                if label:
                    acumular(votos, label, vals)
            elif desc.startswith("Escaños ("):
                label = etiqueta_candidatura(desc)
                if label:
                    acumular(escanos, label, vals)

        provs = []
        for i, nombre in enumerate(provincias):
            electores = val(metricas["Electores"][i])
            votantes = val(metricas["Votantes"][i])
            validos = val(metricas["Votos válidos"][i])
            nulos = val(metricas["Votos nulos"][i])
            blancos = val(metricas["Votos en blanco"][i])
            candidaturas = []
            for label in sorted(set(votos) | set(escanos)):
                v = val(votos.get(label, [0] * 52)[i])
                e = val(escanos.get(label, [0] * 52)[i])
                c = val(cera.get(label, [0] * 52)[i])
                if v == 0 and e == 0:
                    continue
                candidaturas.append({
                    "etiqueta": label,
                    "acronimo": acronimo(label),
                    "votos": v,
                    "escanos": e,
                    "cera": c,
                })
            candidaturas.sort(key=lambda x: (-x["votos"], -x["escanos"], x["etiqueta"]))
            suma = sum(c["votos"] for c in candidaturas)
            if suma + blancos != validos:
                print(
                    f"VALIDACIÓN FALLIDA: {fecha} {nombre}: "
                    f"candidaturas {suma} + blancos {blancos} != válidos {validos}",
                    file=sys.stderr,
                )
                return 1
            provs.append({
                "nombre": nombre,
                "electores": electores,
                "votantes": votantes,
                "validos": validos,
                "nulos": nulos,
                "blancos": blancos,
                "participacion": round(100.0 * votantes / electores, 2) if electores else None,
                "cera_electores": val(metricas.get("Electores CERA", [0] * 52)[i]),
                "cera_votantes": val(metricas.get("Votantes CERA", [0] * 52)[i]),
                "cera_total": sum(c["cera"] for c in candidaturas),
                "candidaturas": candidaturas,
            })
        out[fecha] = {"fecha": fecha, "provincias": provs}

    for fecha, bloque in out.items():
        total = sum(c["escanos"] for p in bloque["provincias"] for c in p["candidaturas"])
        if total != 350:
            print(f"VALIDACIÓN FALLIDA: {fecha} suma {total} escaños", file=sys.stderr)
            return 1
        if len(bloque["provincias"]) != 52:
            print(f"VALIDACIÓN FALLIDA: {fecha} {len(bloque['provincias'])} provincias", file=sys.stderr)
            return 1

    data = {
        "meta": {
            "fuente": FUENTE,
            "fichero": os.path.basename(SRC),
            "sha256": sha,
            "generado": datetime.now(timezone.utc).isoformat(),
            "elecciones": list(ELECCIONES),
            "nota": (
                "Resultados oficiales por provincia con etiqueta original. "
                "Los votos incluyen CERA; el campo cera es un subconjunto, no se suma aparte."
            ),
        },
        "elecciones": out,
    }
    os.makedirs("data", exist_ok=True)
    tmp = OUT + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, OUT)
    print(f"congreso oficial OK · {len(out)} elecciones · {len(out['2023-07-23']['provincias'])} provincias · 350 escaños")
    return 0


if __name__ == "__main__":
    sys.exit(main())
