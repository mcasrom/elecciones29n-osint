import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IMPORT = ROOT / "scripts" / "import_resultados.py"


class NocheElectoralTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        (self.tmp / "data").mkdir()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _run(self, csv_text):
        (self.tmp / "data" / "entrada_resultados.csv").write_text(csv_text, encoding="utf-8")
        return subprocess.run(
            [sys.executable, str(IMPORT)], cwd=self.tmp, capture_output=True, text=True
        )

    def test_import_valid_results(self):
        csv_text = """tipo,clave,valor,fuente_url
participacion,,66.5,https://example.invalid/oficial
validos,,1000,https://example.invalid/oficial
diputados,PP,3,https://example.invalid/oficial
votos,PP,300,https://example.invalid/oficial
"""
        r = self._run(csv_text)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        out = json.loads((self.tmp / "data" / "resultados_29n.json").read_text())
        self.assertEqual(out["participacion"], 66.5)
        self.assertEqual(out["votos_validos"], 1000)
        self.assertEqual(out["diputados"]["PP"], 3)
        self.assertEqual(out["votos"]["PP"], 300)

    def test_import_rejects_missing_source(self):
        r = self._run("tipo,clave,valor,fuente_url\nparticipacion,,66.5,\n")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("sin fuente_url", r.stdout)


if __name__ == "__main__":
    unittest.main()
