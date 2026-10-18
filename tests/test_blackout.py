import unittest
from datetime import datetime

import pytz

from agg import blackout

TZ = pytz.timezone("Europe/Madrid")


class BlackoutTest(unittest.TestCase):
    def test_24_inclusive(self):
        self.assertTrue(blackout.is_blackout(TZ.localize(datetime(2026, 11, 24, 0, 0))))

    def test_28_inclusive(self):
        self.assertTrue(blackout.is_blackout(TZ.localize(datetime(2026, 11, 28, 23, 59, 59))))

    def test_23_not(self):
        self.assertFalse(blackout.is_blackout(TZ.localize(datetime(2026, 11, 23, 23, 59, 59))))

    def test_29_not(self):
        self.assertFalse(blackout.is_blackout(TZ.localize(datetime(2026, 11, 29, 0, 0))))

    def test_window_reason(self):
        start, end = blackout.blackout_window()
        self.assertEqual(start, blackout.BLACKOUT_START)
        self.assertEqual(end, blackout.BLACKOUT_END)
        self.assertIn("24–28 nov 2026", blackout.blackout_reason())


if __name__ == "__main__":
    unittest.main()
