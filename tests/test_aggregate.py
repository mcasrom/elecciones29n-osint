import os
import tempfile
import unittest
from datetime import datetime, timedelta

import pytz

from agg import aggregate as agg

TZ = pytz.timezone("Europe/Madrid")
HEADER = "party,date,value,source_url,sample,pollster,kind\n"


class AggregateTest(unittest.TestCase):
    def run_with(self, rows, now=None):
        tmp = tempfile.TemporaryDirectory()
        old = os.getcwd()
        try:
            os.chdir(tmp.name)
            os.makedirs("data", exist_ok=True)
            os.makedirs("web/data", exist_ok=True)
            with open("data/polls_history.csv", "w", encoding="utf-8") as f:
                f.write(HEADER)
                for r in rows:
                    f.write(",".join(str(x) for x in r) + "\n")
            return agg.aggregate(now=now)
        finally:
            os.chdir(old)
            tmp.cleanup()

    def test_window_is_date_based_and_stable_within_day(self):
        rows = [
            ("X", "2026-10-09", 10.0, "u", 1000, "A", "tracking"),
            ("X", "2026-10-10", 20.0, "u", 1000, "B", "tracking"),
            ("X", "2026-10-11", 30.0, "u", 1000, "C", "tracking"),
            ("X", "2026-10-12", 40.0, "u", 1000, "D", "tracking"),
            ("X", "2026-10-13", 50.0, "u", 1000, "E", "tracking"),
            ("X", "2026-10-18", 60.0, "u", 1000, "F", "tracking"),
        ]
        at8 = self.run_with(rows, now=datetime(2026, 10, 23, 8, 0, tzinfo=TZ))
        at23 = self.run_with(rows, now=datetime(2026, 10, 23, 23, 0, tzinfo=TZ))
        # La ventana son 14 días naturales contando hoy: 10..23, no 9..23.
        self.assertEqual(at8["n_polls"], 5)
        self.assertEqual(at8["n_polls"], at23["n_polls"])
        self.assertEqual(
            [(p["party"], p["mean"]) for p in at8["parties"]],
            [(p["party"], p["mean"]) for p in at23["parties"]],
        )
        # El 9-oct sale al cambiar el día, no a las 08:00 del build.
        at22 = self.run_with(rows, now=datetime(2026, 10, 22, 23, 0, tzinfo=TZ))
        self.assertEqual(at22["n_polls"], 6)
        self.assertTrue(at22["window_span"].startswith("2026-10-09"))

    def test_table_sum_excludes_territorial_and_counts_houses(self):
        rows = [
            ("PP", "2026-10-20", 30.0, "u", 1000, "A", "tracking"),
            ("PSOE", "2026-10-20", 28.0, "u", 1000, "A", "tracking"),
            ("VOX", "2026-10-20", 18.0, "u", 1000, "A", "tracking"),
            ("SUMAR", "2026-10-20", 7.0, "u", 1000, "A", "tracking"),
            ("PODEMOS", "2026-10-20", 3.0, "u", 1000, "A", "tracking"),
            ("SAF", "2026-10-20", 2.0, "u", 1000, "A", "tracking"),
            ("Otros", "2026-10-20", 10.0, "u", None, "A", "tracking"),
            ("ERC", "2026-10-20", 2.0, "u", 1000, "A", "tracking"),
        ]
        res = self.run_with(rows, now=datetime(2026, 10, 23, 8, 0, tzinfo=TZ))
        self.assertEqual(res["table_sum"], 98.0)
        erc = next(p for p in res["parties"] if p["party"] == "ERC")
        self.assertTrue(erc["territorial"])
        self.assertEqual(erc["n_houses_recent"], 1)
        self.assertEqual(erc["n_houses_window"], 1)
        pp = next(p for p in res["parties"] if p["party"] == "PP")
        self.assertEqual(pp["sample_n"], 1)
        self.assertEqual(pp["n_houses_recent"], 1)

    def test_weighting_favours_big_sample(self):
        today = datetime.now(TZ).strftime("%Y-%m-%d")
        res = self.run_with([
            ("X", today, 10.0, "u", 5000, "A", "tracking"),
            ("X", today, 20.0, "u", 500, "B", "tracking"),
        ])
        p = next(p for p in res["parties"] if p["party"] == "X")
        self.assertLess(p["mean"], 15.0)

    def test_median_and_range(self):
        today = datetime.now(TZ).strftime("%Y-%m-%d")
        res = self.run_with([
            ("X", today, 10.0, "u", 1000, "A", "tracking"),
            ("X", today, 20.0, "u", 1000, "B", "tracking"),
            ("X", today, 60.0, "u", 1000, "C", "tracking"),
        ])
        p = next(p for p in res["parties"] if p["party"] == "X")
        self.assertEqual(p["median"], 20.0)
        self.assertEqual(p["min"], 10.0)
        self.assertEqual(p["max"], 60.0)

    def test_average_kind_excluded(self):
        today = datetime.now(TZ).strftime("%Y-%m-%d")
        res = self.run_with([
            ("X", today, 10.0, "u", 1000, "Panel", "tracking"),
            ("X", today, 30.0, "u", None, "Promedio", "average"),
        ])
        p = next(p for p in res["parties"] if p["party"] == "X")
        self.assertEqual(p["n"], 1)
        self.assertEqual(p["mean"], 10.0)
        self.assertIn("Promedio", res["excluded_averages"])

    def test_extension_to_four_polls(self):
        rows = []
        for i, d in enumerate(["2026-08-20", "2026-09-01", "2026-09-15", "2026-10-01", "2026-10-10"]):
            rows.append(("X", d, 10.0 + i, "u", 1000, "A", "tracking"))
        res = self.run_with(rows)
        self.assertGreaterEqual(res["n_polls"], 4)

    def test_health_ok_two_pollsters(self):
        now = datetime.now(TZ)
        rows = []
        for i in range(4):
            d = (now - timedelta(days=i)).strftime("%Y-%m-%d")
            rows.append(("X", d, 10.0 + i, "u", 1000, "A" if i % 2 == 0 else "B", "tracking"))
        res = self.run_with(rows)
        self.assertEqual(res["health"]["status"], "ok")
        self.assertEqual(res["health"]["n_pollsters"], 2)

    def test_health_single_pollster_warn(self):
        now = datetime.now(TZ)
        rows = []
        for i in range(4):
            d = (now - timedelta(days=i)).strftime("%Y-%m-%d")
            rows.append(("X", d, 10.0, "u", 1000, "A", "tracking"))
        res = self.run_with(rows)
        self.assertEqual(res["health"]["status"], "warn")
        self.assertIn("una sola encuestadora", res["health"]["reasons"])

    def test_health_low_bad(self):
        today = datetime.now(TZ).strftime("%Y-%m-%d")
        res = self.run_with([("X", today, 10.0, "u", 1000, "A", "tracking")])
        self.assertEqual(res["health"]["status"], "bad")
        self.assertEqual(res["health"]["n_polls"], 1)

    def test_house_mean_equal_weight(self):
        now = datetime.now(TZ)
        rows = [
            ("X", (now - timedelta(days=30)).strftime("%Y-%m-%d"), 10.0, "u", 1000, "A", "tracking"),
            ("X", (now - timedelta(days=10)).strftime("%Y-%m-%d"), 20.0, "u", 1000, "A", "tracking"),
            ("X", (now - timedelta(days=5)).strftime("%Y-%m-%d"), 30.0, "u", 1000, "B", "tracking"),
        ]
        res = self.run_with(rows)
        house = next(p for p in res["house_mean"]["parties"] if p["party"] == "X")
        self.assertEqual(house["mean"], 25.0)
        self.assertEqual(house["n_houses"], 2)

    def test_party_names_canonical(self):
        today = datetime.now(TZ).strftime("%Y-%m-%d")
        res = self.run_with([
            ("Podemos", today, 3.0, "u", 1000, "A", "tracking"),
            ("PODEMOS", today, 4.0, "u", 1000, "B", "tracking"),
        ])
        names = [p["party"] for p in res["parties"]]
        self.assertEqual(names.count("PODEMOS"), 1)
        p = next(x for x in res["parties"] if x["party"] == "PODEMOS")
        self.assertEqual(p["n"], 2)

    def test_weight_basis_reports_sample(self):
        today = datetime.now(TZ).strftime("%Y-%m-%d")
        res = self.run_with([("X", today, 10.0, "u", 1000, "A", "tracking")])
        self.assertIn("muestra", res["weight_basis"])

    def test_poll_weights_share_by_house_and_poll(self):
        today = datetime.now(TZ).strftime("%Y-%m-%d")
        res = self.run_with([
            ("X", today, 10.0, "u", 5000, "A", "tracking"),
            ("X", today, 20.0, "u", None, "B", "tracking"),
        ])
        w = res["weights"]
        self.assertEqual(w["total_polls"], 2)
        self.assertEqual(w["top_house"], "A")
        self.assertAlmostEqual(sum(h["share_pct"] for h in w["houses"]), 100.0, places=0)
        self.assertAlmostEqual(sum(x["share_pct"] for x in w["polls"]), 100.0, places=0)
        house = next(h for h in w["houses"] if h["pollster"] == "A")
        self.assertGreater(house["share_pct"], 50)
        self.assertEqual(house["n_polls"], 1)
        self.assertIsNone(w["houses"][-1]["sample"])

    def test_poll_weights_source_grouping(self):
        today = datetime.now(TZ).strftime("%Y-%m-%d")
        res = self.run_with([
            ("X", today, 10.0, "https://www.ondacero.es/x", None, "Sigma Dos", "tracking"),
            ("X", today, 20.0, "https://electomania.es/x", 1000, "ElectoPanel", "tracking"),
            ("X", today, 30.0, "https://www.cis.es/x", 4000, "CIS", "tracking"),
        ])
        w = res["weights"]
        srcs = {s["source"]: s for s in w["sources"]}
        self.assertEqual(set(srcs), {"Onda Cero", "Electomanía", "CIS"})
        self.assertEqual(srcs["CIS"]["n_houses"], 1)
        self.assertAlmostEqual(sum(s["share_pct"] for s in w["sources"]), 100.0, places=0)

    def test_poll_weights_equal_without_sample(self):
        today = datetime.now(TZ).strftime("%Y-%m-%d")
        res = self.run_with([
            ("X", today, 10.0, "u", None, "A", "tracking"),
            ("X", today, 20.0, "u", None, "B", "tracking"),
        ])
        shares = [h["share_pct"] for h in res["weights"]["houses"]]
        self.assertEqual(shares, [50.0, 50.0])


class SampleParseTest(unittest.TestCase):
    def test_parse_sample(self):
        from ingest.electomania import parse_sample
        self.assertEqual(parse_sample("Tamaño muestral: 3.141 cuestionarios"), 3141)
        self.assertEqual(parse_sample("La oleada se levantó con 8.171 cuestionarios"), 8171)
        self.assertIsNone(parse_sample("sin datos"))

    def test_pollster_kind(self):
        from ingest.electomania import pollster_of
        self.assertEqual(pollster_of("ElectoPanel (11 oct)"), ("ElectoPanel", "tracking"))
        self.assertEqual(pollster_of("ElectoPromedio cierre"), ("ElectoPromedio", "average"))


if __name__ == "__main__":
    unittest.main()
