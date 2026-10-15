<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- Copyright © 2026 Isto Hunttila -->
# NMEA 2000 instrument compatibility matrix — initial extraction (2026-10-15)

## Scope and confidence

This is a **documentation matrix, not a bench-tested interoperability certification**. Directly extracted RX/TX PGN sets are available for Garmin GNX 20/21 installation instructions and Furuno FI-70 operator manual. B&G Triton² and Simrad IS42 manuals include RX/TX appendices, but their exact tables still require extraction. Raymarine i70s and nke Multigraphic II need model-specific verification.

**Never interpret `not_listed` as confirmed lack of support.** It means absent from the particular published list. `pending_extraction` means not assessed.

## Sources
- Garmin GNX 20/21 installation instructions, NMEA 2000 PGN Information: https://static.garmin.com/pumac/GNX_20_21_Install_Instructions_EN.pdf
- Furuno FI-70 operator manual, Specifications of Color Instrument / Input-Output PGNs: https://www.furuno.it/docs/OPERATOR_MANUAL/FI70_OME-H.pdf
- B&G Triton² operator manual (software 1.0), appendix index: https://www.manualslib.com/manual/1224005/BAndg-Triton2.html
- Simrad IS42 operator manual, appendix index: https://www.manualslib.com/manual/3177426/Simrad-Is42.html
- Raymarine i70s installation instructions (not a device-specific PGN matrix): https://docs.raymarine.com/87420/en-US/latest/index.html
- nke Multigraphic II manual V2.0 index: https://www.manualslib.fr/manual/1017211/Nke-Multigraphic-Ii.html

**Important:** Raymarine's generic online PGN support tables for other products (e.g. documents 81406 or 87472) must not be assigned to i70s without model-specific proof.

## Initial comparisons
- GNX 20 explicitly receives 128259 (speed through water), 128267 (depth), 127250 (heading), 130306 (wind), 129025/129026/129029 (GNSS), 129283/129284/129285 (navigation) and 127508 (battery status).
- FI-70 explicitly receives the same core wind/depth/speed/heading/navigation groups, and lists multiple AIS and engine-related PGNs.
- Both devices have control/administration traffic in addition to instrument-data traffic.
- FI-70 has more listed receive PGNs than GNX 20 in these specific manual editions. This **does not establish better interoperability** without tests of fields, instances, sources, freshness, errors and firmware versions.
- Some Furuno PGNs in the 1308xx range and PGN 65280 may be vendor-specific; do not assume interoperability from a number alone.

## Required validation
1. Resolve manual editions and document hashes, and cite exact pages.
2. Extract Triton² and IS42 RX/TX appendix tables, independently validate transcription.
3. Obtain i70s-specific and nke-specific PGN evidence.
4. Normalize leading zeros and NMEA PGN naming, verify proprietary groups and obsolete PGNs.
5. For each documented receive PGN, test individual fields, SID, instances, data source selection, missing data, invalid values, timeouts and update rates.
6. Log test equipment, firmware, bus load and raw CAN captures; record deviations and uncertainty.

## Candidate replay tests
- MEL-N2K-001: standard valid PGN replay and displayed field verification.
- MEL-N2K-002: competing data sources, source address changes, device and system instances.
- MEL-N2K-003: invalid/out-of-range/unavailable field encodings and loss/recovery.
- MEL-N2K-004: fast-packet behavior, timing, PGN request and address claim.
- MEL-N2K-005: simultaneous traffic, bus load and display update latency.

No hardware measurements have been performed.
