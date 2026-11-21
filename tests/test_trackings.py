import csv, json, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent

class TrackingRegistryTest(unittest.TestCase):
    def test_registry_exists_and_is_separate(self):
        with (ROOT / "data" / "trackings_registry.csv").open(encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 4)
        self.assertEqual(sum(r["status"] == "verificado" for r in rows), 1)
        self.assertEqual(sum(r["status"] == "sin_ficha" for r in rows), 3)
        latest = json.loads((ROOT / "web" / "data" / "latest.json").read_text(encoding="utf-8"))
        self.assertEqual(latest["tracking_registry_n"], 4)
        self.assertEqual(latest["tracking_no_ficha"], 3)
        self.assertGreater(latest["n_polls"], 0)

if __name__ == "__main__":
    unittest.main()
