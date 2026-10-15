# Copyright © 2026 Isto Hunttila
# SPDX-License-Identifier: MIT
import csv
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from n2k_compare import compare, render_md

class TestCompare(unittest.TestCase):
    def test_observed_does_not_mean_rx_supported(self):
        with tempfile.TemporaryDirectory() as directory:
            d = Path(directory)
            log = d / "capture.log"
            log.write_text("(1502979132.106111) can0 09F11223#0102030405060708\n"
                           "(1502979132.206111) can0 09F11224#0102030405060708\n"
                           "malformed line\n", encoding="utf-8")
            matrix = d / "matrix.csv"
            with matrix.open("w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["pgn","description","garmin_gnx20_rx","garmin_gnx20_tx"])
                writer.writerow([127250,"Heading","documented","not_listed"])
                writer.writerow([130306,"Wind","documented","not_listed"])
            report = compare(log, matrix, "garmin_gnx20", [35])
            self.assertEqual(report["parsed_frames"], 2)
            self.assertEqual(report["ignored_lines"], 1)
            heading = next(x for x in report["rows"] if x["pgn"] == 127250)
            self.assertEqual(heading["frames_observed_any_source"], 2)
            self.assertEqual(heading["frames_observed_dut_source"], 1)
            self.assertEqual(heading["manual_rx"], "documented")
            self.assertIn("does not prove", render_md(report))

if __name__ == "__main__":
    unittest.main()
