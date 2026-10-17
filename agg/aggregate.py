from __future__ import annotations

import json
import os
from datetime import datetime
from typing import List, Dict, Any

import pytz

from agg import blackout

TZ = pytz.timezone("Europe/Madrid")
WINDOW_DAYS = 14


def load_polls() -> List[Dict[str, Any]]:
    # Leer polls_history.csv si existe
    hist = "data/polls_history.csv"
    if not os.path.exists(hist):
        return []
    polls = []
    with open(hist, encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i == 0:
                continue
            line = line.strip()
            if not line:
                continue
            # formato: party,date,value,source_url,sample
            parts = line.split(",")
            if len(parts) < 4:
                continue
            party, dstr, vstr, src = parts[0], parts[1], parts[2], parts[3]
            dt = _parse_date(dstr)
            try:
                val = float(vstr.replace("%", "").strip())
            except Exception:
                continue
            if dt is None or not (0 <= val <= 100):
                continue
            polls.append(
                {
                    "party": party.strip(),
                    "date": dt,
                    "value": val,
                    "source_url": src.strip(),
                }
            )
    return polls


def _parse_date(s: str) -> datetime | None:
    from datetime import datetime

    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            dt = datetime.strptime(s, fmt)
            return TZ.localize(dt)
        except Exception:
            continue
    return None


def aggregate() -> Dict[str, Any]:
    now = datetime.now(TZ)
    if blackout.is_blackout(now):
        # Mantener último válido si existe
        latest_path = "web/data/latest.json"
        if os.path.exists(latest_path):
            with open(latest_path, encoding="utf-8") as f:
                return json.load(f)
        return {
            "updated_at": now.strftime("%Y-%m-%d %H:%M %Z"),
            "in_blackout": True,
            "blackout_reason": blackout.blackout_reason(),
            "parties": [],
        }

    polls = load_polls()
    if not polls:
        latest_path = "web/data/latest.json"
        if os.path.exists(latest_path):
            with open(latest_path, encoding="utf-8") as f:
                return json.load(f)
        return {
            "updated_at": now.strftime("%Y-%m-%d %H:%M %Z"),
            "in_blackout": False,
            "parties": [],
        }

    cutoff = now - __import__("datetime").timedelta(days=WINDOW_DAYS)
    recent = [p for p in polls if p["date"] >= cutoff]

    # Agregar por partido: media móvil ponderada simple + min/max
    by_party: Dict[str, List[float]] = {}
    for p in recent:
        by_party.setdefault(p["party"], []).append(p["value"])

    parties = []
    for party, vals in by_party.items():
        if not vals:
            continue
        m = sum(vals) / len(vals)
        parties.append(
            {
                "party": party,
                "mean": round(m, 2),
                "min": round(min(vals), 2),
                "max": round(max(vals), 2),
                "n": len(vals),
            }
        )
    parties.sort(key=lambda x: x["mean"], reverse=True)

    return {
        "updated_at": now.strftime("%Y-%m-%d %H:%M %Z"),
        "in_blackout": False,
        "window_days": WINDOW_DAYS,
        "parties": parties,
        "aggr": {"window_days": WINDOW_DAYS, "min_max_shown": True},
    }


if __name__ == "__main__":
    res = aggregate()
    os.makedirs("web/data", exist_ok=True)
    with open("web/data/latest.json", "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=2)
    print("agg ok", res["updated_at"])
