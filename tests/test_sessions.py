"""End-to-end checks for sessions without AI. Run with: python -m unittest discover tests"""
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class NoAiSessions(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Path(self.tmp.name) / "journal.db"
        self.exports = Path(self.tmp.name) / "exports"
        self.env = {
            **os.environ,
            "DAILYJOURNAL_DB_PATH": str(self.db),
            "DAILYJOURNAL_SYNC_DIR": str(self.exports),
            "DAILYJOURNAL_NO_AI": "1",
            "HOME": self.tmp.name,
            "APPDATA": self.tmp.name,
            "PYTHONIOENCODING": "utf-8",
        }
        self.env.pop("OPENAI_API_KEY", None)

    def tearDown(self):
        self.tmp.cleanup()

    def run_cli(self, *args, stdin=""):
        result = subprocess.run(
            [sys.executable, str(ROOT / "app.py"), *args],
            input=stdin, capture_output=True, text=True, encoding="utf-8", env=self.env, cwd=ROOT,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def rows(self, session_type):
        with sqlite3.connect(self.db) as con:
            con.row_factory = sqlite3.Row
            return [dict(r) for r in con.execute("SELECT * FROM sessions WHERE session_type = ?", (session_type,))]

    def test_morning_then_evening(self):
        out = self.run_cli("am", stdin="Ship the invoice report\nWalk with the kids at 6\nSlack\nIf I open Slack, I close it and stand up\nslept badly\n.done\n")
        self.assertIn("Work One Thing: Ship the invoice report", out)
        am = self.rows("am")[0]
        self.assertEqual(am["work_one_thing"], "Ship the invoice report")
        self.assertEqual(am["family_one_thing"], "Walk with the kids at 6")
        self.assertEqual(am["if_then_plan"], "If I open Slack, I close it and stand up")
        self.assertEqual(am["free_text"], "slept badly")

        self.run_cli("append", "Report is half done")

        out = self.run_cli("pm", stdin="Yes, sent at 3\nNo, it rained\nSlack again\nMute it until noon\nFinish the audit\nmaybe\ny\nn\n.done\n")
        self.assertIn("Ship the invoice report", out)
        self.assertIn("Please answer y or n.", out)
        pm = self.rows("pm")[0]
        self.assertEqual((pm["work_done"], pm["family_done"]), (1, 0))
        self.assertEqual(pm["distraction_cause"], "Slack again")
        self.assertEqual(pm["improvement"], "Mute it until noon")
        self.assertEqual(pm["tomorrow_focus"], "Finish the audit")
        self.assertIn("Work Result: Done. Yes, sent at 3", pm["summary"])
        self.assertIn("Family Result: Not done. No, it rained", pm["summary"])
        self.assertIn("Report is half done", pm["raw_transcript"])

        # Tomorrow's focus carries into the next morning, and every entry was exported.
        out = self.run_cli("am", stdin="a\nb\nc\nd\n.done\n")
        self.assertIn("Finish the audit", out)
        exported = [json.loads(p.read_text(encoding="utf-8")) for p in self.exports.glob("*.json")]
        self.assertEqual(len(exported), 4)
        self.assertIn("[PM] Work Result: Done", self.run_cli("last"))

    def test_evening_without_morning(self):
        self.run_cli("pm", stdin="Fix the gate\nHalf done\nStart earlier\nFinish the gate\nn\n.done\n")
        pm = self.rows("pm")[0]
        self.assertEqual((pm["work_done"], pm["family_done"]), (0, 0))
        self.assertEqual(pm["tomorrow_focus"], "Finish the gate")
        self.assertEqual(pm["improvement"], "Start earlier")
        self.assertNotIn("Family Result", pm["summary"])

    def test_help_names_the_mode(self):
        self.assertIn("dailyjournal 0.2.0", self.run_cli("help"))
        self.assertEqual(self.run_cli("--version").strip(), "0.2.0")


if __name__ == "__main__":
    unittest.main()
