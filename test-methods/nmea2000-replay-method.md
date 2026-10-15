# MEL-N2K — NMEA 2000 bench test method

Status: DRAFT / NOT EXECUTED
Date: 2026-10-15

## Purpose
Repeatably test instrument reception, source arbitration, loss handling, latency and behavior under controlled NMEA 2000 traffic. This is a research method, not NMEA certification.

## Safety boundaries
- **Never transmit test traffic onto a vessel's live navigation network.**
- Phase A: offline log analysis only; Phase B: listen-only isolated CAN; Phase C: active replay only on an isolated, correctly terminated, current-limited test bus.
- Do not connect autopilot, engine control, alarms, VHF/AIS safety devices or other operational equipment to active test bus.
- Verify interface voltage, CAN transceiver suitability, isolation, NMEA 2000 network power, connector pinout and common-mode limits before connecting.
- PiCAN-M physical interface and power topology must be confirmed from the actual hardware revision/manual.
- Any active replay requires a human enable step, preflight checklist and clearly marked test-only hardware.

## Bench architecture
Raspberry Pi 4B + PiCAN-M -> SocketCAN (listen-only initially) -> isolated CAN bench bus -> device under test (DUT). Separate regulated, fused 12 V bench supply for NMEA 2000 bus/DUT where required. 120 ohm termination at both physical bus ends; measure about 60 ohms across CAN-H/L only with power disconnected and if no other loads affect measurement.

## Reproducibility
Record DUT model, serial pseudonym, hardware/firmware, manual revision, interface hardware, Linux kernel, bitrate, network power, topology, termination, clock sync, ambient conditions, source captures, SHA-256 and test operator.

## Stages
1. Offline: analyze saved candump captures and generate deterministic reports.
2. Passive: record startup, address claim, product information and PGN frequencies.
3. Isolated active: valid PGNs, SID/instance/source changes, missing data and recovery.
4. Edge cases: unavailable field encodings, malformed fast packets, source address conflicts; require separate approval.
5. Performance: repeat timing with synchronized video/photodiode when appropriate, report distributions and uncertainty.

## Required observations
PGN and direction, source address, device/system instance when available, update interval, missing data behavior, alarms, display state, data source chosen, measured response delay, raw log and video evidence.

## Test IDs
- MEL-N2K-001: valid PGN input and displayed field mapping
- MEL-N2K-002: dual source and source loss/failover
- MEL-N2K-003: missing, unavailable, invalid and stale values
- MEL-N2K-004: startup, address claim and fast-packet handling
- MEL-N2K-005: bus load, update rate and latency

## Acceptance criteria
Criteria must be set *before* executing each test from an explicit requirement, documented manufacturer claim or independently declared editorial benchmark. Record PASS/FAIL/INCONCLUSIVE and deviations; absence of evidence is not FAIL.
