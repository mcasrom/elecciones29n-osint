import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime

import pytz

from gen import build

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VALIDATOR = os.path.join(ROOT, "scripts", "validate_site.py")


class BlackoutSiteTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.site = os.path.join(self.tmp, "site")
        shutil.copytree(os.path.join(ROOT, "web"), self.site)
        self._old_out = build.OUT

    def tearDown(self):
        build.OUT = self._old_out
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_blackout_removes_aggregate_and_validates(self):
        build.OUT = self.site
        build.write_blackout_site(
            datetime(2026, 11, 24, 9, 0, tzinfo=pytz.timezone("Europe/Madrid")),
            "202611240900",
            "2026-11-24",
            "0.10.2",
            "test",
        )
        self.assertFalse(os.path.exists(os.path.join(self.site, "data/latest.json")))
        self.assertFalse(os.path.exists(os.path.join(self.site, "data/robustez.json")))
        html = open(os.path.join(self.site, "index.html"), encoding="utf-8").read()
        self.assertIn("Blackout electoral", html)
        self.assertNotIn('class="chart"', html)
        r = subprocess.run(
            [sys.executable, VALIDATOR, self.site],
            capture_output=True,
            text=True,
        )
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("blackout OK", r.stdout)


if __name__ == "__main__":
    unittest.main()
