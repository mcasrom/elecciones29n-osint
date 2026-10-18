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


def _weight(p: Dict[str, Any], now: datetime) -> float:
    age_days = max(0.0, (now - p["date"]).total_seconds() / 86400.0)
    recency = 0.5 ** (age_days / HALF_LIFE_DAYS)
    sample = p.get("sample")
    if sample:
        return math.sqrt(sample / 1000.0) * recency
    return recency


def _series(polls: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    out: Dict[str, List[Dict[str, Any]]] = {}
    for p in polls:
        out.setdefault(p["party"], []).append(
            {"date": p["date"].strftime("%Y-%m-%d"), "value": p["value"]}
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
    }


def aggregate(out_dir: str = "web/data") -> Dict[str, Any]:
    now = datetime.now(TZ)
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

    cutoff = now - timedelta(days=WINDOW_DAYS)
    recent = [p for p in tracking if p["date"] >= cutoff]

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
        parties.append(
            {
                "party": party,
                "mean": round(mean, 2),
                "median": round(statistics.median(vals), 2),
                "min": round(min(vals), 2),
                "max": round(max(vals), 2),
                "n": len(vals),
                "sample_total": sum((r.get("sample") or 0) for r in rows),
                "pollsters": sorted({r.get("pollster") for r in rows if r.get("pollster")}),
            }
        )
    parties.sort(key=lambda x: x["mean"], reverse=True)

    long_cutoff = now - timedelta(days=LONG_DAYS)
    series_long = _series([p for p in tracking if p["date"] >= long_cutoff])
    series = _series(recent)

    poll_dates = sorted({p["date"].strftime("%Y-%m-%d") for p in recent})
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
    if len(poll_dates) < LOW_N:
        status = "bad"
        reasons.append(f"solo {len(poll_dates)} sondeos en la media")
    if n_pollsters <= 1:
        status = "bad" if status == "bad" else "warn"
        reasons.append("una sola encuestadora")
    if days_since is not None and days_since > 10:
        status = "bad" if days_since > 21 else ("warn" if status == "ok" else status)
        reasons.append(f"último sondeo hace {days_since} días")
    health = {
        "status": status,
        "n_polls": len(poll_dates),
        "n_pollsters": n_pollsters,
        "pollsters": pollsters,
        "days_since_last": days_since,
        "reasons": reasons,
    }

    election = now.replace(year=2026, month=11, day=29, hour=0, minute=0, second=0, microsecond=0)
    blackout_start = now.replace(year=2026, month=11, day=24, hour=0, minute=0, second=0, microsecond=0)

    return {
        "updated_at": now.strftime("%Y-%m-%d %H:%M %Z"),
        "updated_at_iso": now.isoformat(),
        "in_blackout": False,
        "window_days": WINDOW_DAYS,
        "parties": parties,
        "series": series,
        "series_long": series_long,
        "poll_dates": poll_dates,
        "n_polls": len(poll_dates),
        "low_n": len(poll_dates) < LOW_N,
        "window_extended": extended,
        "window_span": (
            f"{poll_dates[0]} – {poll_dates[-1]}" if poll_dates else ""
        ),
        "sources": sources,
        "last_poll_date": poll_dates[-1] if poll_dates else None,
        "health": health,
        "days_to_election": max(0, (election - now).days),
        "days_to_blackout": max(0, (blackout_start - now).days),
        "gap_pp_psoe": round(means.get("PP", 0) - means.get("PSOE", 0), 2),
        "bloc_right": round(sum(means.get(k, 0) for k in ("PP", "VOX")), 2),
        "bloc_left": round(sum(means.get(k, 0) for k in ("PSOE", "SUMAR", "PODEMOS")), 2),
        "weight_basis": (
            "muestra (√n) + recencia (vida media 10 d)"
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
