import unittest

from gen.build import build_calibration


class CalibrationTest(unittest.TestCase):
    def test_pending_without_inputs(self):
        self.assertEqual(build_calibration({}, {})["status"], "pending")
        self.assertEqual(build_calibration({"votos": {"PP": 1}}, {})["status"], "pending")

    def test_ready_rows_and_seats(self):
        res = {
            "votos": {"PP": 8000000, "PSOE": 7000000},
            "diputados": {"PP": 140, "PSOE": 120},
            "meta": {"url": "https://example.org", "actualizado": "2026-11-29"},
        }
        snap = {
            "updated_at": "2026-11-23",
            "n_polls": 10,
            "parties": [{"party": "PP", "mean": 32}, {"party": "PSOE", "mean": 28}],
            "hemicycle_last": {"seats": [{"party": "PP", "seats": 145}, {"party": "PSOE", "seats": 115}]},
        }
        out = build_calibration(res, snap)
        self.assertEqual(out["status"], "ready")
        self.assertEqual(out["n"], 2)
        self.assertAlmostEqual(out["rows"][0]["error"], 32 - 100 * 8000000 / 15000000, places=2)
        self.assertEqual(out["seat_rows"][0]["error"], 5)
        self.assertEqual(out["official_url"], "https://example.org")


if __name__ == "__main__":
    unittest.main()
