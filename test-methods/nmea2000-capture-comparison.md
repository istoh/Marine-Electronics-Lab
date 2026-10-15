<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- Copyright © 2026 Isto Hunttila -->
# NMEA 2000 documentation/capture comparison

This tool **does not send CAN messages**. It reads an existing candump log and compares observed PGN identifiers against the repository's manufacturer-documentation matrix.

## Usage

From repository root:

```bash
python3 tools/n2k_compare.py capture.log --device garmin_gnx20 --dut-source 35 --json result.json --markdown result.md
python3 -m unittest discover -s tools/tests -v
```

Omit `--dut-source` if the instrument's source address is unknown. Repeat `--dut-source` for known addresses after an address change. **Source addresses alone do not authenticate device identity**: establish the identity from address claim/product information and controlled bench setup.

## Interpretation

- `documented`: appears in the relevant manual list, not independently verified.
- `not_listed`: not in the consulted manual list; not proof of non-support.
- `pending_extraction`: manufacturer manual PGNs not extracted.
- `observed_on_bus`: one or more CAN frames with that PGN identifier were captured.
- `not_observed`: no matching CAN frame in this particular capture, not proof of absence.
- `frames_observed_dut_source`: frames with an operator-specified source address; identity requires independent verification.

**Passive captures cannot establish whether a display receives, decodes or shows a value.** Those require isolated active test injection and synchronized display observation.

The tool counts raw CAN frames, not reassembled NMEA 2000 fast-packet messages. A single fast-packet message may be multiple frames. Timestamp gaps are frame intervals, not guaranteed data-update rates. Invalid lines are counted but not interpreted.

The report includes SHA-256 hashes of the original log and PGN matrix for reproducibility. No pass/fail claim is made.
