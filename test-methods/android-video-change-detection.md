<!-- Copyright © 2026 Isto Hunttila -->
<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Android instrument video change detection

**Status:** prototype; no real Android capture or synchronized NMEA 2000 bench validation yet.

## Setup

```bash
python3 -m pip install opencv-python
python3 tools/android_video_changes.py \
  --video android-recording.mp4 \
  --roi 150 120 480 240 \
  --threshold 12 --consecutive 2 --min-gap-ms 300 \
  --trial-id trial-001 --out test-results/android-trial-001
```

ROI is `X Y WIDTH HEIGHT` in decoded video pixels. Choose an area containing only the changing numeric readout where possible. Stabilize the phone and lock exposure/focus if available. Do not use the example ROI without inspecting the actual video.

Output: `events.csv` with `display_changed` events compatible with `n2k_bench_session.py`, `metadata.json` with video SHA-256 and analysis parameters, and `evidence/` PNG frames. Keep the original MP4 unchanged. A zero-event CSV contains a header only; `n2k_bench_session.py` currently requires at least one event, so do not feed an empty CSV to it.

**Critical:** OpenCV `CAP_PROP_POS_MSEC` is a decoder-reported presentation timeline, not a verified exposure timestamp or clock synchronized to Raspberry Pi CAN captures. Variable-frame-rate Android recordings require timestamp verification (e.g. with container PTS extraction), especially before quantitative latency reporting. Without independently measured offsets, latency results must remain INCONCLUSIVE. Image differences are only candidate changes, not proof of a specific instrument value.

## Limitations and follow-ups

- This prototype compares each frame against the immediately preceding frame. Very brief changes, animations, reflections, autofocus and moving camera may cause missed or false detections.
- The detector's `consecutive` confirmation requires sustained frame-to-frame change. A display that switches once and then stays stable may only create one high-score sample and be missed. **Do not use for latency measurements until an improved baseline/state detector is implemented and validated.**
- Event timestamps mark the first threshold-crossing sample; confirmation occurs later. Report uncertainty due to frame interval, exposure, display refresh and detection logic.
- Planned improvements: baseline/state comparison with hysteresis; direct container PTS inspection for variable frame rate; explicit synchronization-marker workflow; synthetic-video integration tests; ROI presets and visual calibration.

## Configuration tickets

- MEL-CFG-CAM-006: ROI per device and display mode.
- MEL-CFG-CAM-007: Change threshold, temporal confirmation and rearm rules.
- MEL-CFG-CAM-008: Video timeline validation, frame-time uncertainty and clock domain.
- MEL-CFG-CAM-009: Evidence storage and privacy/retention settings.

## Test

```bash
python3 -m unittest discover -s tools/tests -p 'test_android_video_changes.py' -v
```

No real hardware or phone video test is claimed.
