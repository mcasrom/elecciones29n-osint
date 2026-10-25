import os
import tempfile
import unittest
from datetime import datetime

import pytz

from agg import aggregate as agg

TZ = pytz.timezone("Europe/Madrid")
HEADER = "party,date,value,source_url,sample,pollster,kind\n"


class RobustezTest(unittest.TestCase):
    def run_with(self, rows):
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
            return agg.aggregate()
        finally:
            os.chdir(old)
            tmp.cleanup()

    def test_sample_pct_and_iqr(self):
        today = datetime.now(TZ).strftime("%Y-%m-%d")
        rows = []
        for house, pp, ps in (("A", 30, 26), ("B", 32, 28), ("C", 31, 27)):
            rows.append(("PP", today, pp, "u", 1000, house, "tracking"))
            rows.append(("PSOE", today, ps, "u", 1000, house, "tracking"))
        res = self.run_with(rows)
        self.assertEqual(res["health"]["sample_pct"], 100)
        self.assertIsNotNone(res["health"]["dispersion_iqr"])
        pp = next(p for p in res["parties"] if p["party"] == "PP")
        self.assertEqual(pp["n_houses"], 3)
        self.assertGreater(pp["iqr"], 0)
        w = res["weights"]
        self.assertGreaterEqual(w["effective_sources"], 1)
        self.assertGreaterEqual(w["effective_houses"], 1)
        self.assertLessEqual(w["effective_sources"], len(w["sources"]) + 0.05)
        self.assertLessEqual(w["effective_houses"], len(w["houses"]) + 0.05)
        self.assertIn("sensitivity", res)

    def test_sample_pct_with_missing(self):
        today = datetime.now(TZ).strftime("%Y-%m-%d")
        res = self.run_with([
            ("PP", today, 30, "u", 1000, "A", "tracking"),
            ("PP", today, 31, "u", "", "B", "tracking"),
        ])
        self.assertEqual(res["health"]["sample_pct"], 50)
        self.assertEqual(res["health"]["sample_polls"], 1)

    def test_house_latest_nota_cis(self):
        today = datetime.now(TZ).strftime("%Y-%m-%d")
        res = self.run_with([
            ("PP", today, 22.2, "u", 5025, "CIS", "tracking"),
            ("PSOE", today, 34.0, "u", 5025, "CIS", "tracking"),
            ("PP", today, 31.0, "u", 1000, "A", "tracking"),
        ])
        row = next(r for r in res["house_latest"] if r["pollster"] == "CIS")
        self.assertEqual(row["nota"], "estimación de voto")
        self.assertEqual(row["pp"], 22.2)
        self.assertEqual(row["sample"], 5025)
        self.assertIsNone(next(r for r in res["house_latest"] if r["pollster"] == "A")["nota"])

    def test_house_latest_enlaza_pieza(self):
        today = datetime.now(TZ).strftime("%Y-%m-%d")
        url = "https://electomania.es/electopanel-18-oct/"
        res = self.run_with([
            ("PP", today, 31.8, url, 3141, "ElectoPanel", "tracking"),
            ("PSOE", today, 27.1, url, 3141, "ElectoPanel", "tracking"),
        ])
        row = next(r for r in res["house_latest"] if r["pollster"] == "ElectoPanel")
        self.assertEqual(row["url"], url)


if __name__ == "__main__":
    unittest.main()
