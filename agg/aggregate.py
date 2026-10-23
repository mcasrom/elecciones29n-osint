from __future__ import annotations

import csv
import json
import math
import os
import statistics
from datetime import datetime, timedelta
from typing import Any, Dict, List

import pytz

from agg import blackout

TZ = pytz.timezone("Europe/Madrid")
WINDOW_DAYS = 14
LONG_DAYS = 90
HALF_LIFE_DAYS = 10.0
LOW_N = 4
HOUSE_WINDOW_DAYS = 45
CANON = {"Podemos": "PODEMOS", "Bildu": "BILDU", "Junts": "JUNTS", "Cs": "Cs", "C's": "Cs", "Ciudadanos": "Cs"}
HOUSE_NOTA = {"CIS": "estimación de voto"}
# Partidos que solo se presentan en algunas circunscripciones. Se publican,
# pero no se suman a la tabla principal: en Onda Cero ya van dentro de "Otros".
TERRITORIAL = {"ERC", "JUNTS", "BILDU", "PNV"}


def _parse_date(s: str) -> datetime | None:
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d/%m/%y"):
        try:
            return TZ.localize(datetime.strptime(s.strip(), fmt))
        except Exception:
            continue
    return None


def load_polls() -> List[Dict[str, Any]]:
    hist = "data/polls_history.csv"
    if not os.path.exists(hist):
        return []
    polls: List[Dict[str, Any]] = []
    seen: Dict[tuple, int] = {}
    with open(hist, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            party = (row.get("party") or "").strip()
            party = CANON.get(party, party)
            dt = _parse_date(row.get("date") or "")
            try:
                val = float((row.get("value") or "").replace("%", "").strip())
            except Exception:
                continue
            if not party or dt is None or not (0 <= val <= 100):
                continue
            sample = row.get("sample") or ""
            try:
                sample_i = int(sample) if sample else None
            except ValueError:
                sample_i = None
            pollster = (row.get("pollster") or "Electomania").strip()
            kind = (row.get("kind") or "tracking").strip().lower()
            key = (party, dt.strftime("%Y-%m-%d"), pollster)
            item = {
                    "party": party,
                    "date": dt,
                    "value": val,
                    "source_url": (row.get("source_url") or "").strip(),
                    "sample": sample_i,
                    "pollster": pollster,
                    "kind": kind,
                }
            if key in seen:
                polls[seen[key]] = item
            else:
                seen[key] = len(polls)
                polls.append(item)
    return polls


def _iqr(vals: List[float]) -> float:
    """Rango intercuartilico (Q3-Q1); 0 si hay menos de 2 valores."""
    if len(vals) < 2:
        return 0.0
    q = statistics.quantiles(vals, n=4)
    return q[2] - q[0]


def _cutoff_date(now: datetime, days: int):
    """Corte por fecha natural: 'days' días contando hoy (14 -> hace 13 días).

    La ventana no puede depender de la hora del build: con un corte por
    timestamp, un sondeo del día 14 entraba a las 23:00 y salía a las 08:00.
    """
    return now.date() - timedelta(days=max(0, days - 1))


def _weight(p: Dict[str, Any], now: datetime) -> float:
    # Edad en días naturales: la fecha del sondeo no tiene hora, así que el
    # peso es estable durante todo el día (08:00 y 23:00 dan lo mismo).
    age_days = float(max(0, (now.date() - p["date"].date()).days))
    recency = 0.5 ** (age_days / HALF_LIFE_DAYS)
    sample = p.get("sample")
    if sample:
        return math.sqrt(sample / 1000.0) * recency
    return recency


def _poll_source(p: Dict[str, Any]) -> str:
    """Fuente de captacion del sondeo: Onda Cero, Electomania o CIS."""
    url = (p.get("source_url") or "").lower()
    house = p.get("pollster") or ""
    if "ondacero.es" in url:
        return "Onda Cero"
    if "electomania.es" in url:
        return "Electomanía"
    if "cis.es" in url:
        return "CIS"
    if house.startswith("Electo"):
        return "Electomanía"
    if house == "CIS":
        return "CIS"
    return "Otras fuentes"


def _poll_weights(recent: List[Dict[str, Any]], now: datetime, extended: bool) -> Dict[str, Any]:
    """Reparto del peso que usa la media: por fuente, casa y sondeo.

    La cuota se calcula sobre sondeos distintos (fecha + casa), no sobre filas
    por partido: asi una casa que publica mas partidos no pesa mas.
    """
    polls: Dict[tuple, Dict[str, Any]] = {}
    for p in recent:
        day = p["date"].strftime("%Y-%m-%d")
        key = (day, p.get("pollster") or "?")
        row = polls.get(key)
        if row is None:
            row = polls[key] = {
                "pollster": p.get("pollster") or "?",
                "source": _poll_source(p),
                "date": day,
                "sample": p.get("sample"),
                "kind": p.get("kind") or "tracking",
                "weight": _weight(p, now),
                "n_parties": 0,
            }
        row["n_parties"] += 1

    total = sum(r["weight"] for r in polls.values()) or 1.0
    for r in polls.values():
        r["share_pct"] = round(100 * r["weight"] / total, 1)
        r["weight"] = round(r["weight"], 4)

    by_house: Dict[str, Dict[str, Any]] = {}
    for r in polls.values():
        h = by_house.get(r["pollster"])
        if h is None:
            h = by_house[r["pollster"]] = {
                "pollster": r["pollster"],
                "source": r["source"],
                "weight": 0.0,
                "n_polls": 0,
                "last_date": r["date"],
                "sample": None,
                "n_parties": 0,
            }
        h["weight"] += r["weight"]
        h["n_polls"] += 1
        h["last_date"] = max(h["last_date"], r["date"])
        if r["sample"]:
            h["sample"] = max(h["sample"] or 0, r["sample"])
        h["n_parties"] = max(h["n_parties"], r["n_parties"])

    houses = sorted(by_house.values(), key=lambda x: x["weight"], reverse=True)
    for h in houses:
        h["share_pct"] = round(100 * h["weight"] / total, 1)
        h["weight"] = round(h["weight"], 4)

    by_source: Dict[str, Dict[str, Any]] = {}
    for r in polls.values():
        s = by_source.get(r["source"])
        if s is None:
            s = by_source[r["source"]] = {
                "source": r["source"],
                "weight": 0.0,
                "n_polls": 0,
                "n_houses": 0,
            }
        s["weight"] += r["weight"]
        s["n_polls"] += 1
    for h in houses:
        s = by_source.get(h["source"])
        if s is not None:
            s["n_houses"] += 1
    sources = sorted(by_source.values(), key=lambda x: x["weight"], reverse=True)
    for s in sources:
        s["share_pct"] = round(100 * s["weight"] / total, 1)
        s["weight"] = round(s["weight"], 4)

    polls_sorted = sorted(polls.values(), key=lambda x: (x["weight"], x["date"]), reverse=True)
    top = houses[0] if houses else None
    top_src = sources[0] if sources else None
    return {
        "window_days": WINDOW_DAYS,
        "extended": extended,
        "total_polls": len(polls),
        "total_weight": round(total, 4),
        "top_source": top_src["source"] if top_src else None,
        "top_source_share_pct": top_src["share_pct"] if top_src else None,
        "sources": sources,
        "top_house": top["pollster"] if top else None,
        "top_share_pct": top["share_pct"] if top else None,
        "houses": houses,
        "polls": polls_sorted,
    }


def _series(polls: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    out: Dict[str, List[Dict[str, Any]]] = {}
    for p in polls:
        out.setdefault(p["party"], []).append(
            {"date": p["date"].strftime("%Y-%m-%d"), "value": p["value"],
             "pollster": p.get("pollster") or "?"}
        )
    for party in out:
        out[party].sort(key=lambda x: x["date"])
    return out


def _empty(now: datetime, in_blackout: bool) -> Dict[str, Any]:
    return {
        "updated_at": now.strftime("%Y-%m-%d %H:%M %Z"),
        "updated_at_iso": now.isoformat(),
        "in_blackout": in_blackout,
        "blackout_reason": blackout.blackout_reason() if in_blackout else "",
        "parties": [],
        "series": {},
        "series_long": {},
        "n_polls": 0,
        "low_n": True,
        "weights": None,
    }


NOVEDADES_STATE = "data/novedades_state.json"


def _novedades(polls: List[Dict[str, Any]], now: datetime) -> List[Dict[str, str]]:
    """Sondeos nuevos desde la ultima ejecucion. Si la ejecucion es del mismo dia
    y no hay nuevos, se conserva el aviso (para que no desaparezca al reejecutar)."""
    today = now.strftime("%Y-%m-%d")
    cur = {
        (p.get("pollster") or "", p["date"].strftime("%Y-%m-%d"))
        for p in polls
        if (p.get("kind") or "tracking") != "average"
    }
    prev: Dict[str, Any] = {}
    try:
        with open(NOVEDADES_STATE, encoding="utf-8") as f:
            prev = json.load(f)
    except Exception:
        prev = {}
    seen_prev = {tuple(x) for x in prev.get("seen", [])}
    if not seen_prev:
        novedades: List[Dict[str, str]] = []  # primera ejecucion: sembrar sin avisar
    else:
        nuevos = sorted(cur - seen_prev, key=lambda x: x[1], reverse=True)
        novedades = [{"pollster": p, "date": d} for p, d in nuevos if p]
        if not novedades and prev.get("date") == today:
            novedades = prev.get("novedades", [])
    try:
        os.makedirs("data", exist_ok=True)
        tmp = NOVEDADES_STATE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump({"date": today, "seen": sorted(cur), "novedades": novedades[:3]}, f,
                      ensure_ascii=False)
        os.replace(tmp, NOVEDADES_STATE)
    except Exception:
        pass
    return novedades[:3]


def aggregate(out_dir: str = "web/data", now: datetime | None = None) -> Dict[str, Any]:
    now = now or datetime.now(TZ)
    latest_path = os.path.join(out_dir, "latest.json")

    if blackout.is_blackout(now):
        if os.path.exists(latest_path):
            with open(latest_path, encoding="utf-8") as f:
                return json.load(f)
        return _empty(now, True)

    polls_all = load_polls()
    tracking = [p for p in polls_all if p.get("kind") != "average"]
    if not tracking:
        if os.path.exists(latest_path):
            with open(latest_path, encoding="utf-8") as f:
                return json.load(f)
        return _empty(now, False)

    cutoff = _cutoff_date(now, WINDOW_DAYS)
    recent = [p for p in tracking if p["date"].date() >= cutoff]

    # Si la ventana de 14 d no llega a LOW_N sondeos, se extiende a los últimos
    # LOW_N sondeos (máx. LONG_DAYS) para no publicar una "media" de un solo dato.
    recent_dates = sorted({p["date"].strftime("%Y-%m-%d") for p in recent})
    extended = False
    if len(recent_dates) < LOW_N:
        all_dates = sorted({p["date"].strftime("%Y-%m-%d") for p in tracking})
        keep = set(all_dates[-LOW_N:])
        recent = [p for p in tracking if p["date"].strftime("%Y-%m-%d") in keep]
        extended = True
    recent_dates = sorted({p["date"].strftime("%Y-%m-%d") for p in recent})

    # Casas que han publicado cada partido en los 45 días (no solo la última
    # encuesta de cada casa, que es lo que mide n_houses).
    house_cutoff = _cutoff_date(now, HOUSE_WINDOW_DAYS)
    houses_window: Dict[str, set] = {}
    for p in tracking:
        if p["date"].date() >= house_cutoff:
            houses_window.setdefault(p["party"], set()).add(p.get("pollster") or "?")

    by_party: Dict[str, List[Dict[str, Any]]] = {}
    for p in recent:
        by_party.setdefault(p["party"], []).append(p)

    weighted = any(p.get("sample") for p in recent)
    parties = []
    for party, rows in by_party.items():
        vals = [r["value"] for r in rows]
        ws = [_weight(r, now) for r in rows]
        wsum = sum(ws)
        mean = sum(v * w for v, w in zip(vals, ws)) / wsum if wsum else sum(vals) / len(vals)
        rows_sin = [r for r in rows if (r.get("pollster") or "") != "CIS"]
        sin = {}
        if rows_sin:
            vals_s = [r["value"] for r in rows_sin]
            ws_s = [_weight(r, now) for r in rows_sin]
            wsum_s = sum(ws_s)
            mean_s = sum(v * w for v, w in zip(vals_s, ws_s)) / wsum_s if wsum_s else sum(vals_s) / len(vals_s)
            sin = {
                "mean_sin_cis": round(mean_s, 2),
                "median_sin_cis": round(statistics.median(vals_s), 2),
                "min_sin_cis": round(min(vals_s), 2),
                "max_sin_cis": round(max(vals_s), 2),
                "n_sin_cis": len(vals_s),
            }
        parties.append(
            {
                "party": party,
                "mean": round(mean, 2),
                "median": round(statistics.median(vals), 2),
                "min": round(min(vals), 2),
                "max": round(max(vals), 2),
                "n": len(vals),
                "sample_total": sum((r.get("sample") or 0) for r in rows),
                "sample_n": sum(1 for r in rows if (r.get("sample") or 0) > 0),
                "n_houses_window": len(houses_window.get(party, set())),
                "n_houses_recent": len({r.get("pollster") for r in rows if r.get("pollster")}),
                "territorial": party in TERRITORIAL,
                "pollsters": sorted({r.get("pollster") for r in rows if r.get("pollster")}),
                **sin,
            }
        )
    parties.sort(key=lambda x: x["mean"], reverse=True)
    table_sum = round(sum(p["mean"] for p in parties if not p["territorial"]), 2)

    long_cutoff = _cutoff_date(now, LONG_DAYS)
    series_long = _series([p for p in tracking if p["date"].date() >= long_cutoff])
    series = _series(recent)

    poll_dates = sorted({p["date"].strftime("%Y-%m-%d") for p in recent})
    n_polls = len({(p["date"].strftime("%Y-%m-%d"), p.get("pollster")) for p in recent})
    n_polls_sin_cis = len({(p["date"].strftime("%Y-%m-%d"), p.get("pollster")) for p in recent if (p.get("pollster") or "") != "CIS"})
    sources = sorted({p["source_url"] for p in recent if p.get("source_url")})
    means = {p["party"]: p["mean"] for p in parties}
    pollsters = sorted({p.get("pollster") for p in recent if p.get("pollster")})
    n_pollsters = len(pollsters)
    last_poll = poll_dates[-1] if poll_dates else None
    days_since = None
    if last_poll:
        days_since = max(0, (now.date() - datetime.strptime(last_poll, "%Y-%m-%d").date()).days)
    reasons = []
    status = "ok"
    if n_polls < LOW_N:
        status = "bad"
        reasons.append(f"solo {n_polls} sondeos en la media")
    if n_pollsters <= 1:
        status = "bad" if status == "bad" else "warn"
        reasons.append("una sola encuestadora")
    if days_since is not None and days_since > 10:
        status = "bad" if days_since > 21 else ("warn" if status == "ok" else status)
        reasons.append(f"último sondeo hace {days_since} días")
    # Contraste por casa: última encuesta de cada casa (45 d), mismo peso
    house_polls = [p for p in tracking if p["date"].date() >= house_cutoff]
    latest_by_house: Dict[str, Dict[str, Any]] = {}
    for p in house_polls:
        h = p.get("pollster") or "?"
        cur = latest_by_house.get(h)
        if not cur or p["date"] > cur["date"]:
            latest_by_house[h] = {"date": p["date"], "rows": [p]}
        elif p["date"] == cur["date"]:
            cur["rows"].append(p)
    house_by_party: Dict[str, List[float]] = {}
    for h, obj in latest_by_house.items():
        vals_by_party: Dict[str, List[float]] = {}
        for p in obj["rows"]:
            vals_by_party.setdefault(p["party"], []).append(p["value"])
        for party, vs in vals_by_party.items():
            house_by_party.setdefault(party, []).append(sum(vs) / len(vs))
    house_parties = []
    for party, vals in house_by_party.items():
        house_parties.append({
            "party": party,
            "mean": round(sum(vals) / len(vals), 2),
            "min": round(min(vals), 2),
            "max": round(max(vals), 2),
            "median": round(statistics.median(vals), 2),
            "iqr": round(_iqr(vals), 2),
            "n_houses": len(vals),
        })
    house_parties.sort(key=lambda x: x["mean"], reverse=True)
    _hmap = {h["party"]: h for h in house_parties}
    for _p in parties:
        _h = _hmap.get(_p["party"], {})
        _p["n_houses"] = _h.get("n_houses")
        _p["iqr"] = _h.get("iqr")
    house_mean = {
        "window_days": HOUSE_WINDOW_DAYS,
        "n_houses": len(latest_by_house),
        "parties": house_parties,
    }
    house_latest = []
    for _h, _obj in latest_by_house.items():
        _v: Dict[str, List[float]] = {}
        for _p in _obj["rows"]:
            _v.setdefault(_p["party"], []).append(_p["value"])
        _avg = {k: sum(x) / len(x) for k, x in _v.items()}
        house_latest.append({
            "pollster": _h,
            "date": _obj["date"].strftime("%Y-%m-%d"),
            "pp": round(_avg["PP"], 2) if "PP" in _avg else None,
            "psoe": round(_avg["PSOE"], 2) if "PSOE" in _avg else None,
            "sample": max((p.get("sample") or 0) for p in _obj["rows"]) or None,
            "nota": HOUSE_NOTA.get(_h),
        })
    house_latest.sort(key=lambda r: (r["date"], r["pollster"]), reverse=True)

    _disp = [h["iqr"] for h in house_parties if h["n_houses"] >= 3 and h["mean"] >= 3]
    dispersion = round(sum(_disp) / len(_disp), 2) if _disp else None
    _with_sample = {
        (p["date"].strftime("%Y-%m-%d"), p.get("pollster"))
        for p in recent if (p.get("sample") or 0) >= 200
    }
    sample_pct = round(100 * len(_with_sample) / n_polls) if n_polls else None
    if dispersion is not None and dispersion > 3:
        reasons.append(f"dispersión alta entre casas ({dispersion:.1f} pp)")

    health = {
        "status": status,
        "n_polls": n_polls,
        "n_polls_sin_cis": n_polls_sin_cis,
        "n_pollsters": n_pollsters,
        "pollsters": pollsters,
        "days_since_last": days_since,
        "sample_pct": sample_pct,
        "sample_polls": len(_with_sample),
        "dispersion_iqr": dispersion,
        "reasons": reasons,
    }

    novedades = _novedades(polls_all, now)
    weights = _poll_weights(recent, now, extended)

    election = now.replace(year=2026, month=11, day=29, hour=0, minute=0, second=0, microsecond=0)
    blackout_start = now.replace(year=2026, month=11, day=24, hour=0, minute=0, second=0, microsecond=0)

    return {
        "updated_at": now.strftime("%Y-%m-%d %H:%M %Z"),
        "updated_at_iso": now.isoformat(),
        "in_blackout": False,
        "window_days": WINDOW_DAYS,
        "parties": parties,
        "table_sum": table_sum,
        "series": series,
        "series_long": series_long,
        "poll_dates": poll_dates,
        "n_polls": n_polls,
        "n_polls_sin_cis": n_polls_sin_cis,
        "low_n": n_polls < LOW_N,
        "window_extended": extended,
        "window_span": (
            f"{poll_dates[0]} – {poll_dates[-1]}" if poll_dates else ""
        ),
        "sources": sources,
        "last_poll_date": poll_dates[-1] if poll_dates else None,
        "health": health,
        "novedades": novedades,
        "weights": weights,
        "house_mean": house_mean,
        "house_latest": house_latest,
        "days_to_election": max(0, (election - now).days),
        "days_to_blackout": max(0, (blackout_start - now).days),
        "gap_pp_psoe": round(means.get("PP", 0) - means.get("PSOE", 0), 2),
        "bloc_right": round(sum(means.get(k, 0) for k in ("PP", "VOX")), 2),
        "bloc_left": round(sum(means.get(k, 0) for k in ("PSOE", "SUMAR", "PODEMOS")), 2),
        "weight_basis": (
            "recencia (vida media 10 d); √n cuando la fuente declara muestra"
            if weighted
            else "recencia (vida media 10 d)"
        ),
        "excluded_averages": sorted(
            {p.get("pollster") for p in polls_all if p.get("kind") == "average"}
        ),
    }


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="web/data")
    a = ap.parse_args()
    res = aggregate(a.out)
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "latest.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=2)
    print("agg ok", res["updated_at"], "| n_polls", res.get("n_polls"))
