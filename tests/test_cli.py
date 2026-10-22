import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from scone_sto_audit.cli import main

GOOD = (
    "synthetic fixture\nnRows=3\nnColumns=2\ninDegrees=yes\n"
    "endheader\ntime knee_angle_r\n0 10\n0.1 30\n0.2 -40\n"
)


class TestCLI(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.path = self.root / "sample.sto"
        self.path.write_text(GOOD, encoding="utf-8")

    def test_batch_output_and_count(self):
        target = self.root / "summary.json"
        result = main([str(self.path), str(self.path), "--columns", "knee_angle_r", "--output", str(target)])
        self.assertEqual(result, 0)
        report = json.loads(target.read_text())
        self.assertEqual(report["files_analyzed"], 2)
        self.assertIn("not assumed to be independent", report["note"])
        self.assertNotIn(str(self.root), target.read_text())

    def test_failure_no_output_created(self):
        target = self.root / "summary.json"
        with contextlib.redirect_stderr(io.StringIO()):
            result = main([str(self.path), str(self.root / "missing.sto"), "--columns", "knee_angle_r", "--output", str(target)])
        self.assertEqual(result, 2)
        self.assertFalse(target.exists())

    def test_existing_output_preserved_on_failed_batch(self):
        target = self.root / "summary.json"
        target.write_text("old valid report", encoding="utf-8")
        with contextlib.redirect_stderr(io.StringIO()):
            result = main([str(self.path), str(self.root / "missing.sto"), "--columns", "knee_angle_r", "--output", str(target)])
        self.assertEqual(result, 2)
        self.assertEqual(target.read_text(), "old valid report")

    def test_reject_overwrite_input(self):
        before = self.path.read_bytes()
        with contextlib.redirect_stderr(io.StringIO()):
            result = main([str(self.path), "--columns", "knee_angle_r", "--output", str(self.path)])
        self.assertEqual(result, 2)
        self.assertEqual(self.path.read_bytes(), before)

    def test_stdout_json(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = main([str(self.path), "--columns", "knee_angle_r"])
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(output.getvalue())["files_analyzed"], 1)
