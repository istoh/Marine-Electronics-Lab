<!-- Copyright © 2026 Isto Hunttila -->
<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Nexus multi-observer instrument test plan (spring 2027)

**Status:** planning only. Boat is ashore for winter; no spring measurements have been performed. Exact Nexus instrument models, Windows software/version, connection topology, manual editions, and available loan equipment must be confirmed before test execution.

## Objective

Capture one controlled stimulus simultaneously through (1) bus/protocol recording, (2) Nexus Windows application and (3) an Android camera viewing the physical instrument. Compare observable values, display state transitions, update rates, behavior under faults and repeatability. Do not infer clock alignment from coincident events.

## Documentation inventory before tests

For **each exact instrument model and firmware**, record manual title, manufacturer URL, revision, pages, screenshots or descriptions and evidence status for every menu item: pages/display modes, units, calibration, damping, alarms, sources, brightness, diagnostics, resets and firmware information. Do not assume menu equivalence across Nexus generations.

For **each Nexus Windows software release**, record exact product name, version, supported hardware/interface, user manual, menu hierarchy, controls, calibration functions, logs/export format, configuration read/write behavior, and automation feasibility. Determine whether it is NX2 Race Software, Nexus Race Software, a configuration utility, or another application before documenting its actual menus. Mark all unverified menu items as **TO_VERIFY**, not facts.

Recommended inventory columns: product,model,firmware_or_version,menu_path,setting_or_action,allowed_values,default,readable,writable,persistence,protocol_effect,manual_url,manual_page,evidence_status,test_case_id.

## Automation design

- Windows controller: prefer official API/CLI or documented file export if available; otherwise inspect Windows UI Automation with Python `pywinauto`; image-based `pyautogui` only as a fallback.
- Identify window/control selectors by application version. Detect modal dialogs, errors and loss of connection; never silently continue after failed commands.
- Store the command issued, acknowledgement or observed UI state, screenshots, monotonic and wall-clock timestamps, and software version.
- Capture bus traffic read-only on isolated bench. Protocol-specific adapters are required: Nexus FDX is not NMEA 2000 and cannot be connected directly to CAN.
- Record Android original MP4, ROI, video hash, video presentation timestamps and evidence frames. Camera/video timestamps are not exposure timestamps.
- Add a physical synchronization marker visible to camera and captured by the acquisition system; independently measure offsets and uncertainty before computing cross-device latency.
- Keep automation safe: no autopilot actuation or live vessel control; verify effects of calibration writes, factory resets and firmware updates before enabling.

## Test matrix

1. Power-up, discovery, firmware identification, shutdown and recovery.
2. Every documented instrument page and menu entry: navigation, editability, persistence after power cycle, and screen behavior.
3. Units and numerical formatting: knots, m/s, depth units, degrees, wraparound, missing/invalid values.
4. Sensor source selection, data dropout, stale data, multiple conflicting sources and recovery.
5. Damping/filtering, refresh interval, response to step and ramp input, quantization and rounding.
6. Alarm limits, hysteresis, acknowledgement and fault indications.
7. Calibration: backup, change, verification and restore; destructive actions require separate authorization.
8. Windows app vs physical instrument: matching values, changes, discrepancies, configuration write/readback and logs.
9. NMEA 2000/0183/Nexus FDX gateway translation where documented and physically supported; capture both sides.
10. Repeatability across instrument models, firmware versions and ambient lighting.

Each test records DUT, wiring, supply voltage, stimuli, expected behavior/source, actual observations, raw logs, hashes, PASS/FAIL/INCONCLUSIVE, and limitations. Treat unsupported/unverified functions as NOT_RUN, not FAIL.

## Portable bench hardware

**Recommendation:** build a reusable electrically protected base/power-and-logging case plus **interchangeable instrument front panels** or instrument-specific small cases. A dedicated case per instrument family makes sense only after the loaned devices, connector geometry, power needs and cable pinouts are known.

Possible construction: plywood or aluminum removable panel with documented cutouts; mounting screws and strain relief; instrument face visible to a fixed camera mount; protected DC power input; labeled fuse per circuit; terminal distribution; emergency power disconnect; accessible connectors and test points; clearly separated bus networks and sensor leads; cable glands; spare blank panel. Avoid assuming all instruments use 12 V or identical polarity/pinouts. Do not route unknown sensor power into the shared bus.

Keep a wiring diagram, connector pinout verification, supply-current budget, fuse calculation, termination check, grounding/isolation plan, BOM, panel drawing and photos for each configuration. Use detachable harnesses so loaned instruments can be returned unmodified. No permanent drilling in loaned devices.

## Winter preparation and spring execution

**Winter:** obtain authoritative manuals and Windows installers/documentation; extract menu inventories; inventory own Nexus devices and connectors; prototype Python Windows GUI control against an available software version; validate synthetic camera transitions; design modular panels and cable harnesses; write repeatable test scripts and dry-run on recorded data.

**Before borrowing:** ask lender for exact model, firmware, accessories, connectors, allowed operations, loan duration and condition photos. Prepare a model-specific test pack and check-in/check-out checklist.

**Spring:** bench electrical inspection and safe power-up, interface discovery, manual spot-check of menu inventories, automated scripted tests with simultaneous logs/video, repeated measurements, signed evidence manifest and equipment return inspection.

## Configuration tickets

- MEL-CFG-NEX-001: model/firmware-specific menu map and selector strategy.
- MEL-CFG-NEX-002: Windows app executable/version, automation backend and UI control selectors.
- MEL-CFG-NEX-003: bus adapters, source addresses, interface channels and sample rates.
- MEL-CFG-NEX-004: camera ROI, exposure/focus and evidence retention.
- MEL-CFG-NEX-005: measured clock offsets, synchronization marker and uncertainty.
- MEL-CFG-NEX-006: supply voltage, per-circuit fuse, connector pinouts and harness revision.
- MEL-CFG-NEX-007: per-test stimulus, tolerance, repetitions and timeout.
- MEL-CFG-NEX-008: permitted write operations and calibration restoration.
