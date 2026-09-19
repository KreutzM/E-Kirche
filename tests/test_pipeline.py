"""Regression checks for evidence preservation and invalid-data rejection."""
import contextlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import urllib.error
from unittest.mock import patch

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import fetch_assets as fetch


class DownloadTests(unittest.TestCase):
    def test_rate_limit_stops_remaining_requests(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            manifest = root / "manifest.json"
            manifest.write_text(json.dumps([
                {"id": name, "title": "test.jpg", "group": "modern", "priority": 1}
                for name in ("M01", "M02")
            ]))
            error = urllib.error.HTTPError("https://example.invalid", 429, "Rate limited", {}, None)
            with patch.multiple(fetch, ROOT=root, MANIFEST=manifest, META=root / "meta.jsonl", REPORT=root / "report.csv"), \
                 patch.object(sys, "argv", ["fetch_assets.py"]), \
                 patch.object(fetch, "info", side_effect=error) as info, \
                 contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(fetch.main(), 1)
                self.assertEqual(info.call_count, 1)
            self.assertIn("M02,DEFERRED", (root / "report.csv").read_text())

    def test_license_rejects_restricted_and_unknown_labels(self):
        for name in ("CC BY-SA 4.0", "Public domain", "CC0", "GFDL 1.2"):
            self.assertTrue(fetch.allowed(name), name)
        for name in ("CC BY-NC 4.0", "CC BY-ND 4.0", "not public domain", "", "unknown"):
            self.assertFalse(fetch.allowed(name), name)

    def test_existing_reference_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as temp:
            dest = Path(temp) / "evidence.jpg"
            dest.write_bytes(b"original evidence")
            with self.assertRaises(FileExistsError):
                fetch.download("https://example.invalid/image", dest)
            self.assertEqual(dest.read_bytes(), b"original evidence")

    def test_failed_download_preserves_provenance_and_returns_failure(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            manifest = root / "manifest.json"
            manifest.write_text(json.dumps([{"id": "M01", "title": "test.jpg", "group": "modern", "priority": 1}]))
            meta = root / "metadata.jsonl"
            prior = '{"dataset_id":"old"}\n'
            meta.write_text(prior)
            with patch.multiple(fetch, ROOT=root, MANIFEST=manifest, META=meta, REPORT=root / "report.csv"), \
                 patch.object(sys, "argv", ["fetch_assets.py"]), \
                 patch.object(fetch, "info", side_effect=RuntimeError("network unavailable")), \
                 patch.object(fetch.time, "sleep"), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(fetch.main(), 1)
            self.assertEqual(meta.read_text(), prior)


class ValidationTests(unittest.TestCase):
    def test_rejects_wrong_axes_and_undocumented_assumption(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for directory in ("data", "sources", "validation"):
                shutil.copytree(ROOT / directory, root / directory, ignore=shutil.ignore_patterns("renders", "*.jsonl", "*.csv"))
            (root / "scripts").mkdir()
            script = root / "scripts/validate_dataset.py"
            shutil.copyfile(ROOT / "scripts/validate_dataset.py", script)
            valid = subprocess.run([sys.executable, str(script)], capture_output=True, text=True)
            self.assertEqual(valid.returncode, 0, valid.stdout + valid.stderr)
            coords = root / "data/coordinate_system.yaml"
            data = yaml.safe_load(coords.read_text())
            data["axes"]["x_positive"] = "west"
            coords.write_text(yaml.safe_dump(data))
            (root / "data/assumptions.yaml").write_text("assumptions:\n  guessed_wall:\n    value: 1.0\n")
            invalid = subprocess.run([sys.executable, str(script)], capture_output=True, text=True)
            self.assertEqual(invalid.returncode, 1)
            self.assertIn("x_positive must be east", invalid.stdout)
            self.assertIn("assumption guessed_wall: missing", invalid.stdout)


if __name__ == "__main__":
    unittest.main()
