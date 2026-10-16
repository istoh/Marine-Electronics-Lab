#!/usr/bin/env python3
# Copyright © 2026 Isto Hunttila
# SPDX-License-Identifier: MIT
"""Read-only Windows UI Automation inventory for Nexus Race Software.

Never clicks, types, changes settings, or communicates with a device.
Run on the Windows desktop hosting the application.
"""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

def inventory(title_regex, max_depth=5, max_nodes=2000):
    try:
        from pywinauto import Desktop
    except ImportError as exc:
        raise RuntimeError("Install pywinauto on Windows: py -m pip install pywinauto") from exc
    windows = Desktop(backend="uia").windows(title_re=title_regex, visible_only=True)
    if not windows:
        raise RuntimeError("No visible application window matched title regex")
    result = []
    for window in windows:
        nodes = []
        queue = [(window, 0)]
        while queue and len(nodes) < max_nodes:
            node, depth = queue.pop(0)
            try:
                info = node.element_info
                rect = node.rectangle()
                nodes.append({
                    "depth": depth, "name": info.name,
                    "control_type": info.control_type,
                    "automation_id": info.automation_id,
                    "class_name": info.class_name,
                    "rectangle": [rect.left, rect.top, rect.right, rect.bottom],
                    "enabled": node.is_enabled(),
                    "visible": node.is_visible(),
                })
                if depth < max_depth:
                    queue.extend((child, depth + 1) for child in node.children())
            except Exception as exc:
                nodes.append({"depth": depth, "error": type(exc).__name__})
        result.append({"window_title": window.window_text(), "nodes": nodes,
                       "truncated": bool(queue)})
    return result

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--title-regex", default="(?i).*nexus.*race.*")
    parser.add_argument("--max-depth", type=int, default=5)
    parser.add_argument("--max-nodes", type=int, default=2000)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    if not 0 <= args.max_depth <= 12 or not 1 <= args.max_nodes <= 20000:
        parser.error("max-depth must be 0..12 and max-nodes 1..20000")
    try:
        windows = inventory(args.title_regex, args.max_depth, args.max_nodes)
    except RuntimeError as exc:
        parser.error(str(exc))
    result = {"schema_version": "1.0", "generated_utc": datetime.now(timezone.utc).isoformat(),
              "mode": "read_only_uia_inventory", "title_regex": args.title_regex,
              "windows": windows, "caution": "UI text can contain personal/device identifiers; review before sharing"}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    digest = hashlib.sha256(args.out.read_bytes()).hexdigest()
    print(f"Saved {args.out} SHA256={digest} windows={len(windows)}")

if __name__ == "__main__":
    main()
