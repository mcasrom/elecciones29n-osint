import json
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "m5_results.json")


class M5Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = json.load(open(DATA, encoding="utf-8"))

    def test_panel(self):
        self.assertGreaterEqual(self.d["meta"]["n"], 700)
        self.assertLessEqual(self.d["meta"]["n"], 850)
        self.assertEqual(self.d["meta"]["elecciones"], 16)
        self.assertEqual(self.d["meta"]["provincias"], 52)

    def test_bins(self):
        self.assertEqual(len(self.d["bins"]), 4)
        self.assertTrue(all("part" in b and "n" in b for b in self.d["bins"]))

    def test_model(self):
        c = self.d["modelo"]["coef"]["prec_media"]
        self.assertLess(c["beta"], 0)
        self.assertLessEqual(c["ci_low"], c["beta"])
        self.assertGreaterEqual(c["ci_high"], c["beta"])
        self.assertIn("desde_2004", self.d["robustez"])

    def test_caveats(self):
        self.assertTrue(any("causal" in x.lower() for x in self.d["limites"]))


if __name__ == "__main__":
    unittest.main()
