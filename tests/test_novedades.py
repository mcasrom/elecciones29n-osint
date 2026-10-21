import os
import tempfile
import unittest
from datetime import datetime

import pytz

from agg.aggregate import _novedades

TZ = pytz.timezone("Europe/Madrid")


def poll(pollster, day, kind="tracking"):
    return {
        "pollster": pollster,
        "date": datetime.strptime(day, "%Y-%m-%d").replace(tzinfo=TZ),
        "kind": kind,
    }


class NovedadesTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.old = os.getcwd()
        os.chdir(self.tmp.name)
        os.makedirs("data", exist_ok=True)

    def tearDown(self):
        os.chdir(self.old)
        self.tmp.cleanup()

    def test_seed_does_not_alert(self):
        now = datetime(2026, 10, 21, 9, 0, tzinfo=TZ)
        self.assertEqual(_novedades([poll("A", "2026-10-01")], now), [])

    def test_new_poll_and_same_day_kept(self):
        now = datetime(2026, 10, 21, 9, 0, tzinfo=TZ)
        _novedades([poll("A", "2026-10-01")], now)
        nov = _novedades([poll("A", "2026-10-01"), poll("B", "2026-10-20")], now)
        self.assertEqual(nov, [{"pollster": "B", "date": "2026-10-20"}])
        self.assertEqual(
            _novedades([poll("A", "2026-10-01"), poll("B", "2026-10-20")], now), nov
        )

    def test_next_day_clears(self):
        _novedades([poll("A", "2026-10-01")], datetime(2026, 10, 21, 9, 0, tzinfo=TZ))
        _novedades(
            [poll("A", "2026-10-01"), poll("B", "2026-10-20")],
            datetime(2026, 10, 21, 9, 0, tzinfo=TZ),
        )
        later = datetime(2026, 10, 22, 9, 0, tzinfo=TZ)
        self.assertEqual(
            _novedades([poll("A", "2026-10-01"), poll("B", "2026-10-20")], later), []
        )

    def test_averages_ignored(self):
        now = datetime(2026, 10, 21, 9, 0, tzinfo=TZ)
        _novedades([poll("A", "2026-10-01")], now)
        self.assertEqual(
            _novedades([poll("A", "2026-10-01"), poll("Promedio", "2026-10-20", "average")], now),
            [],
        )


if __name__ == "__main__":
    unittest.main()
