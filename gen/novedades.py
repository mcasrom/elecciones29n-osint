from __future__ import annotations

import html
import re
from pathlib import Path

from markupsafe import Markup

_HEADER = re.compile(r"^##\s+(?P<version>\S+)\s+[—–-]\s+(?P<date>.+?)\s*$")
_LINK = re.compile(r"\[([^\]]+)\]\((https?://[^)]+)\)")
_CODE = re.compile(r"`([^`]+)`")
_BOLD = re.compile(r"\*\*([^*]+)\*\*")


def _inline(text: str) -> Markup:
    text = html.escape(text.strip(), quote=False)
    text = _LINK.sub(r'<a href="\2" rel="noopener">\1</a>', text)
    text = _CODE.sub(r"<code>\1</code>", text)
    text = _BOLD.sub(r"<strong>\1</strong>", text)
    return Markup(text)


def parse(path: str | Path = "CHANGELOG.md") -> list[dict]:
    p = Path(path)
    if not p.exists():
        return []
    entries: list[dict] = []
    current = None
    for raw in p.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        m = _HEADER.match(line)
        if m:
            current = {
                "version": m.group("version"),
                "date": m.group("date"),
                "bullets": [],
            }
            entries.append(current)
            continue
        if current is not None and line.startswith("- "):
            current["bullets"].append(_inline(line[2:]))
    return entries
