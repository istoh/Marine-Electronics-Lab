# NMEA 2000 automated bench — phase 1

**Status: implementation committed, hardware not tested.** This phase is entirely offline and never opens a CAN interface.

## Pipeline

1. Isolated test bus with DUT and PiCAN-M; passive SocketCAN capture first.
2. `candump -L can0 > capture.log` on a verified **listen-only** interface, with no live vessel connection.
3. Record DUT screen with a camera. Retain original video, frame rate, exposure settings and timestamps.
4. Annotate `stimulus_sent`, `can_received`, `display_changed` and optional `sync_marker` events in CSV.
5. Use externally **measured** clock offsets to align event timestamps to a common clock.
6. Generate timing JSON; review evidence before deriving any claims.
7. Run the existing PGN comparison and evidence report separately.

## Offline command

```bash
python3 tools/n2k_bench_session.py \
  --session test-plans/examples/n2k-bench-session.template.json \
  --events test-plans/examples/n2k-bench-events.template.csv \
  --out session-report.json
python3 -m unittest discover -s tools/tests -v
```

Templates contain placeholders and no observations. Supply actual events before running.

## Clock domains and measurement uncertainty

- `stimulus_sent`: preferably monotonic timestamp captured by the transmitting test host at frame dispatch. Dispatch is not necessarily on-wire transmission.
- `can_received`: host timestamp when a frame is captured; account for hardware/kernel/user-space latency.
- `display_changed`: camera frame timestamp marking the visible change; correct for camera timestamp origin, rolling shutter, exposure and frame interval.
- Each event declares its `clock_domain`; `measured_clock_offsets_ns` is a mapping from domain to a reference-clock offset. An unknown offset makes the trial **INCONCLUSIVE**, not zero.
- Repeated measurements and an uncertainty budget are mandatory for publication-quality latency claims.

## Active replay design — intentionally not implemented yet

Use a separate, physically isolated, terminated, fused and current-limited 250 kbit/s test bus. Provide a hardwired transmit-enable control, operator preflight acknowledgement, explicit allowlisted PGNs, rate limits, source-address handling, proper address claim, bus error monitoring and immediate abort. Never connect the replay bus to operational navigation/autopilot/engine/safety devices. A future replay tool must start in dry-run mode.

## Current limits

- No camera capture or computer vision is automated yet: display-change events are manually annotated.
- No active PGN generator/transmitter is present.
- A timestamp calculation is **not** a verified display latency measurement without calibration and evidence review.
- The session script does not establish DUT identity or NMEA 2000 protocol compliance.
