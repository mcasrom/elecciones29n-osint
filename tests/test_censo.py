import json
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "censo_2026.json")


class CensusTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = json.load(open(DATA, encoding="utf-8"))

    def test_totals(self):
        self.assertEqual(self.d["total"], 38_728_356)
        self.assertEqual(self.d["cer"], 35_958_711)
        self.assertEqual(self.d["cera"], 2_769_645)
        self.assertEqual(self.d["cer"] + self.d["cera"], self.d["total"])

    def test_provinces_sum(self):
        self.assertEqual(len(self.d["provincias"]), 52)
        self.assertEqual(sum(p["total"] for p in self.d["provincias"]), self.d["total"])
        self.assertEqual(sum(p["cer"] for p in self.d["provincias"]), self.d["cer"])
        self.assertEqual(sum(p["cera"] for p in self.d["provincias"]), self.d["cera"])

    def test_ccaa_sum(self):
        self.assertEqual(len(self.d["ccaa"]), 19)
        self.assertEqual(sum(c["total"] for c in self.d["ccaa"]), self.d["total"])

    def test_age_sex_sum(self):
        self.assertEqual(len(self.d["edad_sexo"]), 15)
        self.assertEqual(sum(e["total"] for e in self.d["edad_sexo"]), self.d["cer"])
        self.assertEqual(
            sum(e["mujeres"] for e in self.d["edad_sexo"])
            + sum(e["hombres"] for e in self.d["edad_sexo"]),
            self.d["cer"],
        )

    def test_new_voters(self):
        self.assertEqual(self.d["nuevos_desde_2023"], 1_615_127)
        self.assertEqual(
            sum(n["desde_2023"] for n in self.d["nuevos_provincia"]),
            self.d["nuevos_desde_2023"],
        )


if __name__ == "__main__":
    unittest.main()
