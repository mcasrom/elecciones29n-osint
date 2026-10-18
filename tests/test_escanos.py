import json
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ESC = os.path.join(ROOT, "data", "escanos_2026.json")
CEN = os.path.join(ROOT, "data", "censo_2026.json")


class EscanosTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = json.load(open(ESC, encoding="utf-8"))
        cls.censo = json.load(open(CEN, encoding="utf-8"))

    def test_total_and_count(self):
        self.assertEqual(self.d["total_escanos"], 350)
        self.assertEqual(len(self.d["provincias"]), 52)
        self.assertEqual(sum(p["escanos"] for p in self.d["provincias"]), 350)

    def test_known_allocations(self):
        by = {p["nombre"]: p for p in self.d["provincias"]}
        self.assertEqual(by["Madrid"]["escanos"], 38)
        self.assertEqual(by["Barcelona"]["escanos"], 32)
        self.assertEqual(by["Teruel"]["escanos"], 3)
        self.assertEqual(by["Soria"]["escanos"], 2)
        self.assertEqual(by["Ceuta"]["escanos"], 1)
        self.assertEqual(by["Melilla"]["escanos"], 1)

    def test_electors_match_census(self):
        self.assertEqual(
            sum(p["electores"] for p in self.d["provincias"]),
            self.censo["total"],
        )

    def test_ratio_extremes(self):
        lo = min(self.d["provincias"], key=lambda p: p["electores_por_escanos"])
        hi = max(self.d["provincias"], key=lambda p: p["electores_por_escanos"])
        self.assertEqual(lo["nombre"], "Teruel")
        self.assertEqual(hi["nombre"], "Madrid")
        self.assertGreater(hi["electores_por_escanos"] / lo["electores_por_escanos"], 3.5)


if __name__ == "__main__":
    unittest.main()
