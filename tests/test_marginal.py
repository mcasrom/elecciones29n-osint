import unittest

from agg.dhondt import marginal, reparto


class DhondtTest(unittest.TestCase):
    def test_reparto_simple(self):
        self.assertEqual(reparto({"A": 100, "B": 80, "C": 30}, 3, 210), {"A": 2, "B": 1, "C": 0})

    def test_umbral(self):
        r = reparto([("A", 100), ("B", 80), ("C", 30), ("D", 6)], 3, 216)
        self.assertEqual(r["D"], 0)
        self.assertEqual(r["A"], 2)
        self.assertEqual(r["B"], 1)

    def test_un_escanos(self):
        self.assertEqual(reparto({"A": 100, "B": 80}, 1, 180), {"A": 1, "B": 0})

    def test_marginal(self):
        m = marginal({"A": 100, "B": 60, "C": 20}, 2, 180)
        self.assertEqual(m["ultimo"]["etiqueta"], "B")
        self.assertEqual(m["siguiente"]["etiqueta"], "C")
        self.assertEqual(m["siguiente"]["escanos"], 0)
        self.assertEqual(m["margen_votos"], 41)

    def test_marginal_no_confunde_ganador_con_primera_fuera(self):
        m = marginal({"A": 100, "B": 60, "C": 20}, 2, 180)
        self.assertNotEqual(m["siguiente"]["etiqueta"], m["ultimo"]["etiqueta"])
        self.assertGreater(m["siguiente"]["votos"], 0)
        self.assertIsNotNone(m["margen_pct"])

    def test_marginal_sin_siguiente(self):
        m = marginal({"A": 100}, 2, 100)
        self.assertIsNone(m["siguiente"])
        self.assertIsNone(m["margen_votos"])

    def test_validos_invalidos(self):
        with self.assertRaises(ValueError):
            reparto({"A": 1}, 1, 0)


if __name__ == "__main__":
    unittest.main()
