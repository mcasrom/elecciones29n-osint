import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from ingest.cis_lideres import extract  # noqa: E402


class TestCisLideres(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = extract(ROOT / "data/raw/cis_3582_multi.xlsx")

    def test_four_leaders_and_scale(self):
        self.assertEqual(self.data["meta"]["scale"], "1-10")
        self.assertEqual(len(self.data["leaders"]), 4)

    def test_means(self):
        got = {x["name"]: x["mean"] for x in self.data["leaders"]}
        self.assertEqual(got["Pedro Sánchez"], 4.42)
        self.assertEqual(got["Yolanda Díaz"], 4.22)
        self.assertEqual(got["Alberto Núñez Feijóo"], 3.43)
        self.assertEqual(got["Santiago Abascal"], 2.89)

    def test_valid_n_and_distribution(self):
        for x in self.data["leaders"]:
            self.assertGreater(x["n_valid"], 4000)
            self.assertGreater(x["coverage_pct"], 98)
            self.assertEqual(len(x["distribution_pct"]), 10)


if __name__ == "__main__":
    unittest.main()
