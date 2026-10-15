# Copyright © 2026 Isto Hunttila
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from n2k_bench_session import analyze

class BenchTimingTests(unittest.TestCase):
    def test_timing_with_measured_offset(self):
        events=[
          {"trial_id":"1","event_type":"stimulus_sent","timestamp_ns":1000000000,"clock_domain":"pi"},
          {"trial_id":"1","event_type":"display_changed","timestamp_ns":1100000000,"clock_domain":"camera"}]
        result=analyze(events,{"pi":0,"camera":10000000})
        self.assertEqual(result["valid_trials"],1)
        self.assertEqual(result["mean_ms"],110.0)
    def test_unsynchronized_is_inconclusive(self):
        events=[
          {"trial_id":"1","event_type":"stimulus_sent","timestamp_ns":1000000000,"clock_domain":"pi"},
          {"trial_id":"1","event_type":"display_changed","timestamp_ns":1100000000,"clock_domain":"camera"}]
        self.assertEqual(analyze(events,{"pi":0})["valid_trials"],0)
    def test_negative_delay_is_inconclusive(self):
        events=[
          {"trial_id":"1","event_type":"stimulus_sent","timestamp_ns":2000000000,"clock_domain":"pi"},
          {"trial_id":"1","event_type":"display_changed","timestamp_ns":1000000000,"clock_domain":"pi"}]
        self.assertEqual(analyze(events,{"pi":0})["valid_trials"],0)
if __name__=="__main__":unittest.main()
