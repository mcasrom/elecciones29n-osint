from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timezone

import openpyxl

BASE = "https://www.ine.es/oficina_censo/elecgen2026"
FILES = {
    "provincias": "Elecgral_2026_cc_tab3.xlsx",
    "ccaa": "Elecgral_2026_cc_tab2.xlsx",
    "edad_sexo": "Elecgral_2026_cc_tab9.xlsx",
    "nuevos": "Elecgral_2026_cc_tab12.xlsx",
    "cera_paises": "Elecgral_2026_cc_tab6.xlsx",
}
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"

RAW_DIR = "data/censo_raw"
OUT = "data/censo_2026.json"

TOTAL = 38_728_356
CER = 35_958_711
CERA = 2_769_645
NUEVOS = 1_615_127


def download(name: str, filename: str) -> tuple[str, str, str]:
    os.makedirs(RAW_DIR, exist_ok=True)
    path = os.path.join(RAW_DIR, filename)
    url = f"{BASE}/{filename}"
    if not os.path.exists(path):
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=60) as r:
            data = r.read()
        with open(path, "wb") as f:
            f.write(data)
    with open(path, "rb") as f:
        data = f.read()
    return path, url, hashlib.sha256(data).hexdigest()


def rows(path: str) -> list[tuple]:
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    ws = wb.active
    out = list(ws.iter_rows(values_only=True))
    wb.close()
    return out


def num(v) -> int:
    if v is None or v == "":
        return 0
    if isinstance(v, (int, float)):
        return int(v)
    s = str(v).strip().replace(".", "").replace(",", "")
    return int(s) if s.isdigit() else 0


def is_code(v) -> bool:
    return bool(re.fullmatch(r"\d{2,3}", str(v or "").strip()))


def parse_provincias(path: str) -> list[dict]:
    out = []
    for r in rows(path):
        a, b = (r + ("",))[:2]
        if str(a or "").strip().lower().startswith("total general"):
            continue
        if not is_code(a):
            continue
        out.append({
            "codigo": str(a).strip(),
            "nombre": str(b).strip(),
            "cer": num(r[2]),
            "cera": num(r[3]),
            "total": num(r[4]),
        })
    return out


def parse_ccaa(path: str) -> list[dict]:
    out = []
    started = False
    for r in rows(path):
        a, b = (r + ("",))[:2]
        if str(a or "").strip().lower().startswith("comunidad aut"):
            started = True
            continue
        if not started:
            continue
        if str(a or "").strip().lower().startswith("total general"):
            continue
        # CCAA: nombre en A, B vacío. Provincia: código en A, nombre en B.
        if is_code(a) or not str(a or "").strip() or str(b or "").strip():
            continue
        nombre = str(a).strip()
        out.append({
            "nombre": nombre,
            "cer": num(r[2]),
            "cera": num(r[3]),
            "total": num(r[4]),
        })
    return out


def parse_edad(path: str) -> list[dict]:
    out = []
    started = False
    for r in rows(path):
        a = str(r[0] or "").strip()
        if a.lower().startswith("total nacional"):
            started = True
            continue
        if not started:
            continue
        if not a:
            break
        out.append({
            "grupo": a,
            "mujeres": num(r[1]),
            "hombres": num(r[2]),
            "total": num(r[3]),
        })
    return out


def parse_nuevos(path: str) -> list[dict]:
    out = []
    for r in rows(path):
        a, b = (r + ("",))[:2]
        if str(a or "").strip().lower().startswith("total general"):
            continue
        if not is_code(a):
            continue
        out.append({
            "codigo": str(a).strip(),
            "nombre": str(b).strip(),
            "desde_2023": num(r[2]),
            "desde_2024": num(r[3]),
        })
    return out


def parse_cera_paises(path: str, top: int = 20) -> list[dict]:
    out = []
    for r in rows(path):
        a, b = (r + ("",))[:2]
        if str(a or "").strip().lower().startswith("total general"):
            continue
        if not is_code(a):
            continue
        out.append({"codigo": str(a).strip(), "pais": str(b).strip(), "electores": num(r[2])})
    out.sort(key=lambda x: -x["electores"])
    return out[:top]


def main() -> int:
    meta = {"fuente": "INE · Oficina del Censo Electoral", "descargado": datetime.now(timezone.utc).isoformat()}
    paths = {}
    hashes = {}
    for key, fn in FILES.items():
        path, url, sha = download(key, fn)
        paths[key] = path
        hashes[key] = {"url": url, "sha256": sha}

    provincias = parse_provincias(paths["provincias"])
    ccaa = parse_ccaa(paths["ccaa"])
    edad = parse_edad(paths["edad_sexo"])
    nuevos = parse_nuevos(paths["nuevos"])
    cera_paises = parse_cera_paises(paths["cera_paises"])

    total = sum(p["total"] for p in provincias)
    cer = sum(p["cer"] for p in provincias)
    cera = sum(p["cera"] for p in provincias)
    checks = {
        "total": (total, TOTAL),
        "cer": (cer, CER),
        "cera": (cera, CERA),
        "cer+cera": (cer + cera, total),
        "ccaa": (sum(c["total"] for c in ccaa), total),
        "edad": (sum(e["total"] for e in edad), cer),
        "nuevos": (sum(n["desde_2023"] for n in nuevos), NUEVOS),
    }
    bad = {k: v for k, v in checks.items() if v[0] != v[1]}
    if bad:
        print("VALIDACIÓN FALLIDA:", bad)
        return 1

    data = {
        "meta": meta,
        "ficheros": hashes,
        "total": total,
        "cer": cer,
        "cera": cera,
        "nuevos_desde_2023": checks["nuevos"][0],
        "nuevos_desde_2024": sum(n["desde_2024"] for n in nuevos),
        "provincias": sorted(provincias, key=lambda x: -x["total"]),
        "ccaa": sorted(ccaa, key=lambda x: -x["total"]),
        "edad_sexo": edad,
        "nuevos_provincia": sorted(nuevos, key=lambda x: -x["desde_2023"]),
        "cera_paises": cera_paises,
        "nota": (
            "Edad y sexo corresponden a electores residentes en España (CER); "
            "no incluyen a los residentes en el extranjero (CERA)."
        ),
    }
    os.makedirs("data", exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"censo OK · total {total:,} · CER {cer:,} · CERA {cera:,} · nuevos {checks['nuevos'][0]:,}")
    print(f"  provincias {len(provincias)} · CCAA {len(ccaa)} · grupos de edad {len(edad)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
