#!/usr/bin/env python3
# Copyright © 2026 Isto Hunttila
# SPDX-License-Identifier: MIT
"""Offline, read-only instrument display change detection from Android videos.

Video presentation time is NOT a synchronized camera capture timestamp.
No latency is inferred without independent clock alignment.
"""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

def validate_roi(roi, width, height):
    x, y, w, h = roi
    if any(type(v) is not int for v in roi) or min(x, y) < 0 or min(w, h) <= 0:
        raise ValueError("ROI must be nonnegative x,y and positive width,height integers")
    if x + w > width or y + h > height:
        raise ValueError("ROI exceeds video frame dimensions")
    return roi

def change_score(previous, current, cv2):
    """Mean absolute difference after grayscale conversion and mild blur."""
    a = cv2.GaussianBlur(cv2.cvtColor(previous, cv2.COLOR_BGR2GRAY), (5, 5), 0)
    b = cv2.GaussianBlur(cv2.cvtColor(current, cv2.COLOR_BGR2GRAY), (5, 5), 0)
    return float(cv2.mean(cv2.absdiff(a, b))[0])

def detect_scores(samples, threshold, consecutive, min_gap_ms):
    """Confirm a stable new state relative to the last accepted baseline.

    Samples are (timestamp_ms, score_to_baseline). On detection the caller
    must update its image baseline; this pure helper operates on score series
    and rearms when scores return below threshold.
    """
    if not (math.isfinite(threshold) and threshold > 0):
        raise ValueError("threshold must be positive and finite")
    if type(consecutive) is not int or consecutive < 1 or not math.isfinite(min_gap_ms) or min_gap_ms < 0:
        raise ValueError("invalid confirmation or gap")
    result, streak, onset, armed, last = [], 0, None, True, -math.inf
    previous_time = -math.inf
    for timestamp_ms, score in samples:
        if not (math.isfinite(timestamp_ms) and math.isfinite(score)):
            raise ValueError("Non-finite sample")
        if timestamp_ms < previous_time:
            raise ValueError("Non-monotonic presentation timestamps")
        previous_time = timestamp_ms
        if score >= threshold:
            if streak == 0:
                onset = timestamp_ms
            streak += 1
            if armed and streak >= consecutive and onset - last >= min_gap_ms:
                result.append((onset, score))
                last, armed = onset, False
        else:
            streak, onset, armed = 0, None, True
    return result


def detect_frame_states(frames, threshold, consecutive, min_gap_ms, cv2):
    """Compare frames against the last accepted stable state, not adjacent frames.

    frames: iterable of (presentation_ms, BGR ROI, full_frame).
    Returns (onset_ms, score, full_frame) candidate changes.
    """
    if not (math.isfinite(threshold) and threshold > 0):
        raise ValueError("threshold must be positive and finite")
    if type(consecutive) is not int or consecutive < 1 or not math.isfinite(min_gap_ms) or min_gap_ms < 0:
        raise ValueError("invalid confirmation or gap")
    baseline = None
    candidate = None
    streak = 0
    last_event = -math.inf
    previous_time = -math.inf
    events = []
    for timestamp, roi, full_frame in frames:
        if not math.isfinite(timestamp) or timestamp < previous_time:
            raise ValueError("Invalid or non-monotonic video timestamp")
        previous_time = timestamp
        if baseline is None:
            baseline = roi.copy()
            continue
        score = change_score(baseline, roi, cv2)
        if score < threshold:
            streak = 0
            candidate = None
            continue
        if streak == 0:
            candidate = (timestamp, score, full_frame.copy())
        streak += 1
        if streak >= consecutive and timestamp - last_event >= min_gap_ms:
            events.append(candidate)
            last_event = timestamp
            baseline = roi.copy()
            streak = 0
            candidate = None
    return events

