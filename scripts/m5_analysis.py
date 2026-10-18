#!/usr/bin/env python3
"""M5 · Meteorología y participación (v1).

Panel provincia × elección. Descriptivo + correlación intra-elección + OLS con
efectos fijos de elección y provincia y errores agrupados por provincia.

No afirma causalidad: mide asociación dentro de cada elección.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

CON = "data/congreso.json"
MET = "data/meteo_electoral.json"
OUT = "data/m5_results.json"


def build_panel() -> pd.DataFrame:
    con = json.load(open(CON, encoding="utf-8"))["elecciones"]
    met = json.load(open(MET, encoding="utf-8"))["elecciones"]
    rows = []
    for date, e in con.items():
        for p in e["provincias"]:
            m = (met.get(date) or {}).get("provincias", {}).get(p["nombre"]) or {}
            if not m.get("n") or p.get("participacion") is None:
                continue
            rows.append({
                "date": date,
                "provincia": p["nombre"],
                "participacion": float(p["participacion"]),
                "prec_media": float(m.get("prec_media") or 0),
                "prec_max": float(m.get("prec_max") or 0),
                "lluvia_pct": float(m.get("lluvia_pct") or 0),
                "tmax_media": float(m["tmax_media"]) if m.get("tmax_media") is not None else np.nan,
                "viento_media": float(m["viento_media"]) if m.get("viento_media") is not None else np.nan,
                "n_estaciones": int(m["n"]),
            })
    df = pd.DataFrame(rows).dropna(subset=["participacion", "prec_media", "tmax_media", "viento_media"])
    return df


def weather_coefs(model) -> dict:
    out = {}
    for name in ("prec_media", "lluvia_pct", "tmax_media", "viento_media"):
        if name not in model.params.index:
            continue
        ci = model.conf_int().loc[name]
        out[name] = {
            "beta": round(float(model.params[name]), 4),
            "se": round(float(model.bse[name]), 4),
            "p": round(float(model.pvalues[name]), 4),
            "ci_low": round(float(ci[0]), 4),
            "ci_high": round(float(ci[1]), 4),
        }
    return out


def fit(df: pd.DataFrame, prec_col: str) -> dict:
    formula = f"participacion ~ {prec_col} + tmax_media + viento_media + C(date) + C(provincia)"
    m = smf.ols(formula, data=df).fit(cov_type="cluster", cov_kwds={"groups": df["provincia"]})
    return {
        "formula": formula,
        "n": int(m.nobs),
        "r2": round(float(m.rsquared), 4),
        "r2_adj": round(float(m.rsquared_adj), 4),
        "coef": weather_coefs(m),
    }


def main() -> int:
    df = build_panel()
    df["part_w"] = df["participacion"] - df.groupby("date")["participacion"].transform("mean")
    df["prec_w"] = df["prec_media"] - df.groupby("date")["prec_media"].transform("mean")
    df["lluvia_w"] = df["lluvia_pct"] - df.groupby("date")["lluvia_pct"].transform("mean")

    corr = {
        "simple": round(float(df["participacion"].corr(df["prec_media"])), 3),
        "within": round(float(df["part_w"].corr(df["prec_w"])), 3),
        "simple_lluvia": round(float(df["participacion"].corr(df["lluvia_pct"])), 3),
        "within_lluvia": round(float(df["part_w"].corr(df["lluvia_w"])), 3),
    }

    bins = pd.cut(df["prec_media"], bins=[-0.01, 0, 1, 5, 1000],
                  labels=["0 mm", "0–1 mm", "1–5 mm", ">5 mm"])
    b = df.groupby(bins, observed=True).agg(
        n=("participacion", "size"),
        part=("participacion", "mean"),
        part_w=("part_w", "mean"),
    ).reset_index()
    bins_out = [{
        "label": str(r["prec_media"]),
        "n": int(r["n"]),
        "part": round(float(r["part"]), 2),
        "part_within": round(float(r["part_w"]), 2),
    } for _, r in b.iterrows()]

    modelo = fit(df, "prec_media")
    modelo_lluvia = fit(df, "lluvia_pct")

    robust = {}
    for name, sub in (
        ("desde_2004", df[df["date"] >= "2004-01-01"]),
        ("n_estaciones_3", df[df["n_estaciones"] >= 3]),
    ):
        if len(sub) > 100:
            robust[name] = fit(sub, "prec_media")

    data = {
        "meta": {
            "generado": datetime.now(timezone.utc).isoformat(),
            "n": int(len(df)),
            "elecciones": int(df["date"].nunique()),
            "provincias": int(df["provincia"].nunique()),
            "fuente_participacion": "Ministerio del Interior (XLSX provincial)",
            "fuente_meteo": "AEMET OpenData",
        },
        "corr": corr,
        "bins": bins_out,
        "modelo": modelo,
        "modelo_lluvia": modelo_lluvia,
        "robustez": robust,
        "limites": [
            "Asociación observacional, no causalidad.",
            "Cobertura de estaciones desigual (1977–1982: 120–140 estaciones).",
            "La precipitación se agrega por provincia; oculta variación local.",
            "EF de elección y provincia; errores agrupados por provincia.",
            "No se predice participación ni voto.",
        ],
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"M5 OK · n={data['meta']['n']} · corr simple {corr['simple']} · within {corr['within']}")
    for k, v in data["modelo"]["coef"].items():
        print(f"  {k}: {v['beta']} (IC {v['ci_low']}–{v['ci_high']}, p={v['p']})")
    print("  bins:", [(x['label'], x['part'], x['part_within']) for x in bins_out])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
