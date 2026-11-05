import json
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CON = os.path.join(ROOT, "data", "congreso.json")


class GobernabilidadTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(CON, encoding="utf-8") as f:
            cls.congreso = json.load(f)
        from gen import build
        cls.g = build.build_gobernabilidad(cls.congreso)

    def test_total_and_threshold(self):
        self.assertEqual(self.g["total"], 350)
        self.assertEqual(self.g["threshold"], 176)
        self.assertEqual(sum(p["seats"] for p in self.g["parties"]), 350)

    def test_territorial_weight(self):
        self.assertEqual(self.g["territorial_seats"], 28)
        territorial = {p["party"] for p in self.g["parties"] if p["territorial"]}
        self.assertEqual(territorial, {"ERC", "Junts", "EH Bildu", "PNV", "CCa", "BNG", "UPN"})

    def test_known_scenarios(self):
        by = {s["label"]: s["seats"] for s in self.g["scenarios"]}
        self.assertEqual(by["PP + VOX"], 170)
        self.assertEqual(by["PSOE + Sumar"], 152)
        self.assertEqual(by["PSOE + Sumar + ERC + Junts"], 166)
        self.assertEqual(by["PSOE + Sumar + ERC + Junts + PNV"], 171)
        self.assertEqual(by["PSOE + Sumar + ERC + Junts + PNV + EH Bildu"], 177)
        self.assertEqual(by["PP + VOX + PNV"], 175)


if __name__ == "__main__":
    unittest.main()
