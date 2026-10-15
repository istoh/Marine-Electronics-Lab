#!/usr/bin/env python3
# Copyright © 2026 Isto Hunttila
"""Read-only SocketCAN candump-log summarizer. No CAN interface opened, no transmissions.

Input: candump -L/-l style lines e.g.
(1502979132.106111) can0 09F50374#000A00FFFF00FFFF
"""
import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

LINE = re.compile(r"^\((\d+(?:\.\d+)?)\)\s+(\S+)\s+([0-9A-Fa-f]{8})#([0-9A-Fa-f]*)$")
def decode_id(can_id):
    priority = (can_id >> 26) & 7
    dp = (can_id >> 24) & 1
    pf = (can_id >> 16) & 255
    ps = (can_id >> 8) & 255
    src = can_id & 255
    pgn = (dp << 16) | (pf << 8) | (ps if pf >= 240 else 0)
    dst = 255 if pf >= 240 else ps
    return priority, pgn, src, dst

def summarize(path):
    counts = Counter()
    times = defaultdict(list)
    ignored = 0
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        match = LINE.fullmatch(line.strip())
        if not match:
            ignored += 1
            continue
        timestamp, interface, ident, payload = match.groups()
        if len(payload) % 2 or len(payload) > 16:
            ignored += 1
            continue
        priority, pgn, src, dst = decode_id(int(ident, 16))
        key = (interface, pgn, src, dst)
        counts[key] += 1
        times[key].append(float(timestamp))
    rows = []
    for (interface, pgn, src, dst), count in sorted(counts.items()):
        stamps = times[(interface, pgn, src, dst)]
        gaps = [b-a for a,b in zip(stamps, stamps[1:]) if b >= a]
        rows.append(dict(interface=interface, pgn=pgn, source=src, destination=dst,
                         frames=count, first_timestamp=min(stamps),
                         last_timestamp=max(stamps),
                         mean_interframe_ms=round(sum(gaps)/len(gaps)*1000, 3) if gaps else None))
    return dict(input=str(path), parsed_frames=sum(counts.values()), ignored_lines=ignored,
                note="Frame counts are NOT reassembled NMEA 2000 message counts. Fast packets may span multiple frames.",
                rows=rows)

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("capture", help="Existing candump log file")
    ap.add_argument("--csv", help="Optional output CSV path")
    args=ap.parse_args()
    report=summarize(args.capture)
    print(json.dumps(report, indent=2))
    if args.csv:
        with open(args.csv, "w", newline="", encoding="utf-8") as f:
            w=csv.DictWriter(f, fieldnames=["interface","pgn","source","destination","frames","first_timestamp","last_timestamp","mean_interframe_ms"])
            w.writeheader()
            w.writerows(report["rows"])
if __name__ == "__main__":
    main()
