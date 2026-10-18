import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "needs.py"


class NeedsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.repo = base / "repo"
        self.state = base / "state"
        self.logs = base / "logs"
        (self.repo / "web" / "data").mkdir(parents=True)
        (self.repo / "data").mkdir(parents=True)
        self.env = os.environ.copy()
        self.env.update({
            "ELECCIONES29N_REPO": str(self.repo),
            "ELECCIONES29N_STATE_DIR": str(self.state),
            "ELECCIONES29N_LOG_DIR": str(self.logs),
        })
        self.write_latest()

    def tearDown(self):
        self.tmp.cleanup()

    def write_latest(self, updated="2026-10-18T08:00:00+02:00", status="ok", days=4, n=15):
        data = {
            "updated_at": "2026-10-18 08:00 CEST",
            "updated_at_iso": updated,
            "in_blackout": False,
            "n_polls": n,
            "last_poll_date": "2026-10-14",
            "health": {
                "status": status,
                "n_polls": n,
                "n_pollsters": 12,
                "days_since_last": days,
                "reasons": [] if status == "ok" else ["pocos sondeos"],
            },
        }
        (self.repo / "web" / "data" / "latest.json").write_text(json.dumps(data), encoding="utf-8")

    def run_cmd(self, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            env=self.env,
            capture_output=True,
            text=True,
            cwd=str(ROOT),
        )

    def test_seed_is_idempotent(self):
        self.assertEqual(self.run_cmd("seed").returncode, 0)
        path = self.state / "needs.json"
        first = json.loads(path.read_text(encoding="utf-8"))
        self.run_cmd("seed")
        second = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(len(first["tasks"]), 3)
        self.assertEqual(len(second["tasks"]), 3)

    def test_done_marks_manual_task(self):
        self.run_cmd("seed")
        self.run_cmd("done", "gsc-index")
        data = json.loads((self.state / "needs.json").read_text(encoding="utf-8"))
        task = next(t for t in data["tasks"] if t["id"] == "gsc-index")
        self.assertEqual(task["status"], "done")

    def test_stale_data_is_auto_task_and_panel(self):
        self.write_latest(updated="2026-01-01T00:00:00+01:00")
        out = self.run_cmd("list", "--json").stdout
        ids = {t["id"] for t in json.loads(out)}
        self.assertIn("auto:stale", ids)
        self.assertEqual(self.run_cmd("digest", "--no-notify").returncode, 0)
        panel = (self.state / "needs.html").read_text(encoding="utf-8")
        self.assertIn("29N - lo que necesita tu atención", panel)

    def test_example_inbox_is_ignored(self):
        (self.repo / "data" / "entrada_sondeos.csv").write_text(
            "pollster,date,sample,source_url,values\n"
            "EJEMPLO,2026-10-20,1500,https://ejemplo.com,PP=31.8;PSOE=27.1\n",
            encoding="utf-8",
        )
        out = self.run_cmd("list", "--json").stdout
        ids = {t["id"] for t in json.loads(out)}
        self.assertNotIn("auto:inbox", ids)


if __name__ == "__main__":
    unittest.main()
