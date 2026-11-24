import unittest
from gen.build import build_calibration


class PostElectoralCalibrationTest(unittest.TestCase):
    def test_calibration_vote_and_blocks(self):
        snapshot = {
            "parties": [
                {"party": "PP", "mean": 31.0},
                {"party": "PSOE", "mean": 24.0},
                {"party": "VOX", "mean": 16.0},
                {"party": "SUMAR", "mean": 9.0},
                {"party": "PODEMOS", "mean": 1.0},
                {"party": "ERC", "mean": 4.0},
                {"party": "JUNTS", "mean": 6.0},
                {"party": "PNV", "mean": 5.0},
            ],
            "house_latest": [],
        }
        resultados = {
            "votos_validos": 1000,
            "votos": {"PP": 300, "PSOE": 250, "VOX": 150, "SUMAR": 100, "PODEMOS": 20, "ERC": 50, "JUNTS": 50, "PNV": 50},
        }
        c = build_calibration(resultados, snapshot)
        self.assertEqual(c["status"], "ready")
        self.assertEqual(len(c["rows"]), 7)
        self.assertAlmostEqual(c["mae"], 0.86, places=2)
        self.assertAlmostEqual(c["bias"], 0.0, places=2)
        self.assertEqual(c["rows"][0]["party"], "PP")
        self.assertEqual(c["rows"][0]["official"], 30.0)
        self.assertEqual(c["block_rows"][0]["bloc"], "PP + VOX")

    def test_calibration_pending_without_results(self):
        self.assertEqual(build_calibration({}, {})["status"], "pending")


if __name__ == "__main__":
    unittest.main()
