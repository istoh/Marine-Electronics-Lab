<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- Copyright © 2026 Isto Hunttila -->
# Android phone camera for instrument display measurements

**Status:** proposed camera acquisition path, not validated on hardware.

An Android phone is an alternative to a Raspberry Pi camera. The phone records the DUT display while Raspberry Pi + PiCAN-M records CAN frames. Retain original footage, device identity, firmware, frame rate, capture settings, and test-session metadata.

## Phase A — video file import (recommended first)
1. Mount the phone rigidly, facing the display, avoiding glare and automatic screen dimming.
2. Record a video with the phone's normal camera app. Lock focus, exposure and white balance if supported; note variable frame rate and stabilization.
3. Copy the original video unchanged to the analysis machine (USB transfer is acceptable). Hash the original.
4. Extract presentation timestamps from the video container; do **not** assume frame index / nominal FPS equals accurate capture time.
5. Mark a shared visual synchronization event visible in the video and independently logged by the Pi (for example a bench-only LED controlled and timestamped by the Pi). Characterize LED command-to-light delay.
6. Annotate display-change frames, estimate camera exposure and frame interval uncertainty, and enter observations in the existing `n2k-bench-events.template.csv`.
7. Run `tools/n2k_bench_session.py` with independently measured offsets. Do not claim precise latency without calibration.

## Phase B — automated video analysis
- Add OpenCV frame extraction, display ROI configuration, image registration and change-point detection.
- Prefer a clearly bounded region showing one changing numeric value. Ignore reflections, blinking icons, exposure shifts and camera motion.
- Record detected frame PTS, confidence, ROI and a before/after evidence frame.
- Require operator confirmation for every automatic detection before publishing results.
- Report uncertainty: at least frame interval, exposure timing, sync offset and CAN capture timestamp latency.

## Phase C — live Android streaming (optional)
Evaluate USB/UVC or IP video transport. Transport latency and buffering are additional unknowns; measure them rather than assuming low latency. A custom Android app could expose frame timestamps and capture metadata, but Android camera sensor timestamps and Pi clock must still be aligned.

## Safety and separation
The phone does not control or transmit on the NMEA 2000 bus. All active test traffic remains a separate, operator-enabled and physically isolated future feature.

## Configuration tickets
- MEL-CFG-CAM-001: camera input mode (offline file / live stream).
- MEL-CFG-CAM-002: display ROI, registration and detection threshold.
- MEL-CFG-CAM-003: frame timing and clock-sync calibration.
- MEL-CFG-CAM-004: camera settings and uncertainty metadata.
- MEL-CFG-CAM-005: synchronization marker source and timing method.

These parameters must be recorded per test session, not silently inferred.
