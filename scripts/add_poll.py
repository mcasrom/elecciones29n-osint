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


def parse_values(raw: str) -> dict[str, float]:
    out: dict[str, float] = {}
    for part in raw.replace(";", ",").split(","):
        part = part.strip()
        if not part:
            continue
        if "=" not in part:
            raise SystemExit(f"formato inválido: {part!r} (usa PARTIDO=valor)")
        k, v = part.split("=", 1)
        k = k.strip()
        if k not in PARTIES:
            raise SystemExit(f"partido desconocido: {k} (válidos: {', '.join(PARTIES)})")
        try:
            val = float(v.strip().replace(",", "."))
        except ValueError:
            raise SystemExit(f"valor no numérico: {part!r}")
        if not (0 <= val <= 100):
            raise SystemExit(f"valor fuera de 0–100: {part!r}")
        out[k] = val
    if not out:
        raise SystemExit("no hay valores")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Añadir uno o varios sondeos a polls_history.csv")
    ap.add_argument("--party", choices=PARTIES, help="modo simple: partido")
    ap.add_argument("--value", type=float, help="modo simple: valor")
    ap.add_argument("--values", help="modo lote: 'PP=31.5,PSOE=26.9,...'")
    ap.add_argument("--date", default=date.today().isoformat())
    ap.add_argument("--source-url", default="")
    ap.add_argument("--sample", type=int, default=None)
    ap.add_argument("--pollster", default="Manual")
    ap.add_argument("--kind", default="tracking", choices=["tracking", "average"])
    args = ap.parse_args()

    if args.values:
        if args.party or args.value is not None:
            ap.error("usa --values O --party/--value, no ambos")
        values = parse_values(args.values)
    else:
        if not args.party or args.value is None:
            ap.error("indica --party y --value, o --values")
        if not (0 <= args.value <= 100):
            ap.error("--value debe estar entre 0 y 100")
        values = {args.party: args.value}

    if args.sample is not None and not (200 <= args.sample <= 20000):
        ap.error("--sample debe estar entre 200 y 20000")

    os.makedirs("data", exist_ok=True)
    new = not os.path.exists(HIST)
    with open(HIST, "a", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["party", "date", "value", "source_url", "sample", "pollster", "kind"])
        for party, val in values.items():
            w.writerow([party, args.date, val, args.source_url, args.sample or "", args.pollster, args.kind])

    total = poll_sum(args.date)
    print(f"OK añadido: {len(values)} partidos · {args.date} · {args.pollster}/{args.kind}")
    if args.kind != "average":
        print(f"   suma de la fecha {args.date}: {total}%", end="")
        if not (90 <= total <= 110):
            print("  ⚠ fuera de 90–110 %: revisa que no falten partidos")
        else:
            print("  OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
