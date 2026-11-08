#!/usr/bin/env python3
"""Análisis disruptivo interno: dependencia, efecto de casa y leverage.

No modifica la media ni publica. Usa el último sondeo de cada casa para una
aproximación de sensibilidad; no sustituye el recálculo exacto del agregado.
"""
from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LATEST = ROOT / "web" / "data" / "latest.json"
OUT = ROOT / "data" / "disruptive_analysis.json"
PARTIES = ("PP", "PSOE", "VOX", "SUMAR")


def main() -> int:
    data = json.loads(LATEST.read_text(encoding="utf-8"))
    weights = data.get("weights", {})
    polls = weights.get("polls", [])
    poll_weights = [float(p.get("weight") or 0) for p in polls]
    kish = (sum(poll_weights) ** 2 / sum(w * w for w in poll_weights)) if poll_weights else None
    sources = weights.get("sources", [])
    houses = weights.get("houses", [])
    hhi_source = sum((float(s.get("share_pct") or 0) / 100) ** 2 for s in sources)
    hhi_house = sum((float(h.get("share_pct") or 0) / 100) ** 2 for h in houses)
    last = data.get("last_poll_date") or ""
    main = {p["party"]: float(p["mean"]) for p in data.get("parties", []) if p.get("party") in PARTIES}
    try:
        cutoff = (date.fromisoformat(last) - timedelta(days=6)).isoformat()
    except ValueError:
        cutoff = last
    latest_by_house = {
        h.get("pollster"): h
        for h in data.get("house_latest", [])
        if h.get("pollster") and (h.get("date") or "") >= cutoff
    }
    house_weights = {h.get("pollster"): float(h.get("weight") or 0) for h in houses}
    effects = []
    for pollster, h in latest_by_house.items():
        for party in ("PP", "PSOE"):
            value = h.get(party.lower())
            if value is not None:
                effects.append({
                    "pollster": pollster,
                    "party": party,
                    "value": float(value),
                    "minus_main": round(float(value) - main.get(party, 0), 2),
                })
    # Aproximación leave-one-house-out con pesos y última observación de cada casa.
    leverage = []
    for party in ("PP", "PSOE"):
        total = sum(house_weights.get(h, 0) for h in latest_by_house)
        weighted = sum(house_weights.get(h, 0) * float(v[party.lower()])
                       for h, v in latest_by_house.items() if v.get(party.lower()) is not None)
        for pollster in latest_by_house:
            w = house_weights.get(pollster, 0)
            value = latest_by_house[pollster].get(party.lower())
            if value is None or total - w <= 0:
                continue
            new = (weighted - w * float(value)) / (total - w)
            leverage.append({
                "pollster": pollster,
                "party": party,
                "delta": round(new - main.get(party, 0), 2),
                "without": round(new, 2),
            })
    result = {
        "method": "Kish, HHI, efecto de casa y leave-one-house-out aproximado",
        "n_polls": data.get("n_polls"),
        "n_houses": data.get("health", {}).get("n_pollsters"),
        "last_poll_date": last,
        "kish_effective_polls": round(kish, 2) if kish is not None else None,
        "effective_sources": weights.get("effective_sources"),
        "effective_houses": weights.get("effective_houses"),
        "source_hhi": round(hhi_source, 4),
        "house_hhi": round(hhi_house, 4),
        "top_source": {"name": weights.get("top_source"), "share_pct": weights.get("top_source_share_pct")},
        "top_house": {"name": weights.get("top_house"), "share_pct": weights.get("top_share_pct")},
        "house_effect": effects,
        "leave_one_house_out": leverage,
        "caveat": "Sensibilidad descriptiva con el último sondeo de cada casa; no es un intervalo de confianza ni un pronóstico.",
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "kish": result["kish_effective_polls"],
        "source_hhi": result["source_hhi"],
        "house_hhi": result["house_hhi"],
        "top_source": result["top_source"],
        "top_house": result["top_house"],
        "max_leave_one_out": sorted(leverage, key=lambda x: abs(x["delta"]), reverse=True)[:6],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
