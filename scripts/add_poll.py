from __future__ import annotations

import argparse
import csv
import os
from datetime import date

HIST = "data/polls_history.csv"
PARTIES = ["PP", "PSOE", "VOX", "SUMAR", "Podemos", "ERC", "Junts", "Bildu", "PNV", "Cs", "SAF", "Otros"]


def poll_sum(dstr: str) -> float:
    if not os.path.exists(HIST):
        return 0.0
    total = 0.0
    with open(HIST, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            if row.get("date") != dstr:
                continue
            if (row.get("kind") or "tracking") == "average":
                continue
            try:
                total += float(row.get("value") or 0)
            except ValueError:
                continue
    return round(total, 2)


def main() -> int:
    ap = argparse.ArgumentParser(description="Añadir un sondeo a polls_history.csv")
    ap.add_argument("--party", required=True, choices=PARTIES)
    ap.add_argument("--value", required=True, type=float)
    ap.add_argument("--date", default=date.today().isoformat())
    ap.add_argument("--source-url", default="")
    ap.add_argument("--sample", type=int, default=None)
    ap.add_argument("--pollster", default="Manual")
    ap.add_argument("--kind", default="tracking", choices=["tracking", "average"])
    args = ap.parse_args()

    if not (0 <= args.value <= 100):
        ap.error("--value debe estar entre 0 y 100")
    if args.sample is not None and not (200 <= args.sample <= 20000):
        ap.error("--sample debe estar entre 200 y 20000")

    os.makedirs("data", exist_ok=True)
    new = not os.path.exists(HIST)
    with open(HIST, "a", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["party", "date", "value", "source_url", "sample", "pollster", "kind"])
        w.writerow([
            args.party, args.date, args.value, args.source_url,
            args.sample or "", args.pollster, args.kind,
        ])

    total = poll_sum(args.date)
    print(f"OK añadido: {args.party} {args.value}% {args.date} · {args.pollster}/{args.kind}")
    if args.kind != "average":
        print(f"   suma de la fecha {args.date}: {total}%", end="")
        if not (90 <= total <= 110):
            print("  ⚠ fuera de 90–110 %: revisa que no falten partidos")
        else:
            print("  OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
