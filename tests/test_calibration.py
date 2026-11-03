import unittest

from gen.build import build_calibration


class CalibrationTest(unittest.TestCase):
    def test_pending_without_inputs(self):
        self.assertEqual(build_calibration({}, {})["status"], "pending")
        self.assertEqual(build_calibration({"votos": {"PP": 1}}, {})["status"], "pending")

    def test_ready_rows_and_house_errors(self):
        res = {
            "votos": {"PP": 8000000, "PSOE": 7000000},
            "votos_validos": 15000000,
            "diputados": {"PP": 140, "PSOE": 120},
            "meta": {"url": "https://example.org", "actualizado": "2026-11-29"},
        }
        snap = {
            "updated_at": "2026-11-23",
            "n_polls": 10,
            "parties": [{"party": "PP", "mean": 32}, {"party": "PSOE", "mean": 28}],
            "house_latest": [
                {"pollster": "A", "date": "2026-11-22", "pp": 33, "psoe": 27},
            ],
        }
        out = build_calibration(res, snap)
        self.assertEqual(out["status"], "ready")
        self.assertEqual(out["n"], 2)
        self.assertAlmostEqual(out["rows"][0]["error"], 32 - 100 * 8000000 / 15000000, places=2)
        self.assertEqual(out["votos_validos"], 15000000)
        self.assertEqual(len(out["house_rows"]), 2)
        self.assertAlmostEqual(out["house_rows"][0]["error"], 33 - 100 * 8000000 / 15000000, places=2)
        self.assertNotIn("seat_rows", out)
        self.assertEqual(out["official_url"], "https://example.org")

    def test_fallback_denominator_is_flagged(self):
        res = {"votos": {"PP": 1, "PSOE": 1}}
        snap = {"parties": [{"party": "PP", "mean": 50}, {"party": "PSOE", "mean": 50}]}
        out = build_calibration(res, snap)
        self.assertEqual(out["status"], "ready")
        self.assertEqual(out["denominator_source"], "suma de votos importados")


if __name__ == "__main__":
    unittest.main()
