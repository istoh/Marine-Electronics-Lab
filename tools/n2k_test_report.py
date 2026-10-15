#!/usr/bin/env python3
# Copyright © 2026 Isto Hunttila
"""Generate an evidence-based NMEA 2000 DUT test report from observations and criteria.
Read-only: no CAN I/O. Never infer display behavior from a passive capture.
"""
import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

STATUSES = {"PASS", "FAIL", "INCONCLUSIVE", "NOT_RUN"}
def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def load_observations(path):
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    required = {"test_id", "pgn", "source_address", "observed_value", "observed_unit",
                "observation_time_utc", "evidence_ref", "operator"}
    if not rows or not required.issubset(rows[0]):
        raise ValueError("Observation CSV requires header and at least one row")
    for row in rows:
        if not row["test_id"] or not row["evidence_ref"] or not row["operator"]:
            raise ValueError("Every observation requires test_id, evidence_ref and operator")
    return rows

def evaluate(case, obs):
    """Numeric comparison is performed only for an explicitly recorded display observation."""
    if case.get("evaluation") != "numeric_tolerance":
        return "INCONCLUSIVE", "No supported automated evaluation for this criterion"
    if len(obs) != 1:
        return "INCONCLUSIVE", "Exactly one observation required per numeric criterion"
    row = obs[0]
    if not row["evidence_ref"]:
        return "INCONCLUSIVE", "Missing evidence"
    if row["observed_unit"] != case["expected_unit"]:
        return "INCONCLUSIVE", "Unit mismatch; conversion not assumed"
    try:
        expected = float(case["expected_value"])
        actual = float(row["observed_value"])
        tolerance = float(case["absolute_tolerance"])
    except (ValueError, TypeError, KeyError):
        return "INCONCLUSIVE", "Non-numeric or incomplete comparison"
    if tolerance < 0 or not all(map(__import__("math").isfinite, (expected, actual, tolerance))):
        return "INCONCLUSIVE", "Invalid numerical value"
    if abs(actual - expected) <= tolerance:
        return "PASS", "Observed value within declared absolute tolerance"
    return "FAIL", "Observed value outside declared absolute tolerance"

def build(criteria_path, observations_path, comparison_path=None):
    criteria = json.loads(Path(criteria_path).read_text(encoding="utf-8"))
    if not isinstance(criteria, dict) or not isinstance(criteria.get("tests"), list):
        raise ValueError("Criteria must be an object containing tests[]")
    if not criteria.get("dut") or not criteria.get("firmware") or not criteria.get("operator"):
        raise ValueError("DUT, firmware and operator are required")
    obs = load_observations(observations_path)
    comparison = None
    if comparison_path:
        comparison = json.loads(Path(comparison_path).read_text(encoding="utf-8"))
        if not isinstance(comparison, dict) or "capture_sha256" not in comparison:
            raise ValueError("Comparison JSON lacks capture hash")
    ids = [t["test_id"] for t in criteria["tests"]]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate test_id")
    known = set(ids)
    unknown = sorted({r["test_id"] for r in obs} - known)
    if unknown:
        raise ValueError("Observations reference undefined tests: " + ", ".join(unknown))
    results = []
    for case in criteria["tests"]:
        related = [r for r in obs if r["test_id"] == case["test_id"]]
        if not related:
            status, reason = "NOT_RUN", "No observations recorded"
        else:
            status, reason = evaluate(case, related)
        results.append({"test_id":case["test_id"],"pgn":case.get("pgn"),
                        "status":status,"reason":reason,"observations":related,
                        "criterion":case})
    return {
        "schema_version":"1.0", "generated_utc":datetime.now(timezone.utc).isoformat(),
        "dut":criteria["dut"],"firmware":criteria["firmware"],"operator":criteria["operator"],
        "criteria_sha256":digest(criteria_path),
        "observations_sha256":digest(observations_path),
        "comparison_sha256":digest(comparison_path) if comparison_path else None,
        "capture_sha256":comparison.get("capture_sha256") if comparison else None,
        "counts":{s:sum(r["status"] == s for r in results) for s in sorted(STATUSES)},
        "warning":"PASS/FAIL applies only to manually recorded numeric observations with matching units and declared tolerance. Evidence is not authenticated by this program. Independent review required.",
        "results":results
    }

def markdown(report):
    lines=["# Marine Electronics Lab — instrument test report","",
           f"**DUT:** {report['dut']}  ",
           f"**Firmware:** {report['firmware']}  ",
           f"**Operator:** {report['operator']}  ",
           f"**Generated UTC:** {report['generated_utc']}","",
           "| Test | PGN | Result | Explanation | Evidence |",
           "|---|---:|---|---|---|"]
    for r in report["results"]:
        evidence=", ".join(o["evidence_ref"] for o in r["observations"]) or "—"
        clean=lambda x:str(x).replace("|","\\|").replace("\n"," ")
        lines.append(f"| {clean(r['test_id'])} | {clean(r['pgn'])} | {r['status']} | {clean(r['reason'])} | {clean(evidence)} |")
    lines.extend(["","## Traceability","",
                  f"- Criteria SHA-256: \`{report['criteria_sha256']}\`",
                  f"- Observations SHA-256: \`{report['observations_sha256']}\`",
                  f"- Comparison SHA-256: \`{report['comparison_sha256']}\`",
                  f"- Capture SHA-256: \`{report['capture_sha256']}\`",
                  "","**Limitation:** recorded evidence and instrument identity require human verification. Passive PGN traffic alone never establishes display compatibility.",""])
    return "\n".join(lines)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--criteria",required=True)
    p.add_argument("--observations",required=True)
    p.add_argument("--comparison",help="Optional output JSON from n2k_compare.py")
    p.add_argument("--json",dest="json_out",required=True)
    p.add_argument("--markdown",required=True)
    args=p.parse_args()
    report=build(args.criteria,args.observations,args.comparison)
    Path(args.json_out).write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    Path(args.markdown).write_text(markdown(report),encoding="utf-8")
if __name__=="__main__":
    main()
