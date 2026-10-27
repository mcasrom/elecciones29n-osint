#!/usr/bin/env python3
"""Empaqueta la versión publicable de 29N para Zenodo.

No incluye sondeos individuales de terceros ni datos personales. Incluye datos
oficiales, agregados propios publicados y metadatos de fuentes.
"""
from __future__ import annotations

import hashlib
import json
import os
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "export"
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
CUT = "2026-10-27"
ZIP = OUT / f"29n-open-data-v{VERSION}-{CUT.replace('-', '')}.zip"

FILES = [
    "README.md", "data/README.md", "docs/LEGAL-29N.md", "data/fuentes_sondeos.csv",
    "web/data/latest.json", "web/data/robustez.json",
    "web/data/censo-2026.json", "web/data/censo-cera.csv", "web/data/censo-edad.csv",
    "web/data/censo-nuevos.csv", "web/data/censo-provincias.csv",
    "web/data/participacion.json", "web/data/participacion.csv",
    "web/data/participacion-provincial.json",
    "web/data/escanos-2026.json", "web/data/escanos-2026.csv",
    "web/data/congreso-oficial.json", "web/data/resultados-2023.csv",
    "web/data/resultados-2023.json", "web/data/cis-m4-2023.csv",
    "web/data/cis-m4-2026.json", "web/data/m5-results.json",
    "web/data/meteo-electoral.csv", "web/data/meteo-electoral.json",
    "web/data/meteo-electoral-provincias.csv",
    "web/data/v1/schema.json", "web/data/v1/latest.json", "web/data/v1/robustez.json",
]

README = f"""# Observatorio electoral 29N — datos abiertos ({CUT})

Snapshot **v{VERSION}** de los datos publicados por el Observatorio 29N.
No es un pronóstico ni una estimación propia de intención de voto.

## Qué incluye

- Agregado y robustez publicados (`latest.json`, `robustez.json`).
- Censo 2026, participación, territorio y resultados oficiales de 2023.
- M4 (CIS 3582), M5 (meteorología) y metadatos de fuentes.
- Contrato de datos v1 y esquema.
- Fuentes y nota legal.

## Qué NO incluye

- **`polls_history.csv` ni filas individuales de sondeos de terceros.**
  Onda Cero sigue pendiente de autorización y cada casa conserva derechos sobre
  sus datos. Se incorporará en una v2 solo con permisos.
- **`subs.db`, logs, correos, `data/raw` ni microdatos personales.**

## Licencia

- **Datos propios y agregados:** CC BY 4.0, citando el proyecto.
- **Código:** AGPL-3.0 (repositorio).
- **Datos oficiales:** conservan la licencia de su fuente (INE, JEC, BOE,
  Ministerio del Interior, CIS, AEMET). Ver `SOURCES.md` y `docs/LEGAL-29N.md`.

## Cita

Miguel Castillo. *Observatorio electoral 29N — datos abiertos* (v{VERSION},
{CUT}). https://elecciones29n.pruebapublica.com

## Límites

- La media es de sondeos publicados, no una encuesta propia.
- El rango es dispersión observada, no intervalo de confianza.
- El hemiciclo es una simulación D'Hondt, no una proyección.
- No se publican resultados el 24–28 de noviembre (blackout LOREG).
"""

SOURCES = """# Fuentes y licencias

- **INE** — censo, participación, IPV/IPC: CC BY 4.0; citar INE.
- **JEC** — participación: citar fuente.
- **BOE / RD 806/2026** — escaños: citar BOE.
- **Ministerio del Interior** — resultados 2023: CC BY 4.0.
- **CIS** — estudio 3582: citar «Origen: CIS», conservar metadatos y no
  desnaturalizar.
- **AEMET OpenData** — meteorología: citar AEMET.
- **Electomanía** — autorización limitada del 23-oct-2026; no se incluyen sus
  tablas, gráficos ni microdatos.
- **Onda Cero** — compilación de sondeos; autorización pendiente; **no se
  incluyen sus filas individuales**.
"""

LICENSE_DATA = """# Licencia de los datos

Salvo donde se indique otra cosa, los datos propios y agregados de este paquete
se publican bajo **Creative Commons Atribución 4.0 Internacional (CC BY 4.0)**:
https://creativecommons.org/licenses/by/4.0/

Debes citar: «Miguel Castillo. Observatorio electoral 29N — datos abiertos».

Los datos oficiales conservan la licencia de su fuente (INE, JEC, BOE,
Ministerio del Interior, CIS, AEMET). Los sondeos individuales de terceros no
se incluyen en esta versión. El código del proyecto es AGPL-3.0.
"""

CITATION = f"""cff-version: 1.2.0
title: "Observatorio electoral 29N — datos abiertos"
message: "Si usas estos datos, cita esta referencia"
authors:
  - family-names: Castillo
    given-names: Miguel
version: "{VERSION}"
date-released: "{CUT}"
url: "https://elecciones29n.pruebapublica.com"
license: "CC-BY-4.0"
"""

META = {
    "metadata": {
        "title": f"Observatorio electoral 29N — datos abiertos (v{VERSION}, {CUT})",
        "upload_type": "dataset",
        "description": ("Snapshot de datos oficiales y agregados publicados por el Observatorio 29N: "
                        "censo 2026, participación, territorio, resultados 2023, M4, M5 y agregado de sondeos. "
                        "No incluye filas individuales de sondeos de terceros ni datos personales."),
        "creators": [{"name": "Castillo, Miguel"}],
        "license": "cc-by-4.0",
        "keywords": ["elecciones", "29N", "España", "sondeos", "participación", "censo", "datos abiertos"],
        "version": VERSION,
        "language": "spa",
        "publication_date": CUT,
        "access_right": "open",
        "related_identifiers": [
            {"identifier": "https://elecciones29n.pruebapublica.com", "relation": "isSupplementTo", "scheme": "url"},
            {"identifier": "https://github.com/mcasrom/elecciones29n-osint", "relation": "isSupplementTo", "scheme": "url"},
        ],
    }
}


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda: f.read(65536), b""):
            h.update(b)
    return h.hexdigest()


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    files = []
    for rel in FILES:
        p = ROOT / rel
        if not p.is_file():
            print("AVISO: falta", rel)
            continue
        files.append((rel, p))
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("README-DATASET.md", README)
        z.writestr("SOURCES.md", SOURCES)
        z.writestr("LICENSE-DATA.md", LICENSE_DATA)
        z.writestr("CITATION.cff", CITATION)
        z.writestr("zenodo-metadata.json", json.dumps(META, ensure_ascii=False, indent=2))
        for rel, p in files:
            z.write(p, rel)
        sums = "\n".join(f"{sha(p)}  {rel}" for rel, p in files) + "\n"
        z.writestr("checksums.sha256", sums)
    (OUT / "zenodo-metadata.json").write_text(json.dumps(META, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "README-DATASET.md").write_text(README, encoding="utf-8")
    (OUT / "SOURCES.md").write_text(SOURCES, encoding="utf-8")
    print(f"OK: {ZIP} ({ZIP.stat().st_size/1024:.1f} KB), {len(files)} ficheros")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
