# Copyright © 2026 Isto Hunttila
# SPDX-License-Identifier: MIT
"""Regression tests for Android instrument video analysis."""
import csv
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from android_video_changes import analyze_video, detect_frame_states, validate_roi

class AndroidVideoChangesTests(unittest.TestCase):
    def test_roi(self):
        self.assertEqual(validate_roi((2, 3, 10, 5), 20, 20), (2, 3, 10, 5))
        with self.assertRaises(ValueError):
            validate_roi((15, 3, 10, 5), 20, 20)

    def test_stable_step_and_glitch(self):
        class Frame:
            def __init__(self, value):
                self.value = value
            def copy(self):
                return Frame(self.value)
        frames = [(i*40, Frame(v), Frame(v)) for i, v in
                  enumerate([0, 0, 1, 1, 1, 0, 1, 1, 2, 2, 2])]
        with patch("android_video_changes.change_score",
                   side_effect=lambda baseline, current, cv2: abs(baseline.value-current.value)*20):
            events = list(detect_frame_states(frames, 10, 2, 0, None))
        self.assertEqual([x[0] for x in events], [80, 200, 320])

    def test_transient_rejected(self):
        class Frame:
            def __init__(self, value):
                self.value = value
            def copy(self):
                return Frame(self.value)
        frames = [(i*40, Frame(v), Frame(v)) for i, v in enumerate([0, 0, 1, 0, 0])]
        with patch("android_video_changes.change_score",
                   side_effect=lambda baseline, current, cv2: abs(baseline.value-current.value)*20):
            self.assertEqual(list(detect_frame_states(frames, 10, 2, 0, None)), [])

    def test_synthetic_video(self):
        try:
            import cv2
            import numpy as np
        except ImportError:
            self.skipTest("OpenCV/numpy not installed")
        with tempfile.TemporaryDirectory() as tmp:
            video = Path(tmp) / "synthetic.avi"
            writer = cv2.VideoWriter(str(video), cv2.VideoWriter_fourcc(*"MJPG"), 25, (80, 60))
            if not writer.isOpened():
                self.skipTest("MJPG encoder unavailable")
            for value in [0]*5 + [255]*6 + [0]*6:
                writer.write(np.full((60, 80, 3), value, dtype=np.uint8))
            writer.release()
            result = analyze_video(video, (5, 5, 60, 40), 15, 2, 0,
                                   Path(tmp) / "out", "trial-001", "android_video_pts")
            self.assertEqual(result["detected_events"], 2)
            with (Path(tmp) / "out/events.csv").open(newline="") as stream:
                rows = list(csv.DictReader(stream))
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0]["event_type"], "display_changed")

if __name__ == "__main__":
    unittest.main()
