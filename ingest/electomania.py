from __future__ import annotations

import re
from datetime import datetime
from typing import List, Dict, Any

import pytz
from bs4 import BeautifulSoup

from ingest.base import get_session, polite_sleep

TZ = pytz.timezone("Europe/Madrid")

URL_BASE = "https://electomania.es"


def _parse_date(s: str) -> datetime | None:
    s = s.strip()
    # Formatos típicos ES
    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(s, fmt)
            return TZ.localize(dt)
        except ValueError:
            continue
    # Intento suave
    m = re.search(r"(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{4})", s)
    if m:
        try:
            dt = datetime(int(m.group(3)), int(m.group(2)), int(m.group(1)))
            return TZ.localize(dt)
        except Exception:
            pass
    return None


def extract_polls() -> List[Dict[str, Any]]:
    # MVP: estructura vacía segura. Añadiremos extracción real con validación
    # y fail-safe (no actualiza si datos inválidos)
    return []
