# Marine instrument manual analysis — initial pass (2026-10-15)

**Status:** Preliminary desk research; not a complete page-by-page review of all 35 candidates. The six representative products below have discoverable manuals, manufacturer documentation, or both. No bench tests were performed. Confirm firmware applicability before relying on behavior.

## Source and document status

| Product | Documentation located | Revision information | Limitations |
|---|---|---|---|
| Garmin GNX 20 | Manufacturer technical product page | Manual revision not yet established | Specifications below come from product page, not an inspected manual |
| B&G Triton² | Operator manual indexed by ManualsLib | Manual states software version 1.0; Navico 2016 | Manufacturer-hosted current PDF/revision still to verify |
| Raymarine i70s | Official installation instructions, document 87420 | Official online edition Rev 2; older Rev 1 dated May 2021 | Need separate operation manual and PGN list |
| Simrad IS42 | Operator manual indexed by ManualsLib | Copyright 2016; exact document revision not confirmed | Manufacturer-hosted edition still to verify |
| Furuno FI-70 | Official Furuno operator manual and support page | Pub. OME-72810-H, June 23 2022 indexed; direct URL currently redirects to download terms | Obtain authorized copy via official terms before full extraction |
| nke Multigraphic II | User/installation manual indexed by ManualsLib | V2.0, PF000401 / PF000195 | Official copy and firmware applicability still to verify |

## Confirmed findings with provenance

**Garmin GNX 20** — Manufacturer product specification lists a monochrome 4.0-inch diagonal LCD, IPX7, 9–16 V via NMEA 2000, 0.35 W day / 0.4 W night, and support for NMEA 2000 and NMEA 0183. These are **manufacturer claims**, not measured values. Source: https://www.garmin.com/en-GB/p/126696/

**B&G Triton²** — Operator manual table of contents identifies AIS, autopilot, supported NMEA 2000 transmit/receive PGNs, data page setup and technical specification sections. Manual text says it was written for software version 1.0. Do not infer exact PGNs without extracting the appendix. Source: https://www.manualslib.com/manual/1224005/BAndg-Triton2.html

**Raymarine i70s** — Manufacturer hosts installation instructions document 87420 Rev 2. Firmware/software lifecycle is separately documented by Raymarine for i50/i60/i70s/p70s/SeaTalkng converter/iTC-5. Confirm NMEA 2000 PGNs and SeaTalkng network behavior in the operation and installation manuals. Sources: https://docs.raymarine.com/87420/en-US/latest/index.html and https://www.raymarine.com/en-us/download/seatalk-seatalkng-software

**Simrad IS42** — Operator manual identifies configurable data pages, missing/faulty data behavior, AIS, MOB, autopilot status, and appendices for supported NMEA 2000 transmit/receive PGNs. It also describes calculated speed, wind, trip and set/drift values. Exact PGNs and algorithms need extraction. Source: https://www.manualslib.com/manual/3177426/Simrad-Is42.html

**Furuno FI-70** — Official operator manual identifies compass, speed, engine, graph, highway, rudder, timer, wind and AIS display categories. Furuno's support page provides operator and user handbooks, software history and update procedures. Direct PDF request may redirect to terms of use; do not bypass. Sources: https://www.furunousa.com/en/support/fi70bw and https://www.furuno.com/files/Manual/164/upload/OME72810H_FI70.pdf

**nke Multigraphic II** — Indexed French user/installation manual V2.0 documents page construction, selectable data and installation. Its specific communication protocols, update procedures and source-selection behavior need full manual verification. Source: https://www.manualslib.fr/manual/1017211/Nke-Multigraphic-Ii.html

## Cross-manufacturer observations

1. **Data-page configuration** appears across multiple devices; compare field count, templates, naming, switching and missing-data indications using a common test.
2. **Network interoperability** cannot be reduced to a checkbox saying NMEA 2000. Test the precise PGNs received/transmitted, instance handling, data source arbitration, failure behavior and update rates.
3. **AIS and autopilot integration** is documented for Triton² and IS42, but behavior and prerequisites must be tested with controlled input.
4. **Power and daylight visibility** need measurements under standardized brightness, supply voltage, ambient illumination and temperature. Do not compare brochure values as equivalent tests.
5. **Lifecycle matters:** tie each observation to manual revision, firmware version and hardware variant.

## Priority verification tasks

- Obtain and register licensed copies of manuals and installation instructions for each of the six devices.
- Extract full supported-PGN tables, preserving direction (RX/TX), footnotes and firmware applicability.
- Extract electrical specifications, mounting dimensions, IP rating, display details and operating temperature with page-level citations.
- Document network startup, source selection, missing-data and alarm behavior.
- Produce a requirement-to-test matrix and a standard NMEA 2000 replay test harness.
- Add more vendors and legacy generations only after source quality is controlled.

## Test cases proposed (not executed)

| ID | Goal | Method |
|---|---|---|
| MEL-DISP-001 | Readability | Calibrated ambient lighting and controlled viewing angles |
| MEL-PWR-001 | Power draw | Measure bus current across day/night brightness and supply range |
| MEL-N2K-001 | PGN coverage | Replay known valid PGNs and log rendered fields |
| MEL-N2K-002 | Source arbitration | Two competing sources, varied instances and source loss |
| MEL-N2K-003 | Data loss | Timeout and malformed-data response, alarms and recovery |
| MEL-UI-001 | Configuration | Repeatable page setup and restore test |
| MEL-BOOT-001 | Startup latency | Power-to-first-valid-data timing across repeated boots |

**Research rule:** source-backed documentation facts and manufacturer claims are distinct from independently measured test results.
