from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import re
import sys
from datetime import datetime, timezone

import openpyxl

SRC = "data/raw/elecciones-congreso.xlsx"
OUT = "data/congreso.json"
UA = "Ministerio del Interior / open data (archivo facilitado)"

MAP_PROV = {
    "A Coruña": "Coruña, A",
    "La Rioja": "Rioja, La",
    "Las Palmas": "Palmas, Las",
    "Alicante/Alacant": "Alicante / Alacant",
    "Castellón/Castelló": "Castellón / Castelló",
    "Valencia/València": "Valencia / València",
    "Balears, Illes": "Balears, Illes",
}


def norm_prov(h: str) -> str:
    name = re.sub(r"^\d+\s*-\s*", "", str(h)).strip()
    return MAP_PROV.get(name, name)


def family(desc: str) -> str:
    s = desc[desc.find("(") + 1:desc.rfind(")")] if "(" in desc else desc
    short = s.rsplit(" - ", 1)[-1].strip()
    u = short.upper()
    if "PARTIDO POPULAR" in u or "PARTIT POPULAR" in u or u == "PP":
        return "PP"
    if ("PSOE" in u or "PSC" in u or "PARTIDO SOCIALISTA" in u
            or "PARTIT DELS SOCIALISTES" in u or "PSDEG" in u or "PSIB" in u
            or "PSN" in u or "PSE-EE" in u):
        return "PSOE"
    if "VOX" in u:
        return "VOX"
    if "SUMAR" in u or "ECP" in u or "COMPROMÍS" in u or "MÉS" in u:
        return "SUMAR"
    if "ESQUERRA REPUBLICANA" in u or u == "ERC":
        return "ERC"
    if "JUNTS" in u:
        return "JUNTS"
    if "EUSKAL HERRIA BILDU" in u:
        return "EH Bildu"
    if "EAJ-PNV" in u or "PARTIDO NACIONALISTA VASCO" in u:
        return "PNV"
    if "BLOQUE NACIONALISTA GALEGO" in u or "B.N.G." in u:
        return "BNG"
    if "COALICIÓN CANARIA" in u:
        return "CC"
    if "UNION DEL PUEBLO NAVARRO" in u or "U.P.N." in u:
        return "UPN"
    return short or "Otros"


