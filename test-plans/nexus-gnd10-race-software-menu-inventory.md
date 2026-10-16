<!-- Copyright © 2026 Isto Hunttila -->
<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Nexus Race Software / GND 10 — verified menu seed

**Evidence status:** Garmin support article documents the following workflow; exact software build and Windows 11 behavior remain unverified.

Primary source: https://support.garmin.com/en-US/?faq=jejY9lLwXm1DwGyj2oawN8
Corroborating Garmin installation instructions: https://static.garmin.com/pumac/GND_10_Install_EN-US.pdf

## Confirmed navigation sequence

1. Connect GND 10 to Windows computer by USB; install driver and Nexus Race Software.
2. Open Nexus Race Software and click **Communication**.
3. Set primary connection to **NX2 FDX server on COM port**, select correct COM port, click OK.
4. Open **Tools → Configure**.
5. Locate **GND 10 NMEA 2000 gateway**.
6. Right-click device and select **Setup**.
7. Garmin's specific troubleshooting workflow says to uncheck every box except **Navigation** and **Position**, then confirm and disconnect. **This is NOT a general default or safe automatic action.** Capture existing state first; perform writes only under a separately approved, model-specific test case.
8. Garmin says GND 10 software earlier than **2.00** cannot be configured with Nexus Race Software until updated.

Garmin article lists Windows Vista–8 for the procedure; Windows 11 behavior and driver signing are **TO_VERIFY**. Do not assume unsupported means impossible.

## Automation sequence (read-only phase)

- Discover Windows COM ports and USB device identity, record driver and software versions.
- Start application, attach to the known COM port, wait for connected state.
- Open Tools → Configure, enumerate devices, capture full-screen evidence.
- Open gateway Setup and record the visible checkbox labels and current states.
- Close Setup without applying changes; disconnect and confirm no persistent settings changed.
- Capture screenshots, logs, error dialogs, monotonic timestamps, application version and SHA-256 hashes.

Use UI Automation/pywinauto only after inspecting actual control tree. A graphical click script without state verification is not sufficient.

## Device and bus matrix

GND 10 connects Nexus FDX and NMEA 2000, and USB to PC. Record separately:
- NMEA 2000 raw PGNs, source addresses, bus topology and termination.
- Nexus FDX behavior as observed through software/compatible interface.
- Windows displayed values and configuration.
- Physical Nexus instrument video with independent timebase.

The gateway direction/source configuration must be recorded for every run. Never assume FDX packets and NMEA 2000 PGNs are identical or that both sides contain every value.

## Follow-up evidence needed

- Nexus Race Software installer, exact version and official manual with full menu hierarchy.
- GND 10 firmware version and driver on the user's Windows machine.
- Instrument models and firmware (NX/NX2/NX displays).
- Bench cable/power diagram and connector verification.
- Approval process and restoration procedure for any write operation.

Configuration tickets: MEL-CFG-NEX-001, MEL-CFG-NEX-002, MEL-CFG-NEX-003, MEL-CFG-NEX-008.
