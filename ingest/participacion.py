from __future__ import annotations

import json
import os
import re
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone

API = "https://es.wikipedia.org/w/api.php"
PAGE = "Elecciones generales de España"
UA = "elecciones29n-osint/1.0 (https://elecciones29n.pruebapublica.com; contacto: mcasrom@gmail.com)"
OUT = "data/participacion.json"


def fetch_wikitext() -> str:
    q = urllib.parse.urlencode({
        "action": "parse", "page": PAGE, "prop": "wikitext",
        "format": "json", "formatversion": "2",
    })
    req = urllib.request.Request(f"{API}?{q}", headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=40) as r:
        d = json.loads(r.read().decode())
    return d["parse"]["wikitext"]


def normaliza(label: str) -> tuple[str, int]:
    s = label.strip()
    if "abril" in s.lower():
        return "2019 (abr)", 2019
    if "noviembre" in s.lower() and "2019" in s:
        return "2019 (nov)", 2019
    m = re.search(r"(\d{4})", s)
    y = int(m.group(1)) if m else 0
    return str(y), y


def parse(wt: str) -> list[dict]:
    i = wt.find('{| class="wikitable sortable"')
    j = wt.find("\n|}", i)
    if i < 0 or j < 0:
        raise SystemExit("no se encontró la tabla de participación")
    table = wt[i:j]
    out = []
    for block in table.split("\n|-")[1:]:
        m_year = re.search(r"\[\[Elecciones generales de España de ([^\]|]+)", block)
        m_val = re.search(r"\{\{porcentaje\|([\d,]+)\|", block)
        m_url = re.search(r"url=(https://www\.juntaelectoralcentral\.es[^\s|}]+)", block)
        if not (m_year and m_val):
            continue
        label, year = normaliza(m_year.group(1))
        value = float(m_val.group(1).replace(",", "."))
        if value <= 0:
            continue
        out.append({
            "eleccion": label,
            "year": year,
            "participacion": value,
            "fuente_url": m_url.group(1) if m_url else "",
        })
    out.sort(key=lambda r: (r["year"], r["eleccion"]))
    return out


def main() -> int:
    rows = parse(fetch_wikitext())
    if len(rows) < 15:
        print(f"VALIDACIÓN FALLIDA: solo {len(rows)} elecciones")
        return 1
    by = {r["eleccion"]: r["participacion"] for r in rows}
    checks = {
        "2023": (by.get("2023"), 66.59),
        "1982_max": (max(r["participacion"] for r in rows), 79.97),
        "2019nov_min": (by.get("2019 (nov)"), 66.23),
    }
    bad = {k: v for k, v in checks.items() if v[0] != v[1]}
    if bad:
        print("VALIDACIÓN FALLIDA:", bad)
        return 1

    data = {
        "meta": {
            "fuente": "Junta Electoral Central (JEC) · tablas de resultados por elección",
            "transcripcion": "Wikipedia ES (API de parseo, wikitexto) y validación de extremos",
            "descargado": datetime.now(timezone.utc).isoformat(),
            "nota": "Participación nacional sobre censo. Serie 1979–2023; 2026 aún sin datos.",
        },
        "elecciones": rows,
    }
    os.makedirs("data", exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"participación OK · {len(rows)} elecciones · 2023 {by['2023']}% · "
          f"máx {checks['1982_max'][0]} · mín {checks['2019nov_min'][0]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
