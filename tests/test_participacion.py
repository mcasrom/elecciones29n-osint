import json
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "participacion.json")


class ParticipacionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = json.load(open(DATA, encoding="utf-8"))
        cls.rows = cls.d["elecciones"]

    def test_count_and_range(self):
        self.assertGreaterEqual(len(self.rows), 15)
        for r in self.rows:
            self.assertGreater(r["participacion"], 50)
            self.assertLess(r["participacion"], 90)
            self.assertTrue(r["fuente_url"].startswith("https://www.juntaelectoralcentral.es/"))

    def test_2023(self):
        last = self.rows[-1]
        self.assertEqual(last["eleccion"], "2023")
        self.assertAlmostEqual(last["participacion"], 66.59, places=2)

    def test_extremes(self):
        self.assertAlmostEqual(max(r["participacion"] for r in self.rows), 79.97, places=2)
        self.assertAlmostEqual(min(r["participacion"] for r in self.rows), 66.23, places=2)

    def test_no_2026(self):
        self.assertFalse(any(r["year"] == 2026 for r in self.rows))


if __name__ == "__main__":
    unittest.main()
