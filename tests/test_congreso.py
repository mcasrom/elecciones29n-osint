import json
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CON = os.path.join(ROOT, "data", "congreso.json")
PP = os.path.join(ROOT, "data", "participacion_provincial.json")


class CongresoTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = json.load(open(CON, encoding="utf-8"))
        cls.p = json.load(open(PP, encoding="utf-8"))
        cls.e23 = cls.d["elecciones"]["2023-07-23"]

    def test_elections(self):
        self.assertGreaterEqual(len(self.d["elecciones"]), 16)
        self.assertEqual(len(self.e23["provincias"]), 52)

    def test_2023_seats(self):
        n = self.e23["nacional"]
        self.assertEqual(sum(n["escanos"].values()), 350)
        self.assertEqual(n["escanos"]["PP"], 137)
        self.assertEqual(n["escanos"]["PSOE"], 121)
        self.assertEqual(n["escanos"]["VOX"], 33)
        self.assertEqual(n["escanos"]["SUMAR"], 31)

    def test_2023_participation(self):
        n = self.e23["nacional"]
        self.assertAlmostEqual(n["participacion"], 66.59, places=2)
        self.assertEqual(
            sum(p["electores"] for p in self.e23["provincias"]), n["electores"]
        )
        self.assertEqual(
            sum(p["votantes"] for p in self.e23["provincias"]), n["votantes"]
        )

    def test_madrid(self):
        m = next(p for p in self.e23["provincias"] if p["nombre"] == "Madrid")
        self.assertEqual(sum(m["escanos"].values()), 37)

    def test_gallagher(self):
        g = self.e23["nacional"]["gallagher"]
        self.assertGreater(g, 4)
        self.assertLess(g, 8)

    def test_provincial_json(self):
        self.assertEqual(len(self.p["elecciones"]), len(self.d["elecciones"]))
        e = self.p["elecciones"]["2023-07-23"]
        self.assertEqual(len(e["provincias"]), 52)
        self.assertAlmostEqual(e["nacional"]["participacion"], 66.59, places=2)


if __name__ == "__main__":
    unittest.main()
