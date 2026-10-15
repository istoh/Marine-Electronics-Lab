<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- Copyright © 2026 Isto Hunttila -->
# NMEA 2000 bench preflight checklist

Status: DRAFT. Never use on an operational vessel bus.

- [ ] Device under test, firmware and source manual revision identified
- [ ] All active bus devices are non-operational test equipment
- [ ] Physical network isolated from the vessel network
- [ ] PiCAN-M revision, CAN voltage levels and NMEA 2000 pinout verified
- [ ] Bench power fused and current limited; supply polarity verified
- [ ] Correct termination and cable topology checked with power off
- [ ] CAN bitrate confirmed (NMEA 2000 nominal 250 kbit/s)
- [ ] SocketCAN interface starts in listen-only mode for passive work
- [ ] Logging path, UTC time and sufficient disk space checked
- [ ] Test case, expected behavior and abort conditions approved
- [ ] Active transmit enable requires deliberate operator confirmation
- [ ] Evidence: capture, DUT display recording and configuration snapshot

Stop immediately on unexpected network activity, supply current, device resets, errors or wiring temperature rise.
