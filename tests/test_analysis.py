import hashlib
import math
import tempfile
import unittest
from pathlib import Path

from scone_sto_audit import STOError, analyze, read_sto

GOOD = (
    "synthetic fixture\nversion=1\nnRows=3\nnColumns=3\ninDegrees=yes\n"
    "endheader\ntime hip_flexion_r knee_angle_r\n"
    "0.0 0 10\n0.1 20 30\n0.2 10 -40\n"
)


class TestSTO(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "fixture.sto"
        self.path.write_text(GOOD, encoding="utf-8")

    def test_metrics(self):
        result = analyze(self.path, ["hip_flexion_r", "knee_angle_r"])
        self.assertEqual(result["metrics"]["hip_flexion_r"]["range"], 20)
        self.assertEqual(result["metrics"]["knee_angle_r"]["peak_absolute"], 40)
        self.assertEqual(result["window_time"]["samples"], 3)

    def test_window_inclusive(self):
        result = analyze(self.path, ["knee_angle_r"], 0.1, 0.2)
        self.assertEqual(result["metrics"]["knee_angle_r"]["range"], 70)
        self.assertEqual(result["window_time"]["samples"], 2)

    def test_hash_and_unit_policy(self):
        result = analyze(self.path, ["hip_flexion_r"])
        self.assertEqual(result["input_sha256"], hashlib.sha256(self.path.read_bytes()).hexdigest())
        self.assertEqual(result["inDegrees_header"], "yes")
        self.assertTrue(result["values_in_source_units"])

    def test_missing_channel(self):
        with self.assertRaises(STOError):
            analyze(self.path, ["missing"])

    def test_no_time_column_as_measurement(self):
        with self.assertRaises(STOError):
            analyze(self.path, ["time"])

    def test_empty_columns(self):
        with self.assertRaises(STOError):
            analyze(self.path, [])

    def test_duplicate_columns(self):
        with self.assertRaises(STOError):
            analyze(self.path, ["knee_angle_r", "knee_angle_r"])

    def test_window_outside(self):
        with self.assertRaises(STOError):
            analyze(self.path, ["hip_flexion_r"], 0, 0.5)

    def test_window_without_sample(self):
        with self.assertRaises(STOError):
            analyze(self.path, ["hip_flexion_r"], 0.031, 0.049)

    def test_invalid_window_nan(self):
        with self.assertRaises(STOError):
            analyze(self.path, ["hip_flexion_r"], math.nan, 0.2)

    def test_duplicate_time(self):
        self.path.write_text(GOOD.replace("0.1 20 30", "0.0 20 30"))
        with self.assertRaises(STOError):
            read_sto(self.path)

    def test_time_decreasing(self):
        self.path.write_text(GOOD.replace("0.2 10 -40", "0.05 10 -40"))
        with self.assertRaises(STOError):
            read_sto(self.path)

    def test_nonfinite(self):
        self.path.write_text(GOOD.replace("0.1 20 30", "0.1 NaN 30"))
        with self.assertRaises(STOError):
            read_sto(self.path)

    def test_wrong_width(self):
        self.path.write_text(GOOD.replace("0.1 20 30", "0.1 20"))
        with self.assertRaises(STOError):
            read_sto(self.path)

    def test_bad_nrows(self):
        self.path.write_text(GOOD.replace("nRows=3", "nRows=4"))
        with self.assertRaises(STOError):
            read_sto(self.path)

    def test_missing_endheader(self):
        self.path.write_text(GOOD.replace("endheader", "not_endheader"))
        with self.assertRaises(STOError):
            read_sto(self.path)

    def test_duplicate_header_key(self):
        self.path.write_text(GOOD.replace("nRows=3", "nRows=3\nnRows=4"))
        with self.assertRaises(STOError):
            read_sto(self.path)

    def test_invalid_indegrees(self):
        self.path.write_text(GOOD.replace("inDegrees=yes", "inDegrees=maybe"))
        with self.assertRaises(STOError):
            read_sto(self.path)

    def test_duplicate_channels_case_insensitive(self):
        self.path.write_text(GOOD.replace("hip_flexion_r knee_angle_r", "hip_flexion_r HIP_FLEXION_R"))
        with self.assertRaises(STOError):
            read_sto(self.path)

    def test_utf8_bom(self):
        self.path.write_bytes(b"\xef\xbb\xbf" + GOOD.encode())
        self.assertEqual(len(read_sto(self.path)["rows"]), 3)

    def test_reject_non_utf8(self):
        self.path.write_bytes(b"\xff\xfe")
        with self.assertRaises(STOError):
            read_sto(self.path)

    def test_mean_no_overflow(self):
        self.path.write_text(GOOD.replace("0.0 0 10", "0.0 1e308 10").replace("0.1 20 30", "0.1 1e308 30").replace("0.2 10 -40", "0.2 1e308 -40"))
        self.assertEqual(analyze(self.path, ["hip_flexion_r"])["metrics"]["hip_flexion_r"]["mean_sampled"], 1e308)

    def test_range_overflow_rejected(self):
        self.path.write_text(GOOD.replace("0.0 0 10", "0.0 -1e308 10").replace("0.1 20 30", "0.1 1e308 30"))
        with self.assertRaises(STOError):
            analyze(self.path, ["hip_flexion_r"])
