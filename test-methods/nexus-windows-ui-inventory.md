<!-- Copyright © 2026 Isto Hunttila -->
<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Nexus Race Software Windows 11 UI inventory

**User-reported verification (2026-10-16):** Nexus Race Software launches and works on the user's Windows 11 computer. Exact version, GND 10 USB/COM connectivity and automation control-tree accessibility have not yet been independently verified. This supersedes the earlier generic Windows 11 compatibility uncertainty for this specific installation only.

## Read-only inventory

On Windows 11, with Nexus Race Software open:

```powershell
py -m pip install pywinauto
py tools\nexus_windows_ui_inventory.py --out results\nexus-ui.json
```

The tool enumerates visible UI Automation controls. It does **not** click menus, enter text, configure GND 10 or send protocol traffic. It stores labels, control types, automation IDs, class names, rectangles and enabled/visible flags. The output may contain identifying device details; review before sharing or committing.

If the application title does not match the default regex, pass `--title-regex ".*"` to inspect all visible top-level windows, but note that this may capture unrelated applications and private information. Prefer an exact title regex once known.

## Next validation steps

1. Record executable version and full window title.
2. Compare discovered UIA menu/control names with the Garmin-supported workflow: Communication, Tools → Configure, gateway → Setup.
3. If menus are owner-drawn or missing from UIA, inspect with Microsoft Accessibility Insights/Inspect.exe; keep screenshots as separately reviewed evidence.
4. Only after controls are identified, write a navigation-only test harness with explicit safeguards and no configuration writes.
5. Independently confirm GND 10 COM port, driver and firmware version.

**Configuration:** MEL-CFG-NEX-002 stores the executable/version and discovered selectors. MEL-CFG-NEX-008 gates any later write operations.
