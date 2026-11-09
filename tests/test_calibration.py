import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

import pytz

from gen import build
from gen.build import build_calibration, snapshot_due


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

    def test_snapshot_write_is_immutable_after_cutoff(self):
        latest = {"updated_at": "2026-11-23 23:50", "n_polls": 12,
                  "parties": [{"party": "PP", "mean": 31, "min": 29, "max": 33, "n": 12}],
                  "house_latest": [], "hemicycle": []}
        tz = pytz.timezone("Europe/Madrid")
        with tempfile.TemporaryDirectory() as td:
            old = (build.PRE_SNAPSHOT_FINAL, build.PRE_SNAPSHOT_WORKING, build.PRE_SNAPSHOT_MARKER)
            try:
                build.PRE_SNAPSHOT_FINAL = Path(td) / "final.json"
                build.PRE_SNAPSHOT_WORKING = Path(td) / "working.json"
                build.PRE_SNAPSHOT_MARKER = Path(td) / "freeze.json"
                before = tz.localize(datetime(2026, 11, 23, 23, 49))
                self.assertFalse(build.write_pre_election_snapshot(latest, before))
                self.assertTrue(build.PRE_SNAPSHOT_WORKING.exists())
                self.assertFalse(build.PRE_SNAPSHOT_FINAL.exists())
                at_cutoff = tz.localize(datetime(2026, 11, 23, 23, 50))
                self.assertTrue(build.write_pre_election_snapshot(latest, at_cutoff))
                first = json.loads(build.PRE_SNAPSHOT_FINAL.read_text(encoding="utf-8"))
                self.assertTrue(first["sha256"])
                self.assertTrue(build.PRE_SNAPSHOT_MARKER.exists())
                changed = dict(latest, n_polls=99)
                self.assertFalse(build.write_pre_election_snapshot(changed, at_cutoff))
                second = json.loads(build.PRE_SNAPSHOT_FINAL.read_text(encoding="utf-8"))
                self.assertEqual(first["sha256"], second["sha256"])
            finally:
                build.PRE_SNAPSHOT_FINAL, build.PRE_SNAPSHOT_WORKING, build.PRE_SNAPSHOT_MARKER = old

    def test_snapshot_freezes_after_last_build_before_blackout(self):
        tz = pytz.timezone("Europe/Madrid")
        self.assertFalse(snapshot_due(tz.localize(datetime(2026, 11, 23, 23, 49))))
        self.assertTrue(snapshot_due(tz.localize(datetime(2026, 11, 23, 23, 50))))

    def test_pre_registered_parties_and_blocs(self):
        votes = {"PP": 30, "PSOE": 25, "VOX": 20, "SUMAR": 7, "ERC": 3, "JUNTS": 3, "PNV": 2, "PODEMOS": 2}
        snap = {"parties": [{"party": p, "mean": v} for p, v in votes.items()]}
        out = build_calibration({"votos": votes, "votos_validos": 100}, snap)
        names = {r["party"] for r in out["rows"]}
        self.assertEqual(names, {"PP", "PSOE", "VOX", "SUMAR", "ERC", "JUNTS", "PNV"})
        self.assertEqual(len(out["block_rows"]), 2)
        self.assertEqual({r["bloc"] for r in out["block_rows"]}, {"PP + VOX", "PSOE + SUMAR + PODEMOS"})

    def test_fallback_denominator_is_flagged(self):
        res = {"votos": {"PP": 1, "PSOE": 1}}
        snap = {"parties": [{"party": "PP", "mean": 50}, {"party": "PSOE", "mean": 50}]}
        out = build_calibration(res, snap)
        self.assertEqual(out["status"], "ready")
        self.assertEqual(out["denominator_source"], "suma de votos importados")


if __name__ == "__main__":
    unittest.main()