def main() -> int:
    if not os.path.exists(SRC):
        print("no existe", SRC)
        return 1
    sha = hashlib.sha256(open(SRC, "rb").read()).hexdigest()
    wb = openpyxl.load_workbook(SRC, read_only=True, data_only=True)
    ws = wb["Congreso"]
    rows = list(ws.iter_rows(values_only=True))
    wb.close()
    hi = next(i for i, r in enumerate(rows) if str(r[0]).strip() == "Fecha")
    header = rows[hi]
    provinces = [norm_prov(h) for h in header[4:-1]]
    if len(provinces) != 52:
        print("VALIDACIÓN FALLIDA: provincias", len(provinces))
        return 1

    elecciones: dict[str, dict] = {}
    for r in rows[hi + 1:]:
        date = str(r[0])[:10]
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
            continue
        desc = str(r[3]).strip()
        vals = list(r[4:-1])
        elecciones.setdefault(date, {})[desc] = vals

    out: dict[str, dict] = {}
    for date, metrics in sorted(elecciones.items()):
        if "Electores" not in metrics or "Votantes" not in metrics:
            continue
        elect = [x for x in metrics["Electores"] if isinstance(x, (int, float))]
        vot = [x for x in metrics["Votantes"] if isinstance(x, (int, float))]
        if len(elect) != 52 or len(vot) != 52:
            print("VALIDACIÓN FALLIDA: filas de provincias", date, len(elect), len(vot))
            return 1
        tot_e, tot_v = sum(elect), sum(vot)
        part = round(100.0 * tot_v / tot_e, 2) if tot_e else 0.0

        provs = []
        for i, name in enumerate(provinces):
            e = int(elect[i] or 0)
            v = int(vot[i] or 0)
            provs.append({
                "nombre": name, "electores": e, "votantes": v,
                "participacion": round(100.0 * v / e, 2) if e else None,
                "votos": {}, "escanos": {},
            })
        idx = {p["nombre"]: p for p in provs}

        nat_votes: dict[str, int] = {}
        nat_seats: dict[str, int] = {}
        for desc, vals in metrics.items():
            if "CERA" in desc:
                continue
            if desc.startswith("Votos ("):
                fam = family(desc)
                nat_votes[fam] = nat_votes.get(fam, 0) + sum(x for x in vals if isinstance(x, (int, float)))
                for i, name in enumerate(provinces):
                    if isinstance(vals[i], (int, float)):
                        idx[name]["votos"][fam] = idx[name]["votos"].get(fam, 0) + int(vals[i])
            elif desc.startswith("Escaños ("):
                fam = family(desc)
                nat_seats[fam] = nat_seats.get(fam, 0) + sum(x for x in vals if isinstance(x, (int, float)))
                for i, name in enumerate(provinces):
                    if isinstance(vals[i], (int, float)):
                        idx[name]["escanos"][fam] = idx[name]["escanos"].get(fam, 0) + int(vals[i])

        nat_seats = {k: v for k, v in nat_seats.items() if v}
        nat_votes = {k: v for k, v in nat_votes.items() if v}
        vtot = sum(nat_votes.values())
        stot = sum(nat_seats.values())
        gall = None
        if vtot and stot == 350:
            gall = round(100 * math.sqrt(0.5 * sum(
                ((nat_votes.get(k, 0) / vtot) - (nat_seats.get(k, 0) / stot)) ** 2
                for k in set(nat_votes) | set(nat_seats)
            )), 2)

        for p in provs:
            p["votos"] = {k: v for k, v in p["votos"].items() if v}
            p["escanos"] = {k: v for k, v in p["escanos"].items() if v}

        out[date] = {
            "nacional": {
                "electores": tot_e, "votantes": tot_v, "participacion": part,
                "votos": dict(sorted(nat_votes.items(), key=lambda kv: -kv[1])),
                "escanos": dict(sorted(nat_seats.items(), key=lambda kv: -kv[1])),
                "gallagher": gall,
                "n_partidos_voto": len(nat_votes),
                "n_partidos_escano": len(nat_seats),
            },
            "provincias": provs,
        }

    # validación 2023
    n23 = out.get("2023-07-23", {}).get("nacional", {})
    checks = {
        "participacion": (n23.get("participacion"), 66.59, 0.05),
        "escanos": (sum(n23.get("escanos", {}).values()), 350, 0),
        "PP": (n23.get("escanos", {}).get("PP"), 137, 0),
        "PSOE": (n23.get("escanos", {}).get("PSOE"), 121, 0),
        "VOX": (n23.get("escanos", {}).get("VOX"), 33, 0),
        "SUMAR": (n23.get("escanos", {}).get("SUMAR"), 31, 0),
    }
    bad = {k: v for k, v in checks.items() if v[0] is None or abs(v[0] - v[1]) > v[2]}
    if bad:
        print("VALIDACIÓN FALLIDA:", bad)
        return 1

    data = {
        "meta": {
            "fuente": UA,
            "fichero": "Elecciones-Congreso.xlsx",
            "sha256": sha,
            "generado": datetime.now(timezone.utc).isoformat(),
            "nota": "Provincial: electores, votantes y votos/escaños por partido (familias). 1977–2023.",
        },
        "elecciones": out,
    }
    os.makedirs("data", exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # JSON de participación provincial (para la web)
    part_out = {
        "meta": data["meta"],
        "elecciones": {
            date: {
                "nacional": {
                    "electores": e["nacional"]["electores"],
                    "votantes": e["nacional"]["votantes"],
                    "participacion": e["nacional"]["participacion"],
                },
                "provincias": [
                    {"nombre": p["nombre"], "electores": p["electores"],
                     "votantes": p["votantes"], "participacion": p["participacion"]}
                    for p in e["provincias"]
                ],
            }
            for date, e in out.items()
        },
    }
    with open("data/participacion_provincial.json", "w", encoding="utf-8") as f:
        json.dump(part_out, f, ensure_ascii=False, indent=2)

    # CSV de participación provincial (todas las elecciones)
    with open("data/participacion_provincial.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["eleccion", "provincia", "electores", "votantes", "participacion"])
        for date, e in sorted(out.items()):
            for p in e["provincias"]:
                w.writerow([date, p["nombre"], p["electores"], p["votantes"], p["participacion"]])

    print(f"congreso OK · {len(out)} elecciones · 2023 part {n23['participacion']}% · "
          f"PP {n23['escanos'].get('PP')} PSOE {n23['escanos'].get('PSOE')} "
          f"VOX {n23['escanos'].get('VOX')} SUMAR {n23['escanos'].get('SUMAR')} · "
          f"Gallagher {n23.get('gallagher')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
