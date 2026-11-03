import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("alertas_email", ROOT / "scripts" / "alertas_email.py")
ae = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ae)


class AlertasEmailTest(unittest.TestCase):
    def latest(self):
        return {
            "n_polls": 12,
            "last_poll_date": "2026-11-02",
            "novedades": [{"pollster": "Sigma Dos", "date": "2026-11-02"}],
            "parties": [
                {"party": "PP", "mean": 31.38, "min": 28.5, "max": 33.0},
                {"party": "PSOE", "mean": 26.24, "min": 24.6, "max": 27.6},
                {"party": "VOX", "mean": 19.32, "min": 18.6, "max": 20.0},
                {"party": "SUMAR", "mean": 6.63, "min": 4.6, "max": 8.9},
            ],
            "hemicycle": [{"blocks": {"right": 213, "left": 137}, "majority": "right"}],
        }

    def test_new_poll_reason_and_subject(self):
        cur = {"n_polls": 12, "last_poll_date": "2026-11-02", "means": {"PP": 31.38},
               "blocks": {"right": 213, "left": 137}, "majority": "right"}
        prev = dict(cur, n_polls=7, last_poll_date="2026-11-01")
        self.assertEqual(ae.reason(prev, cur), "nuevo sondeo")
        subject, html, text = ae.render(self.latest(), {"id": "test"}, "nuevo sondeo")
        self.assertIn("actualización de la media", subject)
        self.assertIn("Sigma Dos (02/11)", subject)
        self.assertIn("/api/unsubscribe?id=test", html)
        self.assertIn("No es un pronóstico", text)

    def test_fingerprint_changes_with_media(self):
        a = self.latest()
        b = self.latest()
        b["parties"][1]["mean"] = 26.9
        self.assertNotEqual(ae.fingerprint(a), ae.fingerprint(b))

    def test_no_change(self):
        cur = {"n_polls": 12, "last_poll_date": "2026-11-02", "means": {"PP": 31.38},
               "blocks": {"right": 213, "left": 137}, "majority": "right"}
        self.assertEqual(ae.reason(cur, cur), "datos actualizados")


if __name__ == "__main__":
    unittest.main()
