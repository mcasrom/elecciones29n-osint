from __future__ import annotations

import argparse
import csv
import os
from datetime import date


HIST = "data/polls_history.csv"
PARTIES = ["PP","PSOE","VOX","SUMAR","Podemos","ERC","Junts","Bildu","PNV","Cs","Otros"]


def main():
    ap = argparse.ArgumentParser(description="Añadir un sondeo a polls_history.csv")
    ap.add_argument("--party", required=True, choices=PARTIES)
    ap.add_argument("--value", required=True, type=float)
    ap.add_argument("--date", default=date.today().isoformat())
    ap.add_argument("--source-url", default="https://electomania.es/")
    ap.add_argument("--sample", type=int, default=None)
    args = ap.parse_args()

    os.makedirs("data", exist_ok=True)
    new = not os.path.exists(HIST)
    with open(HIST, "a", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["party","date","value","source_url","sample"])
        w.writerow([args.party, args.date, args.value, args.source_url, args.sample or ""])

    print(f"OK añadido: {args.party} {args.value}% {args.date}")


if __name__ == "__main__":
    main()
