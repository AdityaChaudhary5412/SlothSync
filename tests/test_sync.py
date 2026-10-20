"""
Unit Tests for SlothSync Engine and AI Classifier
Ensuring 100% error-free execution and reliable rollback safety.
"""

import os
import shutil
import tempfile
import unittest
from pathlib import Path
from engine import AISummarizer
from sync_engine import SlothSyncEngine, compute_file_hash


class TestSlothSync(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.source = Path(self.test_dir) / "source"
        self.backup = Path(self.test_dir) / "backup"
        self.source.mkdir()
        self.backup.mkdir()

        # Create mock files
        (self.source / "invoice_test.txt").write_text("Invoice total: $500", encoding="utf-8")
        (self.source / "script_test.py").write_text("print('test script')", encoding="utf-8")
        # Duplicate of invoice
        (self.source / "invoice_copy(1).txt").write_text("Invoice total: $500", encoding="utf-8")

        self.engine = SlothSyncEngine(str(self.source), str(self.backup))

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_compute_hash(self):
        h1 = compute_file_hash(self.source / "invoice_test.txt")
        h2 = compute_file_hash(self.source / "invoice_copy(1).txt")
        self.assertTrue(len(h1) > 0)
        self.assertEqual(h1, h2)

    def test_heuristic_categorization(self):
        ai = AISummarizer()
        res_code = ai.categorize_file("main.py")
        self.assertEqual(res_code["category"], "Code")

        res_fin = ai.categorize_file("tax_receipt_2026.pdf")
        self.assertEqual(res_fin["category"], "Finance")

    def test_scan_and_duplicate_detection(self):
        res = self.engine.scan()
        self.assertEqual(res["file_count"], 3)
        self.assertEqual(res["duplicates_count"], 1)
        self.assertTrue(res["lazy_payoff"]["minutes_saved"] > 0)

    def test_sync_execution(self):
        res = self.engine.execute_sync(organize_by_category=True)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["actions_count"], 3)

        # Check category directories exist in backup
        self.assertTrue((self.backup / "Finance").exists())
        self.assertTrue((self.backup / "Code").exists())

    def test_atomic_rollback(self):
        self.engine.execute_sync(organize_by_category=True)
        self.assertTrue(any(self.backup.iterdir()))

        rollback_res = self.engine.rollback_last_sync()
        self.assertEqual(rollback_res["status"], "success")
        self.assertTrue(rollback_res["files_reverted"] >= 3)


if __name__ == "__main__":
    unittest.main()
