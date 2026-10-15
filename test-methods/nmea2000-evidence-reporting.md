<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- Copyright © 2026 Isto Hunttila -->
# Display observation + PGN test report workflow

**Status: draft, code committed but not executed against hardware.** Works entirely on files and never transmits CAN traffic.

## Input artifacts
1. An existing `candump` log (optional), analyzed with `tools/n2k_compare.py`.
2. A criteria JSON file: DUT identity, firmware, operator, tests with expected value/unit and absolute tolerance, plus requirement source.
3. An observation CSV with `test_id,pgn,source_address,observed_value,observed_unit,observation_time_utc,evidence_ref,operator`. Evidence references should point to immutable video/image/log records with timestamps.
4. Optional PGN comparison JSON containing capture SHA-256.

## Example commands
```bash
python3 tools/n2k_compare.py capture.log --device garmin_gnx20 --json comparison.json
python3 tools/n2k_test_report.py \
  --criteria test-plans/examples/n2k-criteria.template.json \
  --observations test-plans/examples/n2k-observations.template.csv \
  --comparison comparison.json \
  --json report.json --markdown report.md
python3 -m unittest discover -s tools/tests -v
```

Templates are intentionally incomplete and are **not real observations or manufacturer acceptance thresholds**. Replace placeholders and set criteria *before* testing. An empty observation file with header only will currently be rejected; provide at least one genuine observation.

## Result semantics
- **PASS**: exactly one recorded numeric observation within the predeclared tolerance, with matching unit and evidence reference.
- **FAIL**: exactly one recorded numeric observation outside tolerance, with matching unit and evidence reference.
- **INCONCLUSIVE**: unit mismatch, missing/invalid numeric data, multiple observations, unsupported evaluator.
- **NOT_RUN**: no observation for test.

These are preliminary computational classifications of *operator-supplied* observations, **not independently verified DUT results**. A human must validate video, timestamps, test stimulus, DUT identity, instrument source, calibration and requirement provenance. No automatic conversion between units. PGN bus presence does not establish display response.

## Traceability
The report hashes criteria, observations, optional comparison JSON and the original capture hash. Store actual evidence files in controlled artifact storage; avoid committing large videos or copyrighted manufacturer PDFs to GitHub. A future version should add structured evidence manifests, multiple-trial statistics, synchronized camera timing and independent review signatures.
