from __future__ import annotations

from datetime import datetime, date
from typing import Tuple

import pytz

TZ = pytz.timezone("Europe/Madrid")


BLACKOUT_START = date(2026, 11, 24)
BLACKOUT_END = date(2026, 11, 28)  # inclusive


def is_blackout(dt: datetime | None = None) -> bool:
    if dt is None:
        dt = datetime.now(TZ)
    d = dt.date()
    return d >= BLACKOUT_START and d <= BLACKOUT_END


def blackout_window() -> Tuple[date, date]:
    return BLACKOUT_START, BLACKOUT_END


def blackout_reason() -> str:
    return (
        "Prohibición de publicar, difundir o reproducir sondeos (24–28 nov 2026, LOREG art. 69.7). "
        "La agregación, la robustez y sus JSON quedan retirados; se restablecen el 29 de noviembre."
    )
