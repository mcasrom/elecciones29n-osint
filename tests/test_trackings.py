import csv, json, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent

class TrackingRegistryTest(unittest.TestCase):
    def test_registry_exists_and_is_separate(self):
        with (ROOT / "data" / "trackings_registry.csv").open(encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        self.assertGreaterEqual(len(rows), 4)
        self.assertGreaterEqual(sum(r["status"] == "verificado" for r in rows), 1)
        self.assertEqual(sum(r["status"] == "sin_ficha" for r in rows), len(rows) - 1)
        latest = json.loads((ROOT / "web" / "data" / "latest.json").read_text(encoding="utf-8"))
        self.assertEqual(latest["tracking_registry_n"], len(rows))
        self.assertEqual(latest["tracking_no_ficha"], sum(r["status"] == "sin_ficha" for r in rows))
        self.assertGreater(latest["n_polls"], 0)

if __name__ == "__main__":
    unittest.main()
