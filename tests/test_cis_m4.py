import json
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "cis_m4_2026.json")


class CIS_M4Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = json.load(open(DATA, encoding="utf-8"))

    def test_structure(self):
        self.assertEqual(self.d["meta"]["muestra"], 5025)
        self.assertEqual(len(self.d["edad"]["grupos"]), 7)
        self.assertEqual(len(self.d["sexo"]["grupos"]), 2)
        self.assertEqual(len(self.d["ideologia"]["grupos"]), 3)
        for dim in ("edad", "sexo", "ideologia"):
            for g in self.d[dim]["grupos"]:
                self.assertEqual(set(g["partidos"]), {"PP", "PSOE", "VOX", "SUMAR", "Otros"})

    def test_suppression(self):
        for dim in ("edad", "sexo", "ideologia"):
            for g in self.d[dim]["grupos"]:
                for p, v in g["partidos"].items():
                    self.assertEqual(v["suppressed"], v["n"] < 30, (dim, g["nombre"], p, v))

    def test_sums_sex(self):
        for g in self.d["sexo"]["grupos"]:
            s = sum(v["pct"] for v in g["partidos"].values() if not v["suppressed"])
            self.assertAlmostEqual(s, 100.0, delta=0.6)
            self.assertAlmostEqual(sum(v["n"] for v in g["partidos"].values()), g["n_base"], delta=2)

    def test_known_values(self):
        sex = {g["nombre"]: g for g in self.d["sexo"]["grupos"]}
        self.assertGreater(sex["Mujer"]["partidos"]["PSOE"]["pct"], sex["Hombre"]["partidos"]["PSOE"]["pct"])
        age = {g["nombre"]: g for g in self.d["edad"]["grupos"]}
        self.assertGreater(age["De 25 a 34 años"]["partidos"]["PSOE"]["pct"], 30)
        ideo = {g["nombre"]: g for g in self.d["ideologia"]["grupos"]}
        self.assertGreater(ideo["Izquierda (1–4)"]["partidos"]["PSOE"]["pct"], 50)

    def test_csv_exists(self):
        self.assertTrue(os.path.exists(os.path.join(ROOT, "data", "cis_m4_2023.csv")))


if __name__ == "__main__":
    unittest.main()
