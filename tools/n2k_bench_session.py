#!/usr/bin/env python3
"""Offline NMEA2000 bench session manifest and timing analysis. Never transmits CAN."""
import argparse
import csv
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

def sha256(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()

def parse_events(path):
    with open(path,newline="",encoding="utf-8") as f:
        rows=list(csv.DictReader(f))
    required={"event_id","trial_id","event_type","timestamp_ns","clock_domain","evidence_ref"}
    if not rows:
        raise ValueError("No event rows")
    if not required.issubset(rows[0]):
        raise ValueError("Missing event columns: "+str(sorted(required-set(rows[0]))))
    allowed={"stimulus_sent","can_received","display_changed","sync_marker"}
    for r in rows:
        if r["event_type"] not in allowed:
            raise ValueError("Unknown event_type")
        if not r["trial_id"] or not r["event_id"] or not r["evidence_ref"] or not r["clock_domain"]:
            raise ValueError("Missing event identity or evidence")
        r["timestamp_ns"]=int(r["timestamp_ns"])
        if r["timestamp_ns"]<0: raise ValueError("Negative timestamp")
    if len({r["event_id"] for r in rows})!=len(rows):
        raise ValueError("Duplicate event_id")
    return rows

def analyze(events, clock_offsets=None):
    """Offsets convert event timestamps into a single reference clock, in ns.

    An offset must be measured externally; this code NEVER estimates it from
    unrelated event timestamps. If any offset is missing, timing is inconclusive.
    """
    offsets=clock_offsets or {}
    grouped={}
    for r in events: grouped.setdefault(r["trial_id"],[]).append(r)
    trials=[]
    for trial,rows in sorted(grouped.items()):
        kinds={k:[r for r in rows if r["event_type"]==k] for k in
               ("stimulus_sent","can_received","display_changed")}
        if len(kinds["stimulus_sent"])!=1 or len(kinds["display_changed"])!=1:
            trials.append({"trial_id":trial,"status":"INCONCLUSIVE",
                           "reason":"Requires exactly one stimulus and one display event"})
            continue
        start=kinds["stimulus_sent"][0]
        end=kinds["display_changed"][0]
        if start["clock_domain"] not in offsets or end["clock_domain"] not in offsets:
            trials.append({"trial_id":trial,"status":"INCONCLUSIVE",
                           "reason":"Missing measured clock offset"})
            continue
        t0=start["timestamp_ns"]+offsets[start["clock_domain"]]
        t1=end["timestamp_ns"]+offsets[end["clock_domain"]]
        if t1<t0:
            trials.append({"trial_id":trial,"status":"INCONCLUSIVE",
                           "reason":"Display timestamp precedes stimulus after offset correction"})
            continue
        trials.append({"trial_id":trial,"status":"TIMING_COMPUTED",
                       "stimulus_to_display_ms":round((t1-t0)/1e6,3),
                       "note":"End-to-end estimate; camera exposure and detection uncertainty not corrected"})
    samples=[t["stimulus_to_display_ms"] for t in trials if t["status"]=="TIMING_COMPUTED"]
    return {"trials":trials,"valid_trials":len(samples),
            "mean_ms":round(sum(samples)/len(samples),3) if samples else None,
            "min_ms":min(samples) if samples else None,
            "max_ms":max(samples) if samples else None}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--events",required=True)
    p.add_argument("--session",required=True,help="Session metadata JSON")
    p.add_argument("--out",required=True)
    args=p.parse_args()
    metadata=json.loads(Path(args.session).read_text(encoding="utf-8"))
    if not isinstance(metadata,dict) or not metadata.get("session_id") or not metadata.get("dut"):
        p.error("session JSON requires session_id and dut")
    offsets=metadata.get("measured_clock_offsets_ns",{})
    if not isinstance(offsets,dict) or any(type(v)!=int for v in offsets.values()):
        p.error("clock offsets must be integer nanoseconds")
    events=parse_events(args.events)
    report={"schema_version":"1.0","generated_utc":datetime.now(timezone.utc).isoformat(),
            "session":metadata,"events_sha256":sha256(args.events),
            "session_sha256":sha256(args.session),
            "timing":analyze(events,offsets),
            "caution":"Timing requires independently measured clock offsets and video-frame/exposure uncertainty. No device PASS/FAIL inferred."}
    Path(args.out).write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
if __name__=="__main__":main()