def analyze_video(video, roi, threshold, consecutive, min_gap_ms, output, trial_id, clock_domain):
    try:
        import cv2
    except ImportError as exc:
        raise RuntimeError("OpenCV required: pip install opencv-python") from exc
    capture = cv2.VideoCapture(str(video))
    if not capture.isOpened():
        raise ValueError("Cannot open video")
    output.mkdir(parents=True, exist_ok=True)
    frames = output / "evidence"
    frames.mkdir(exist_ok=True)
    samples, image_refs = [], []
    prev = None
    index = 0
    width = height = None
    fps = capture.get(cv2.CAP_PROP_FPS)
    try:
        while True:
            ok, frame = capture.read()
            if not ok:
                break
            if width is None:
                height, width = frame.shape[:2]
                validate_roi(roi, width, height)
            timestamp = float(capture.get(cv2.CAP_PROP_POS_MSEC))
            if not math.isfinite(timestamp) or timestamp < 0:
                raise ValueError("Invalid video presentation timestamp")
            x, y, w, h = roi
            cropped = frame[y:y+h, x:x+w]
            if prev is not None:
                score = change_score(prev, cropped, cv2)
                samples.append((timestamp, score))
                image_refs.append((index, frame.copy()))
            prev = cropped.copy()
            index += 1
    finally:
        capture.release()
    if index < 2:
        raise ValueError("At least two frames required")
    if len(frames_for_analysis) > 1 and all(t == frames_for_analysis[0][0] for t, _, _ in frames_for_analysis):
        raise ValueError("Video decoder returned no usable presentation timeline")
    changes = detect_frame_states(frames_for_analysis, threshold, consecutive, min_gap_ms, cv2)
    events = []
    for number, (timestamp, score) in enumerate(changes, 1):
        sample_index = next(i for i, (t, _) in enumerate(samples) if t == timestamp)
        frame_number, frame = image_refs[sample_index]
        evidence = f"evidence/display-change-{number:04d}.png"
        if not cv2.imwrite(str(output / evidence), frame):
            raise IOError("Could not write evidence frame")
        events.append({
            "event_id": f"video-change-{number:04d}",
            "trial_id": trial_id,
            "event_type": "display_changed",
            "timestamp_ns": str(round(timestamp * 1_000_000)),
            "clock_domain": clock_domain,
            "evidence_ref": evidence,
        })
    columns = ["event_id", "trial_id", "event_type", "timestamp_ns", "clock_domain", "evidence_ref"]
    with (output / "events.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        writer.writerows(events)
    metadata = {
        "schema_version": "1.0", "video": str(video),
        "video_sha256": sha256(video), "roi_xywh": list(roi),
        "threshold": threshold, "consecutive": consecutive, "min_gap_ms": min_gap_ms,
        "decoded_frames": index, "nominal_fps": fps, "detected_events": len(events),
        "clock_domain": clock_domain,
        "timestamp_semantics": "OpenCV video presentation timeline, not verified exposure time",
        "limitations": [
            "Variable frame rate and decoder timestamp accuracy require independent validation",
            "Camera movement, autoexposure, reflections and animations may trigger false changes",
            "No synchronization with CAN timestamps; do not compute end-to-end latency without measured offsets",
            "Frame evidence is from the first candidate state sample; onset uncertainty includes frame interval",
            "A display change is not automatically a validated instrument value change",
        ],
    }
    (output / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    return metadata

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--video", type=Path, required=True)
    parser.add_argument("--roi", type=int, nargs=4, metavar=("X", "Y", "W", "H"), required=True)
    parser.add_argument("--threshold", type=float, default=12.0)
    parser.add_argument("--consecutive", type=int, default=2)
    parser.add_argument("--min-gap-ms", type=float, default=300.0)
    parser.add_argument("--trial-id", default="trial-001")
    parser.add_argument("--clock-domain", default="android_video_pts")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    try:
        report = analyze_video(args.video, tuple(args.roi), args.threshold,
                               args.consecutive, args.min_gap_ms, args.out,
                               args.trial_id, args.clock_domain)
    except (ValueError, RuntimeError, IOError) as exc:
        parser.error(str(exc))
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
