from __future__ import annotations

import json
import os
import re
import sys
import unicodedata
import urllib.request
from datetime import datetime, timezone

BASE = "https://opendata.aemet.es/opendata/api"
OUT = "data/meteo_electoral.json"
CONGRESO = "data/congreso.json"

MAP = {
    "A CORUNA": "Coruña, A",
    "ALICANTE": "Alicante / Alacant",
    "ARABA/ALAVA": "Araba/Álava",
    "BALEARES": "Balears, Illes",
    "ILLES BALEARS": "Balears, Illes",
    "CASTELLON": "Castellón / Castelló",
    "LA RIOJA": "Rioja, La",
    "LAS PALMAS": "Palmas, Las",
    "SANTA CRUZ DE TENERIFE": "Santa Cruz de Tenerife",
    "STA. CRUZ DE TENERIFE": "Santa Cruz de Tenerife",
    "VALENCIA": "Valencia / València",
}


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", str(s or ""))
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.upper().replace(".", "").strip()
    s = re.sub(r"\s+", " ", s)
    return s


def load_key() -> str:
    key = os.environ.get("AEMET_API_KEY", "").strip()
    if key:
        return key
    # fallback local del ecosistema (solo servidor)
    for path in ("/home/deploy/nearme-osint/.env",):
        if os.path.exists(path):
            for line in open(path, encoding="utf-8"):
                if line.startswith("AEMET_API_KEY="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit("falta AEMET_API_KEY (env)")


def fetch_json(url: str) -> object:
    req = urllib.request.Request(url, headers={"User-Agent": "elecciones29n-osint/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        raw = r.read()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        text = raw.decode("latin-1")
    return json.loads(text)


def fetch_day(date: str, key: str) -> list[dict]:
    q = f"{BASE}/valores/climatologicos/diarios/datos/fechaini/{date}T00:00:00UTC/fechafin/{date}T23:59:59UTC/todasestaciones?api_key={key}"
    d = fetch_json(q)
    if not isinstance(d, dict) or d.get("estado") != 200 or not d.get("datos"):
        raise RuntimeError(f"AEMET {date}: {d}")
    data = fetch_json(d["datos"])
    if not isinstance(data, list):
        raise RuntimeError(f"AEMET {date}: datos no es lista")
    return data


def num(s):
    if s is None or s == "":
        return None
    if str(s).strip().lower() == "ipyn":
        return 0.05
    try:
        return float(str(s).replace(",", "."))
    except ValueError:
        return None


def main() -> int:
    key = load_key()
    dates = sorted(json.load(open(CONGRESO, encoding="utf-8"))["elecciones"])
    censo = json.load(open("data/censo_2026.json", encoding="utf-8"))
    by_norm = {norm(p["nombre"]): p["nombre"] for p in censo["provincias"]}
    out = {}
    for date in dates:
        rows = fetch_day(date, key)
        acc: dict[str, dict] = {}
        for r in rows:
            rawa = r.get("provincia")
            name = MAP.get(norm(rawa)) or by_norm.get(norm(rawa))
            if not name:
                continue
            a = acc.setdefault(name, {"prec": [], "tmax": [], "tmin": [], "viento": []})
            for k, src in (("prec", "prec"), ("tmax", "tmax"), ("tmin", "tmin"), ("viento", "velmedia")):
                v = num(r.get(src))
                if v is not None:
                    a[k].append(v)
        provs = {}
        missing = []
        for name in by_norm.values():
            a = acc.get(name)
            if not a or not a["prec"]:
                missing.append(name)
                provs[name] = {"n": 0}
                continue
            n = len(a["prec"])
            provs[name] = {
                "n": n,
                "prec_media": round(sum(a["prec"]) / n, 2),
                "prec_max": round(max(a["prec"]), 2),
                "lluvia_pct": round(100.0 * sum(1 for x in a["prec"] if x > 0) / n, 1),
                "tmax_media": round(sum(a["tmax"]) / len(a["tmax"]), 1) if a["tmax"] else None,
                "tmin_media": round(sum(a["tmin"]) / len(a["tmin"]), 1) if a["tmin"] else None,
                "viento_media": round(sum(a["viento"]) / len(a["viento"]), 1) if a["viento"] else None,
            }
        out[date] = {"n_estaciones": len(rows), "provincias": provs}
        print(f"{date}: {len(rows)} estaciones · {52-len(missing)}/52 provincias"
              + (f" · faltan: {', '.join(missing)}" if missing else ""))

    data = {
        "meta": {
            "fuente": "AEMET OpenData · valores climatológicos diarios",
            "descargado": datetime.now(timezone.utc).isoformat(),
            "nota": "Agregado por provincia: media/máximo de precipitación, % estaciones con lluvia, tmax/tmin y viento medio. 'Ipyn' = 0,05 mm.",
        },
        "elecciones": out,
    }
    os.makedirs("data", exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("escrito", OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
