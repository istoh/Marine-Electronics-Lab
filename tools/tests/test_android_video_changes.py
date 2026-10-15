# Copyright © 2026 Isto Hunttila
# SPDX-License-Identifier: MIT
"""Unit tests for offline Android video event detection."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from android_video_changes import detect_scores, detect_frame_states, validate_roi
from unittest.mock import patch

class AndroidVideoChangesTests(unittest.TestCase):
    def test_roi(self):
        self.assertEqual(validate_roi((2, 3, 10, 5), 20, 20), (2, 3, 10, 5))
        with self.assertRaises(ValueError):
            validate_roi((15, 3, 10, 5), 20, 20)
        with self.assertRaises(ValueError):
            validate_roi((0, 0, 0, 5), 20, 20)

    def test_confirmation_and_rearm(self):
        samples = [(0, 0), (40, 20), (80, 22), (120, 25),
                   (160, 0), (200, 20), (240, 21)]
        self.assertEqual([x[0] for x in detect_scores(samples, 10, 2, 0)],
                         [40, 200])

    def test_minimum_gap(self):
        samples = [(0, 0), (40, 20), (80, 20), (120, 0),
                   (160, 20), (200, 20), (240, 0), (400, 20), (440, 20)]
        self.assertEqual([x[0] for x in detect_scores(samples, 10, 2, 200)],
                         [40, 400])

    def test_short_spike_ignored(self):
        self.assertEqual(detect_scores([(0, 0), (40, 30), (80, 0)], 10, 2, 0), [])

    def test_nonmonotonic_time(self):
        with self.assertRaises(ValueError):
            detect_scores([(100, 1), (90, 1)], 10, 1, 0)

    def test_single_step_change_remains_detectable(self):
        class Frame:
            def __init__(self, value):
                self.value = value
            def copy(self):
                return Frame(self.value)
        frames = [(i * 40, Frame(value), Frame(value))
                  for i, value in enumerate([0, 0, 1, 1, 1, 1, 2, 2, 2])]
        with patch("android_video_changes.change_score",
                   side_effect=lambda baseline, current, cv2: abs(baseline.value-current.value)*20):
            events = detect_frame_states(frames, 10, 2, 0, None)
        self.assertEqual([event[0] for event in events], [80, 240])

    def test_one_frame_glitch_rejected(self):
        class Frame:
            def __init__(self, value):
                self.value = value
            def copy(self):
                return Frame(self.value)
        frames = [(i * 40, Frame(value), Frame(value))
                  for i, value in enumerate([0, 0, 1, 0, 0, 0])]
        with patch("android_video_changes.change_score",
                   side_effect=lambda baseline, current, cv2: abs(baseline.value-current.value)*20):
            self.assertEqual(detect_frame_states(frames, 10, 2, 0, None), [])

    def test_invalid_threshold(self):
        with self.assertRaises(ValueError):
            detect_scores([(0, 1)], float("nan"), 1, 0)

if __name__ == "__main__":
    unittest.main()
