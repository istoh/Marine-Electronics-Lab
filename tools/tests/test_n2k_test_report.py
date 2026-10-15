import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from n2k_test_report import build, markdown

class ReportTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        d=Path(self.tmp.name)
        self.criteria=d/"criteria.json"
        self.obs=d/"observations.csv"
        self.criteria.write_text(json.dumps({"dut":"Demo instrument","firmware":"1.0",
          "operator":"tester","tests":[
          {"test_id":"T1","pgn":127250,"evaluation":"numeric_tolerance",
           "expected_value":120,"expected_unit":"deg","absolute_tolerance":1},
          {"test_id":"T2","pgn":130306,"evaluation":"numeric_tolerance",
           "expected_value":8,"expected_unit":"m/s","absolute_tolerance":0.5},
          {"test_id":"T3","pgn":128267,"evaluation":"numeric_tolerance",
           "expected_value":3,"expected_unit":"m","absolute_tolerance":0.1}]}),encoding="utf-8")
    def test_pass_inconclusive_not_run(self):
        self.obs.write_text("test_id,pgn,source_address,observed_value,observed_unit,observation_time_utc,evidence_ref,operator\n"
                            "T1,127250,35,120.5,deg,2026-10-15T10:00:00Z,video-001.mp4,tester\n"
                            "T2,130306,35,8,kn,2026-10-15T10:01:00Z,photo-001.png,tester\n",encoding="utf-8")
        report=build(self.criteria,self.obs)
        self.assertEqual(report["counts"]["PASS"],1)
        self.assertEqual(report["counts"]["INCONCLUSIVE"],1)
        self.assertEqual(report["counts"]["NOT_RUN"],1)
        self.assertIn("video-001.mp4",markdown(report))
    def test_fail(self):
        self.obs.write_text("test_id,pgn,source_address,observed_value,observed_unit,observation_time_utc,evidence_ref,operator\n"
                            "T1,127250,35,130,deg,2026-10-15T10:00:00Z,video.mp4,tester\n",encoding="utf-8")
        self.assertEqual(build(self.criteria,self.obs)["counts"]["FAIL"],1)
if __name__=="__main__":
    unittest.main()
