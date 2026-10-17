from datetime import datetime
import pytz
from agg import blackout


def test_blackout_20261124_inclusive():
    tz = pytz.timezone("Europe/Madrid")
    dt = tz.localize(datetime(2026, 11, 24, 0, 0, 0))
    assert blackout.is_blackout(dt) is True


def test_blackout_20261128_inclusive():
    tz = pytz.timezone("Europe/Madrid")
    dt = tz.localize(datetime(2026, 11, 28, 23, 59, 59))
    assert blackout.is_blackout(dt) is True


def test_blackout_before_false():
    tz = pytz.timezone("Europe/Madrid")
    dt = tz.localize(datetime(2026, 11, 23, 23, 59, 59))
    assert blackout.is_blackout(dt) is False


def test_blackout_after_false():
    tz = pytz.timezone("Europe/Madrid")
    dt = tz.localize(datetime(2026, 11, 29, 0, 0, 0))
    assert blackout.is_blackout(dt) is False


def test_blackout_window_reason():
    start, end = blackout.blackout_window()
    assert start == blackout.BLACKOUT_START
    assert end == blackout.BLACKOUT_END
    assert "24–28 nov 2026" in blackout.blackout_reason()
