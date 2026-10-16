#!/usr/bin/env python3
# Copyright © 2026 Isto Hunttila
# SPDX-License-Identifier: MIT
"""Offline Android instrument display state-change detector (read-only)."""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

def validate_roi(roi, width, height):
    if len(roi) != 4 or any(type(v) is not int for v in roi):
        raise ValueError("ROI must contain four integers")
    x, y, w, h = roi
    if x < 0 or y < 0 or w <= 0 or h <= 0 or x+w > width or y+h > height:
        raise ValueError("ROI outside video frame")
    return roi

def change_score(a, b, cv2):
    a = cv2.GaussianBlur(cv2.cvtColor(a, cv2.COLOR_BGR2GRAY), (5, 5), 0)
    b = cv2.GaussianBlur(cv2.cvtColor(b, cv2.COLOR_BGR2GRAY), (5, 5), 0)
    return float(cv2.mean(cv2.absdiff(a, b))[0])

def detect_frame_states(frames, threshold, consecutive, min_gap_ms, cv2):
    """Yield (candidate onset ms, score, evidence frame) for stable new states.

    Frames is an iterator of (presentation ms, BGR ROI, BGR full frame).
    Only the accepted baseline and pending candidate are retained.
    """
    if not math.isfinite(threshold) or threshold <= 0 or type(consecutive) is not int or consecutive < 1 or not math.isfinite(min_gap_ms) or min_gap_ms < 0:
        raise ValueError("Invalid detection parameters")
    baseline, candidate, streak = None, None, 0
    last_confirmed, previous_time = -math.inf, -math.inf
    first_time, distinct_times = None, False
    for timestamp, roi, full_frame in frames:
        if not math.isfinite(timestamp) or timestamp < previous_time:
            raise ValueError("Non-monotonic or invalid video timestamp")
        previous_time = timestamp
        if first_time is None:
            first_time = timestamp
        elif timestamp != first_time:
            distinct_times = True
        if baseline is None:
            baseline = roi.copy()
            continue
        score = change_score(baseline, roi, cv2)
        if score < threshold:
            candidate, streak = None, 0
            continue
        if streak == 0:
            candidate = (timestamp, score, full_frame.copy())
        streak += 1
        if streak >= consecutive and timestamp - last_confirmed >= min_gap_ms:
            yield candidate
            last_confirmed = timestamp
            baseline = roi.copy()
            candidate, streak = None, 0
    if first_time is not None and not distinct_times:
        raise ValueError("No usable video presentation timeline")

def analyze_video(video, roi, threshold, consecutive, min_gap_ms, output, trial_id, clock_domain):
    try:
        import cv2
    except ImportError as exc:
        raise RuntimeError("Install opencv-python") from exc
    capture = cv2.VideoCapture(str(video))
    if not capture.isOpened():
        raise ValueError("Cannot open video")
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    (output / "evidence").mkdir(exist_ok=True)
    frame_count = 0
    fps = capture.get(cv2.CAP_PROP_FPS)
    def decoded():
        nonlocal frame_count
        while True:
            ok, frame = capture.read()
            if not ok:
                break
            if frame_count == 0:
                validate_roi(roi, frame.shape[1], frame.shape[0])
            timestamp = float(capture.get(cv2.CAP_PROP_POS_MSEC))
            x, y, w, h = roi
            frame_count += 1
            yield timestamp, frame[y:y+h, x:x+w], frame
    events = []
    try:
        for number, (timestamp, score, frame) in enumerate(detect_frame_states(decoded(), threshold, consecutive, min_gap_ms, cv2), 1):
            evidence = f"evidence/display-change-{number:04d}.png"
            if not cv2.imwrite(str(output / evidence), frame):
                raise IOError("Cannot write evidence image")
            events.append(dict(event_id=f"video-change-{number:04d}", trial_id=trial_id,
                               event_type="display_changed", timestamp_ns=str(round(timestamp * 1_000_000)),
                               clock_domain=clock_domain, evidence_ref=evidence))
    finally:
        capture.release()
    if frame_count < 2:
        raise ValueError("At least two frames required")
    columns = ["event_id", "trial_id", "event_type", "timestamp_ns", "clock_domain", "evidence_ref"]
    with (output / "events.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerows(events)
    metadata = dict(schema_version="1.0", video=str(video), video_sha256=sha256(video),
                    roi_xywh=list(roi), threshold=threshold, consecutive=consecutive,
                    min_gap_ms=min_gap_ms, decoded_frames=frame_count, nominal_fps=fps,
                    detected_events=len(events), clock_domain=clock_domain, processing_mode="streaming",
                    timestamp_semantics="OpenCV presentation time, not verified exposure time",
                    caution="Candidate changes only; no measured CAN synchronization or latency")
    (output / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    return metadata

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--video", required=True, type=Path)
    parser.add_argument("--roi", nargs=4, type=int, required=True, metavar=("X", "Y", "W", "H"))
    parser.add_argument("--threshold", type=float, default=12)
    parser.add_argument("--consecutive", type=int, default=2)
    parser.add_argument("--min-gap-ms", type=float, default=300)
    parser.add_argument("--trial-id", default="trial-001")
    parser.add_argument("--clock-domain", default="android_video_pts")
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(analyze_video(args.video, tuple(args.roi), args.threshold,
                                       args.consecutive, args.min_gap_ms, args.out,
                                       args.trial_id, args.clock_domain), indent=2))
    except (ValueError, RuntimeError, IOError) as exc:
        parser.error(str(exc))

if __name__ == "__main__":
    main()
