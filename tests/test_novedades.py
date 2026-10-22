import tempfile
import unittest
from pathlib import Path

from gen import novedades


class NovedadesTest(unittest.TestCase):
    def test_parsea_version_y_bullets(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "CHANGELOG.md"
            p.write_text(
                "# Cambios\n\n## 0.9.0 — 2026-10-22\n\n"
                "- **Fuente**: Ministerio del Interior.\n"
                "- Enlace: [datos](https://example.org/datos).\n",
                encoding="utf-8",
            )
            entries = novedades.parse(p)
            self.assertEqual(len(entries), 1)
            self.assertEqual(entries[0]["version"], "0.9.0")
            self.assertEqual(entries[0]["date"], "2026-10-22")
            self.assertEqual(len(entries[0]["bullets"]), 2)
            self.assertIn("<strong>Fuente</strong>", str(entries[0]["bullets"][0]))
            self.assertIn('href="https://example.org/datos"', str(entries[0]["bullets"][1]))

    def test_sin_fichero(self):
        self.assertEqual(novedades.parse("/nonexistent/CHANGELOG.md"), [])


if __name__ == "__main__":
    unittest.main()
