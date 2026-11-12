import json
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Cis3584Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(os.path.join(ROOT, "data", "cis_3584_2026.json"), encoding="utf-8") as f:
            cls.d = json.load(f)

    def test_identidad_y_muestra(self):
        self.assertEqual(self.d["study"], "3584")
        self.assertEqual(self.d["sample"], 45074)
        self.assertEqual(self.d["sample_designed"], 45000)
        self.assertEqual(self.d["fieldwork_start"], "2026-10-07")
        self.assertEqual(self.d["fieldwork_end"], "2026-10-30")

    def test_estimaciones_principales(self):
        rows = {r["party"]: r for r in self.d["vote_estimate"]}
        self.assertEqual(rows["PSOE"]["pct"], 33.3)
        self.assertEqual(rows["PP"]["pct"], 25.5)
        self.assertEqual(rows["VOX"]["pct"], 18.4)
        self.assertEqual(rows["Frente Amplio"]["pct"], 4.7)
        self.assertEqual(rows["ERC-Podemos"]["pct"], 3.1)

    def test_escanos_clave(self):
        rows = {r["party"]: r for r in self.d["vote_estimate"]}
        self.assertEqual((rows["PSOE"]["seats_min"], rows["PSOE"]["seats_max"]), (134, 143))
        self.assertEqual((rows["PP"]["seats_min"], rows["PP"]["seats_max"]), (98, 106))
        self.assertEqual((rows["VOX"]["seats_min"], rows["VOX"]["seats_max"]), (57, 65))
        self.assertEqual(self.d["pp_vox_max"], 171)
        self.assertEqual(self.d["majority"], 176)


if __name__ == "__main__":
    unittest.main()
