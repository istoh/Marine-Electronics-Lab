<!-- Copyright © 2026 Isto Hunttila -->
<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Android instrument video change detection

**Status:** prototype; synthetic MJPG video test run locally on 2026-10-16 (2/2 expected transitions detected). No real Android capture or synchronized NMEA 2000 bench validation yet.

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

- This prototype compares each ROI against the last accepted stable baseline. A single display transition that remains stable can be confirmed after the configured number of frames. Very brief changes, animations, reflections, autofocus and moving camera may still cause missed or false detections.
- The detector's `consecutive` confirmation requires a sustained new state relative to the accepted baseline. A candidate onset is retrospective; it is not a measured exposure time. **Do not use for latency measurements until real-video timestamp and clock synchronization validation is complete.**
- Event timestamps mark the first threshold-crossing sample; confirmation occurs later. Report uncertainty due to frame interval, exposure, display refresh and detection logic.
- Planned improvements: direct container PTS inspection for variable frame rate; explicit synchronization-marker workflow; ROI presets, camera-motion compensation and visual calibration.

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

## Synthetic test evidence (2026-10-16)
A local 17-frame MJPG AVI at 25 fps was generated with grayscale levels 0 (5 frames), 255 (6 frames), and 0 (6 frames). With ROI (5,5,60,40), threshold 15, consecutive 2, and gap 0 ms, the detector reported two candidate transitions at presentation times 200 ms and 440 ms, matching the two programmed state changes. This is a functional integration smoke test only; it does not validate Android VFR footage, capture exposure timestamps, or physical instrument latency.
