#!/usr/bin/env python3
# Copyright © 2026 Isto Hunttila
"""Compare a read-only candump capture with the documentation PGN matrix.

Observation of a PGN does NOT prove the DUT supports it: traffic can come from
other nodes, and receive capability cannot be inferred from passive captures.
"""
import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from n2k_capture_report import summarize

DEVICES = {
    "garmin_gnx20": "Garmin GNX 20",
    "furuno_fi70": "Furuno FI-70",
    "bg_triton2": "B&G Triton2",
    "simrad_is42": "Simrad IS42",
    "raymarine_i70s": "Raymarine i70s",
    "nke_multigraphic_ii": "nke Multigraphic II",
}

def compare(capture, matrix, device, dut_sources=None):
    if device not in DEVICES:
        raise ValueError("Unknown device: " + device)
    report = summarize(capture)
    with open(matrix, newline="", encoding="utf-8") as f:
        matrix_rows = list(csv.DictReader(f))
    rx_col, tx_col = device + "_rx", device + "_tx"
    if matrix_rows and (rx_col not in matrix_rows[0] or tx_col not in matrix_rows[0]):
        raise ValueError("Missing device columns in matrix")
    by_pgn = {int(row["pgn"]): row for row in matrix_rows}
    observed = {}
    for row in report["rows"]:
        pgn = int(row["pgn"])
        observed[pgn] = observed.get(pgn, 0) + int(row["frames"])
    dut_sources = set(dut_sources or [])
    output = []
    for pgn in sorted(set(observed) | set(by_pgn)):
        row = by_pgn.get(pgn, {})
        tx = row.get(tx_col, "not_in_matrix")
        rx = row.get(rx_col, "not_in_matrix")
        output.append({
            "pgn": pgn, "description": row.get("description", ""),
            "frames_observed_any_source": observed.get(pgn, 0),
            "frames_observed_dut_source": sum(
                int(x["frames"]) for x in report["rows"]
                if int(x["pgn"]) == pgn and int(x["source"]) in dut_sources
            ) if dut_sources else None,
            "manual_rx": rx, "manual_tx": tx,
            "observation": ("observed_on_bus" if observed.get(pgn) else "not_observed"),
            "assessment": (
                "manual_pending" if tx == "pending_extraction"
                else "observed_from_dut_source" if dut_sources and any(
                    int(x["pgn"]) == pgn and int(x["source"]) in dut_sources for x in report["rows"])
                else "not_an_interoperability_verdict"
            ),
        })
    return {
        "schema_version": "1.0",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "device": device,
        "device_label": DEVICES[device],
        "dut_sources": sorted(dut_sources),
        "capture": str(capture),
        "capture_sha256": hashlib.sha256(Path(capture).read_bytes()).hexdigest(),
        "matrix_sha256": hashlib.sha256(Path(matrix).read_bytes()).hexdigest(),
        "parsed_frames": report["parsed_frames"],
        "ignored_lines": report["ignored_lines"],
        "methodology": "Passive frame observation versus manufacturer PGN list; no RX capability inference and no pass/fail verdict.",
        "rows": output,
    }

def render_md(report):
    lines = [
        "# NMEA 2000 documentation-to-capture comparison",
        "",
        f"Device: **{report['device_label']}**",
        f"Capture SHA-256: \`{report['capture_sha256']}\`",
        f"Matrix SHA-256: \`{report['matrix_sha256']}\`",
        f"Parsed frames: {report['parsed_frames']}; ignored lines: {report['ignored_lines']}",
        "",
        "**Important:** passive traffic does not prove that the display receives or renders any PGN.",
        "",
        "| PGN | Description | Manual RX | Manual TX | Observed bus frames | DUT-source frames |",
        "|---:|---|---|---|---:|---:|",
    ]
    for r in report["rows"]:
        desc = str(r["description"]).replace("|", "\\|")
        dut = r["frames_observed_dut_source"]
        lines.append(f"| {r['pgn']} | {desc} | {r['manual_rx']} | {r['manual_tx']} | {r['frames_observed_any_source']} | {dut if dut is not None else 'unknown'} |")
    lines.extend(["", "No device performance or interoperability verdict is asserted.", ""])
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("capture")
    parser.add_argument("--matrix", default="research/instruments/nmea2000-pgn-matrix.csv")
    parser.add_argument("--device", required=True, choices=sorted(DEVICES))
    parser.add_argument("--dut-source", type=int, action="append", default=[], help="Known DUT source address; repeatable")
    parser.add_argument("--json", dest="json_path")
    parser.add_argument("--markdown")
    args = parser.parse_args()
    for address in args.dut_source:
        if not 0 <= address <= 253:
            parser.error("DUT source address must be 0..253")
    result = compare(args.capture, args.matrix, args.device, args.dut_source)
    if args.json_path:
        Path(args.json_path).write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if args.markdown:
        Path(args.markdown).write_text(render_md(result), encoding="utf-8")
    if not args.json_path and not args.markdown:
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
