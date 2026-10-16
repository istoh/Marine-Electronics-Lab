<!-- Copyright © 2026 Isto Hunttila -->
<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Nexus FDX reverse-engineering and ESP32-S3 GND 10 replacement — research plan

Status: DESIGN ONLY; no hardware captures, firmware verification, or electrical measurements performed. Target bench work spring 2027. Owner: Isto Hunttila. Scope: Marine Electronics Lab, independent of Sysfuser.

## Goals and acceptance gates

A. Reproducible, timestamped passive Nexus FDX capture with raw edge/bit evidence and preserved errors.
B. Decode at least depth, water speed, apparent wind, water temperature with independently verified scale/units and unknown-value handling.
C. Correlate decoded FDX against GND 10 NMEA 2000 PGNs, Windows Nexus Race Software observations and physical instrument video. Avoid interpreting time correlation alone as proof.
D. Produce isolated NMEA 2000 PGNs from an ESP32-S3 in a test CAN network, with proper address claim and device identification.
E. Assess whether gateway is only an FDX listener or must emulate Nexus server behavior; bidirectional configuration/calibration remains a later optional phase.

No promise of drop-in GND 10 replacement until C, D, E pass.

## Independent evidence channels

- FDX bus: passive isolated/protected RS-485 receiver and edge capture / mark-parity-aware byte capture; raw bytes/bits, parity, framing errors, idle periods, bus voltage evidence, local monotonic timestamps.
- NMEA 2000: RPi4B + PiCAN-M SocketCAN capture; raw CAN frames, timestamps, fast-packet reassembly, PGN decode, source address, instance, SID, NA values, transport details.
- Windows: Nexus Race Software UIA inventory and screenshots/video, software build, selected COM port, visible values, configuration state; read-only until approved.
- Physical NX/NX2 displays: fixed camera video, ROI, controlled stimulus annotations, display latency not assumed equal to bus latency.
- Optional GND 10 USB: USBPcap/Wireshark capture of both directions, if interface and driver permit; respect device safety. USB-side format is not assumed identical to NX bus.

Clock domains must be explicitly named. Synchronization requires independent reference event or measured offset and uncertainty; do not use video presentation timestamps as exposure time. Record every clock adjustment.

## Controlled experiments

1. Power-on baseline and idle captures; inventory all device models, firmware, serial identifiers redacted in public data.
2. One controlled variable at a time: depth, water speed, wind angle, wind speed, temperature, heading if present. Record stimulus, stable plateaus, ramp and return to baseline.
3. Boundary/quality cases: zero, negative where meaningful, max/min, missing sensor, disconnected source, timeout, invalid data, restart.
4. Multi-source conflicts and update cadence; observe which Nexus source GND 10 forwards and whether configuration changes source precedence.
5. Repeated runs at several values, with randomized order and a held-out validation run to avoid overfitting.
6. Optional software settings observations; do not apply changes without snapshot, approval and restoration test.

Use synthetic signals or isolated simulator when possible. Never connect experimental CAN transmitters to a live vessel network.

## FDX protocol analysis

Start with independent review of https://github.com/gzahl/nexusfdx and https://github.com/lkarsten/fdxread. Record source revisions, licenses, tested hardware, and evidence; verify all claims on the target Nexus network. Distinguish physical bus, GND 10 USB representation and logical measurements.

Pipeline: raw capture -> edge timing / UART framing hypothesis (9600 8S1 is a candidate from prior code, not verified on target) -> frame boundary / checksum candidates -> field hypotheses -> decoded values -> independent reference correlation -> held-out confirmation. Preserve alternatives and confidence/evidence links.

AI may propose hypotheses, but automatic acceptance requires repeated independent measurements and explicit validation. Compare NMEA 2000 output only after checking PGN source/instance and gateway filters.

## ESP32-S3 hardware prototype

- ESP32-S3 module with USB and Wi-Fi; two independent capture paths as practical.
- High-impedance, protected RS-485 receive-only input; no drive enable, no added termination or bias until bus topology is verified. Prefer galvanic isolation for vessel-connected work.
- Digital edge capture (RMT or equivalent) to preserve ninth/mark bit; UART software framing for decoded stream; timestamp quality characterized under load.
- Optional analog frontend + ADC for voltage/edge shape. Internal ADC is not a substitute for a calibrated oscilloscope. External simultaneous ADC only if measurements justify cost.
- Later CAN: ESP32-S3 TWAI + suitable isolated CAN transceiver and NMEA 2000 power/connector design. No CAN transmit on vessel until independent validation.
- Power: fused, reverse-polarity and transient protection; bench supply first; defined grounds and isolation boundaries.
- Loss reporting: dropped samples, buffer overflow, time discontinuity, Wi-Fi disconnect and storage backpressure counters.
- Prefer local raw storage or reliable USB stream for evidence; Wi-Fi streaming is secondary and must not silently drop data.

## Software deliverables

1. ESP32-S3 passive capture firmware with explicit pin mapping and board profile.
2. Python collector with binary versioned record schema: capture_id, monotonic timestamp, clock_domain, channel, payload/edge, framing flags, drop counters, firmware revision.
3. NMEA 2000 raw capture + decode and evidence cross-link.
4. Windows UIA inventory and screenshot observation scripts (read-only).
5. Offline alignment/visualization, hypothesis generator and validation report with source provenance.
6. ESP32-S3 FDX-to-N2K translator on an isolated bench, with protocol conformance tests.

## Data integrity

Each capture has SHA-256, immutable raw data, test operator, UTC start, independent monotonic clocks, device/software versions, wiring diagram, configuration snapshot, stimulus log, and consent/redaction for serial IDs. Derivative datasets are versioned; no raw data overwritten.

## Safety and uncertainty

Multimeter alone cannot prove safe logic levels, common-mode voltage, spikes, bus polarity, galvanic isolation needs or differential signaling. Use suitable rated oscilloscope/front-end to characterize unknown signals before direct GPIO/ADC connection. USB oscilloscope grounds may be common and earth-referenced through PC; no arbitrary probe-ground attachment to A/B. For RS-485, receiver common-mode range and isolation must be engineered. No bus driving during passive experiments.

## Configuration tickets (create in backlog/issues when implementing)

- MEL-CFG-FDX-001: physical interface, polarity, isolation, receiver pin mapping.
- MEL-CFG-FDX-002: baud, parity/mark bit, stop bits, inversion, edge capture parameters.
- MEL-CFG-FDX-003: capture channels, timestamp source, buffer limits, loss reporting.
- MEL-CFG-FDX-004: storage/USB/Wi-Fi export, capture metadata and privacy.
- MEL-CFG-FDX-005: protocol decoder version, unit mappings, source/instance policy.
- MEL-CFG-FDX-006: N2K device identity, address claim, PGN enables, update periods, instances.
- MEL-CFG-FDX-007: clock sync method and uncertainty.
- MEL-CFG-FDX-008: mode gating: passive capture vs isolated transmit; writes disabled by default.
- MEL-CFG-FDX-009: bench stimulus definitions and source/reference selection.

## Milestones

Winter: research, manual/source inventory, simulator, PC/UI automation, schemas, capture firmware and synthetic tests.
Spring: isolated electrical characterization; passive capture; controlled 4-observer experiments; held-out decoder validation.
After validation: isolated N2K transmission, interoperability testing, replacement feasibility report.

Reference: test-plans/nexus-windows-video-bench-plan.md and test-plans/nexus-gnd10-race-software-menu-inventory.md.
