import unittest
from scripts.campaign_digest import build_text, detect


class CampaignDigestTest(unittest.TestCase):
    def test_initial(self):
        cur = {"date": "2026-11-13", "n_polls": 8, "last_poll_date": "2026-11-12",
               "parties": {"PP": 30, "PSOE": 28, "VOX": 18, "SUMAR": 6},
               "seats": {"PP": 125, "PSOE": 118, "VOX": 80, "SUMAR": 27},
               "blocks": {"right": 205, "left": 145}, "majority": "right"}
        self.assertEqual(detect({}, cur), ["inicio del parte"])
        self.assertIn("13 nov", build_text(cur, {}))

    def test_no_change(self):
        cur = {"date": "2026-11-14", "n_polls": 8, "last_poll_date": "2026-11-12",
               "parties": {"PP": 30, "PSOE": 28, "VOX": 18, "SUMAR": 6},
               "seats": {"PP": 125, "PSOE": 118, "VOX": 80, "SUMAR": 27},
               "blocks": {"right": 205, "left": 145}, "majority": "right"}
        self.assertEqual(detect(cur, cur), [])

    def test_relevant_change(self):
        prev = {"n_polls": 8, "last_poll_date": "2026-11-12",
                "parties": {"PP": 30, "PSOE": 28, "VOX": 18, "SUMAR": 6},
                "seats": {"PP": 125, "PSOE": 118, "VOX": 80, "SUMAR": 27},
                "blocks": {"right": 205, "left": 145}, "majority": "right"}
        cur = dict(prev, n_polls=9, last_poll_date="2026-11-13",
                   parties=dict(prev["parties"], PP=32),
                   seats=dict(prev["seats"], PP=130))
        r = detect(prev, cur)
        self.assertIn("nuevo sondeo", r)
        self.assertIn("PP +2.0 pp", r)
        self.assertIn("PP +5 escaños", r)


if __name__ == "__main__":
    unittest.main()
