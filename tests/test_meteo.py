import json
import os
import unittest

from gen.build import build_meteo_rows

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "meteo_electoral.json")


class MeteoTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = json.load(open(DATA, encoding="utf-8"))

    def test_years(self):
        self.assertEqual(len(self.d["elecciones"]), 16)
        self.assertEqual(len(self.d["elecciones"]["2023-07-23"]["provincias"]), 52)

    def test_national_rows(self):
        rows = build_meteo_rows(self.d)
        self.assertEqual(len(rows), 16)
        r = next(x for x in rows if x["fecha"] == "2023-07-23")
        self.assertGreater(r["n_estaciones"], 700)
        self.assertGreaterEqual(r["prec_media"], 0)
        self.assertGreaterEqual(r["lluvia_pct"], 0)
        self.assertLessEqual(r["lluvia_pct"], 100)
        self.assertGreater(r["tmax_media"], 0)

    def test_early_low_coverage(self):
        rows = {x["fecha"]: x for x in build_meteo_rows(self.d)}
        self.assertLess(rows["1982-10-28"]["n_estaciones"], rows["2023-07-23"]["n_estaciones"])


if __name__ == "__main__":
    unittest.main()
