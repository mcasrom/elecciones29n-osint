import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VALIDATOR = os.path.join(ROOT, "scripts", "validate_site.py")


class ValidateSiteTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.site = os.path.join(self.tmp, "site")
        shutil.copytree(os.path.join(ROOT, "web"), self.site)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run_validator(self):
        return subprocess.run(
            [sys.executable, VALIDATOR, self.site],
            capture_output=True, text=True,
        )

    def test_accepts_current_site(self):
        r = self.run_validator()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_rejects_missing_chart(self):
        p = os.path.join(self.site, "index.html")
        html = open(p, encoding="utf-8").read().replace('class="chart"', 'class="chart-broken"')
        open(p, "w", encoding="utf-8").write(html)
        r = self.run_validator()
        self.assertEqual(r.returncode, 1)
        self.assertIn("sin gráfico", r.stdout)


if __name__ == "__main__":
    unittest.main()
