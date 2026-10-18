#!/usr/bin/env python3
"""Auditoría de coherencia y fuentes de los datos publicados.

Uso:
    python scripts/audit_datos.py            # offline (recalcula y contrasta anclas)
    python scripts/audit_datos.py --online   # además contrasta Onda Cero y CIS

Escribe data/audit_report.json y sale 1 si alguna comprobación crítica falla.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
import statistics
import sys
import urllib.request
from datetime import date, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from agg.aggregate import aggregate, CANON  # noqa: E402
from metrics import moving_average, series_span  # noqa: E402

OUT = "data/audit_report.json"
CHECKS = []


def check(cid, ok, detail="", critical=True):
    CHECKS.append({"id": cid, "ok": bool(ok), "detail": str(detail), "critical": critical})
    return bool(ok)


def approx(a, b, tol=0.01):
    try:
        return abs(float(a) - float(b)) <= tol
    except Exception:
        return False


def load(path, default=None):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--online", action="store_true")
    a = ap.parse_args()

    # ---------------- Sondeos ----------------
    hist = "data/polls_history.csv"
    rows = list(csv.DictReader(open(hist, encoding="utf-8", newline="")))
    check("polls.filas", len(rows) > 0, f"{len(rows)} filas")
    check("polls.campos", all(set(r) == {"party", "date", "value", "source_url", "sample", "pollster", "kind"} for r in rows), "cabecera")
    polls = {}
    bad_val = bad_date = 0
    for r in rows:
        p = r["party"].strip()
        try:
            d = datetime.strptime(r["date"], "%Y-%m-%d").date()
            v = float(r["value"])
        except Exception:
            bad_date += 1
            continue
        if not (0 <= v <= 100):
            bad_val += 1
        if d > date.today():
            bad_date += 1
        polls.setdefault((r["date"], r["pollster"]), {})[p] = v
    check("polls.valores", bad_val == 0, f"{bad_val} fuera de 0-100")
    check("polls.fechas", bad_date == 0, f"{bad_date} fechas inválidas/futuras")

    dup = 0
    seen = set()
    for r in rows:
        key = (r["party"], r["date"], r["pollster"])
        dup += key in seen
        seen.add(key)
    check("polls.duplicados", dup == 0, f"{dup} duplicados (partido,fecha,casa)")

    bad_sum = []
    for (d, pollster), vals in polls.items():
        s = round(sum(vals.values()), 1)
        if not (90 <= s <= 110):
            bad_sum.append((d, pollster, s))
    check("polls.suma", not bad_sum, f"{len(bad_sum)} sondeos fuera de 90-110: {bad_sum[:3]}")

    latest = load("web/data/latest.json", {})
    check("latest.existe", bool(latest), "web/data/latest.json")
    comp = aggregate()
    check("latest.n_polls", latest.get("n_polls") == comp.get("n_polls"), f"{latest.get('n_polls')} vs {comp.get('n_polls')}")
    check("latest.n_pollsters", latest.get("health", {}).get("n_pollsters") == comp.get("health", {}).get("n_pollsters"), "encuestadoras")
    check("latest.window", latest.get("window_span") == comp.get("window_span"), f"{latest.get('window_span')} vs {comp.get('window_span')}")

    for p in comp.get("parties", []):
        q = next((x for x in latest.get("parties", []) if x["party"] == p["party"]), None)
        check(f"latest.{p['party']}.mean", q and approx(p["mean"], q["mean"]), f"{p['mean']} vs {q and q['mean']}")
        check(f"latest.{p['party']}.minmax", q and p["min"] <= p["mean"] <= p["max"], "media dentro de min-max")
        check(f"latest.{p['party']}.n", q and p["n"] == q["n"], f"{p['n']} vs {q and q['n']}")

    h = latest.get("health", {})
    check("health.n_polls", h.get("n_polls") == latest.get("n_polls"), f"{h.get('n_polls')} vs {latest.get('n_polls')}")
    check("health.status", h.get("status") in ("ok", "warn", "bad"), h.get("status"))
    check("health.n_pollsters", h.get("n_pollsters", 0) >= 1, h.get("n_pollsters"))

    hm = latest.get("house_mean", {})
    check("house.n", hm.get("n_houses", 0) >= 1, hm.get("n_houses"))
    for p in hm.get("parties", []):
        check(f"house.{p['party']}.range", p["min"] <= p["mean"] <= p["max"], f"{p['party']}")

    span = series_span(latest.get("series_long", {}))
    check("series.span", bool(span), span)
    check("series.fechas", all(d <= date.today().isoformat() for d in latest.get("series_long", {}).get("PP", []) for d in [d["date"]]), "sin fechas futuras")
    ma = moving_average(latest.get("series_long", {}).get("PP", []))
    check("series.ma", len(ma) >= 1, f"MA PP {len(ma)} puntos")

    idx = open("web/index.html", encoding="utf-8", errors="ignore").read() if os.path.exists("web/index.html") else ""
    for label in ("media móvil de 14 días", "Salud de la muestra", "Otros", "pasa el cursor"):
        check(f"ui.index.{label}", label in idx, label)

    # ---------------- Censo ----------------
    cen = load("data/censo_2026.json", {})
    check("censo.total", cen.get("total") == 38_728_356, cen.get("total"))
    check("censo.cer", cen.get("cer") == 35_958_711, cen.get("cer"))
    check("censo.cera", cen.get("cera") == 2_769_645, cen.get("cera"))
    check("censo.suma", cen.get("cer", 0) + cen.get("cera", 0) == cen.get("total"), "CER+CERA")
    provs = cen.get("provincias", [])
    check("censo.provincias", len(provs) == 52, len(provs))
    check("censo.suma_prov", sum(p["total"] for p in provs) == cen.get("total"), "suma provincias")
    check("censo.edad", sum(e["total"] for e in cen.get("edad_sexo", [])) == cen.get("cer"), "suma edad = CER")
    check("censo.nuevos", cen.get("nuevos_desde_2023") == 1_615_127, cen.get("nuevos_desde_2023"))
    check("censo.sha", all(len(f.get("sha256", "")) == 64 for f in cen.get("ficheros", {}).values()), "SHA-256")

    # ---------------- Participación ----------------
    par = load("data/participacion.json", {})
    els = par.get("elecciones", [])
    check("part.n", len(els) == 15, len(els))
    by = {e["eleccion"]: e["participacion"] for e in els}
    check("part.2023", approx(by.get("2023"), 66.59, 0.01), by.get("2023"))
    check("part.max", approx(max(by.values()), 79.97, 0.01), max(by.values()))
    check("part.min", approx(min(by.values()), 66.23, 0.01), min(by.values()))
    check("part.fechas", all(e.get("fecha") for e in els), "fechas completas")

    pp = load("data/participacion_provincial.json", {})
    pels = pp.get("elecciones", {})
    check("partprov.n", len(pels) >= 15, len(pels))
    e23 = pels.get("2023-07-23", {})
    check("partprov.2023", approx(e23.get("nacional", {}).get("participacion"), 66.59, 0.01), e23.get("nacional", {}).get("participacion"))
    check("partprov.prov", len(e23.get("provincias", [])) == 52, len(e23.get("provincias", [])))
    check("partprov.suma_e", sum(p["electores"] for p in e23.get("provincias", [])) == e23.get("nacional", {}).get("electores"), "suma electores")
    check("partprov.suma_v", sum(p["votantes"] for p in e23.get("provincias", [])) == e23.get("nacional", {}).get("votantes"), "suma votantes")

    # ---------------- Congreso / territorio ----------------
    con = load("data/congreso.json", {})
    e23c = con.get("elecciones", {}).get("2023-07-23", {}).get("nacional", {})
    check("congreso.2023_part", approx(e23c.get("participacion"), 66.59, 0.01), e23c.get("participacion"))
    check("congreso.2023_escanos", sum(e23c.get("escanos", {}).values()) == 350, sum(e23c.get("escanos", {}).values()))
    for p, n in (("PP", 137), ("PSOE", 121), ("VOX", 33), ("SUMAR", 31), ("ERC", 7), ("JUNTS", 7), ("EH Bildu", 6), ("PNV", 5), ("BNG", 1), ("CCa", 1), ("UPN", 1)):
        check(f"congreso.{p}", e23c.get("escanos", {}).get(p) == n, e23c.get("escanos", {}).get(p))
    check("congreso.gallagher", 5.0 <= e23c.get("gallagher", 0) <= 7.0, e23c.get("gallagher"))

    esc = load("data/escanos_2026.json", {})
    esp = esc.get("provincias", [])
    check("escanos.total", esc.get("total_escanos") == 350, esc.get("total_escanos"))
    check("escanos.prov", len(esp) == 52, len(esp))
    check("escanos.suma", sum(p["escanos"] for p in esp) == 350, "suma 350")
    eb = {p["nombre"]: p for p in esp}
    for name, n in (("Madrid", 38), ("Barcelona", 32), ("Teruel", 3), ("Soria", 2), ("Ceuta", 1), ("Melilla", 1)):
        check(f"escanos.{name}", eb.get(name, {}).get("escanos") == n, eb.get(name, {}).get("escanos"))
    check("escanos.electores", sum(p["electores"] for p in esp) == cen.get("total"), "suma = censo")

    res = "web/data/resultados-2023.csv"
    if os.path.exists(res):
        rr = list(csv.DictReader(open(res, encoding="utf-8")))
        check("resultados.rows", len(rr) > 10, len(rr))
        check("resultados.escanos", sum(int(r["escanos"]) for r in rr) == 350, "suma escanos")
        check("resultados.pp", any(r["partido"] == "PP" and int(r["escanos"]) == 137 for r in rr), "PP 137")

    # ---------------- M4 ----------------
    m4 = load("data/cis_m4_2026.json", {})
    check("m4.muestra", m4.get("meta", {}).get("muestra") == 5025, m4.get("meta", {}).get("muestra"))
    check("m4.edad", len(m4.get("edad", {}).get("grupos", [])) == 7, "7 grupos")
    check("m4.sexo", len(m4.get("sexo", {}).get("grupos", [])) == 2, "2 grupos")
    check("m4.ideologia", len(m4.get("ideologia", {}).get("grupos", [])) == 3, "3 grupos")
    for dim in ("edad", "sexo", "ideologia"):
        for g in m4.get(dim, {}).get("grupos", []):
            for p, v in g.get("partidos", {}).items():
                check(f"m4.{dim}.{g['nombre']}.{p}.n", v["suppressed"] == (v["n"] < 30), f"{v['n']}")
    sex = {g["nombre"]: g for g in m4.get("sexo", {}).get("grupos", [])}
    check("m4.mujer_psoe", approx(sex.get("Mujer", {}).get("partidos", {}).get("PSOE", {}).get("pct"), 49.1, 0.1), sex.get("Mujer", {}).get("partidos", {}).get("PSOE", {}).get("pct"))
    check("m4.hombre_psoe", approx(sex.get("Hombre", {}).get("partidos", {}).get("PSOE", {}).get("pct"), 37.6, 0.1), sex.get("Hombre", {}).get("partidos", {}).get("PSOE", {}).get("pct"))

    comp_page = open("web/comportamiento.html", encoding="utf-8", errors="ignore").read() if os.path.exists("web/comportamiento.html") else ""
    for label in ("n&lt;30", "voto declarado", "N ponderado", "Recuerdo de voto 2023"):
        check(f"ui.m4.{label}", label in comp_page, label)

    # ---------------- M5 ----------------
    met = load("data/meteo_electoral.json", {})
    check("meteo.n", len(met.get("elecciones", {})) == 16, len(met.get("elecciones", {})))
    check("meteo.2023", len(met.get("elecciones", {}).get("2023-07-23", {}).get("provincias", {})) == 52, "52 provincias")
    m5 = load("data/m5_results.json", {})
    check("m5.n", 700 <= m5.get("meta", {}).get("n", 0) <= 850, m5.get("meta", {}).get("n"))
    check("m5.bins", len(m5.get("bins", [])) == 4, len(m5.get("bins", [])))
    c = m5.get("modelo", {}).get("coef", {}).get("prec_media", {})
    check("m5.coef", c.get("ci_low", 0) <= c.get("beta", 0) <= c.get("ci_high", 0), c)
    check("m5.robust", "desde_2004" in m5.get("robustez", {}), "robustez 2004")
    fac = open("web/factores.html", encoding="utf-8", errors="ignore").read() if os.path.exists("web/factores.html") else ""
    for label in ("Resultados (v1)", "Datos meteorológicos usados", "no causalidad"):
        check(f"ui.m5.{label}", label in fac, label)

    # ---------------- Fuentes online ----------------
    if a.online:
        try:
            from ingest.ondacero import fetch_html, parse_html, MAP as OCMAP
            online = parse_html(fetch_html())
            page_map = {}
            for p in online:
                for k, v in (p.get("v") or {}).items():
                    party = OCMAP.get(k)
                    if party and v is not None:
                        page_map[(str(p.get("pub")), str(p.get("fuente")), party)] = float(v)
            hist_map = {}
            for r in rows:
                if "ondacero.es" in r.get("source_url", ""):
                    hist_map[(r["date"], r["pollster"], r["party"])] = float(r["value"])
            mism = sum(1 for k, v in hist_map.items() if k in page_map and not approx(page_map[k], v, 0.01))
            miss = sum(1 for k in hist_map if k not in page_map)
            check("online.ondacero", mism == 0 and miss == 0,
                  f"hist={len(hist_map)} page={len(page_map)} mismatches={mism} missing={miss}", critical=False)
        except Exception as e:
            check("online.ondacero", False, f"error: {e}", critical=False)

        try:
            import subprocess, tempfile
            url = "https://www.cis.es/documents/d/guest/3582_estimacion-pdf"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30) as r:
                pdf = r.read()
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
                f.write(pdf)
                path = f.name
            txt = subprocess.check_output(["pdftotext", "-layout", path, "-"], text=True)
            os.unlink(path)
            cis_hist = {}
            for r in rows:
                if r["date"] == "2026-10-14" and r["pollster"] == "CIS":
                    cis_hist[CANON.get(r["party"], r["party"])] = float(r["value"])
            anchors = {
                "PSOE": (34.0, "PSOE"), "PP": (22.2, "PP"), "VOX": (17.1, "VOX"),
                "SUMAR": (6.1, "SUMAR"), "PODEMOS": (3.1, "Podemos"), "ERC": (3.0, "ERC"),
                "BILDU": (1.6, "EH Bildu"), "JUNTS": (1.1, "Junts"),
                "PNV": (0.6, "EAJ-PNV"), "SAF": (1.8, "Se Acabó la Fiesta"),
            }
            for key, (val, label) in anchors.items():
                pat = re.compile(label + r"[^\n]{0,140}?[\d,]+\s+±[\d,]+\s+([\d,]+)")
                m = pat.search(txt)
                got = float(m.group(1).replace(",", ".")) if m else None
                histv = cis_hist.get(key)
                ok = got is not None and approx(got, val, 0.05) and histv is not None and approx(histv, val, 0.05)
                check(f"online.cis.{key}", ok, f"pdf={got} hist={histv} esperado={val}", critical=False)
        except Exception as e:
            check("online.cis", False, f"error: {e}", critical=False)

        try:
            from ingest.electomania import fetch_posts, extract_poll
            posts = fetch_posts()
            target = None
            for post in posts:
                poll = extract_poll(post)
                if poll and poll["date"] == "2026-10-11":
                    target = poll
                    break
            histv = {r["party"]: float(r["value"]) for r in rows
                     if r["date"] == "2026-10-11" and r["pollster"] == "ElectoPanel"}
            if target:
                mism = sum(1 for k, v in target["values"].items()
                           if k in histv and not approx(v, histv[k], 0.01))
                check("online.electomania", mism == 0 and bool(histv),
                      f"mismatches={mism} hist={len(histv)}", critical=False)
            else:
                check("online.electomania", False, "no se encontró el panel del 11-oct", critical=False)
        except Exception as e:
            check("online.electomania", False, f"error: {e}", critical=False)

    # ---------------- Informe ----------------
    failed = [c for c in CHECKS if not c["ok"] and c["critical"]]
    report = {
        "generado": datetime.now().isoformat(),
        "online": a.online,
        "total": len(CHECKS),
        "failed": len(failed),
        "checks": CHECKS,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    for c in CHECKS:
        if not c["ok"]:
            print(("FAIL " if c["critical"] else "WARN ") + c["id"] + " · " + c["detail"])
    print(f"auditoría: {len(CHECKS)} comprobaciones · {len(failed)} fallos críticos · online={a.online}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
