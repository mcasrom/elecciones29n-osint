import csv
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class Correccion29NTest(unittest.TestCase):
    def test_agregado_fa_retirado(self):
        d = json.loads((ROOT / "data" / "correccion_20261117.json").read_text(encoding="utf-8"))
        self.assertFalse(d["aggregate_visible"]["SUMAR"])

    def test_labels(self):
        d = json.loads((ROOT / "data" / "partidos_display.json").read_text(encoding="utf-8"))
        self.assertEqual(d["SUMAR"]["display_name"], "Frente Amplio")
        self.assertEqual(d["SUMAR"]["historical_display_name"], "Sumar (2023)")
        self.assertFalse(d["SUMAR"]["aggregate_visible"])

    def test_serie_no_comparable(self):
        d = json.loads((ROOT / "data" / "series_breaks.json").read_text(encoding="utf-8"))
        self.assertFalse(d["SUMAR"]["comparable"])
        self.assertEqual(d["SUMAR"]["current_label"], "Frente Amplio")

    def test_auditoria_15(self):
        with (ROOT / "data" / "auditoria_sondeos_20261117.csv").open(encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 15)
        self.assertTrue(all(r["label_original"] == "Frente Amplio" for r in rows))
        self.assertEqual(sum(r["discrepancy"] == "si" for r in rows), 2)


if __name__ == "__main__":
    unittest.main()
