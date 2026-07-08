# HERMES V8 Extreme Frontend Operation Test

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)]()
[![Hermes Agent](https://img.shields.io/badge/Hermes-Agent-purple.svg)](https://hermes-agent.nousresearch.com)

**Multi-agent extreme frontend operation test suite for HERMES V8 on Windows.**  

Organize a 15-agent team across 5 positions, launch 4 apps in screen quadrants, execute parallel operations, record the screen, and generate a signed-off report — all automated.

> ⚡ **Built and verified on 2026-07-06.**  
> 11,709 tests, 0 failures. 28 vulnerabilities identified (2 CRIT, 8 HIGH, 18 MED/LOW).

---

## Overview

```
V8 Modules Under Test:
┌─ engine/contract.py      — verify_with_contract decorator
├─ engine/world_model.py   — HAMT immutable state tree
├─ storage/state_tree.py   — Atomic persistence (os.replace + fsync)
├─ core/telemetry.py       — CausalJournal event stream
├─ core/bootloader.py      — Checkpoint recovery chain
└─ pipeline.py             — Execution pipeline
```

### What this does

| Phase | Est. Time | Contents |
|:------|:---------:|:---------|
| Team Organization | ~11 min | 5 positions × 3 agents = 15 subagents |
| Phase 0 Setup | ~1 min | ffmpeg recording + V8 pre-test check |
| Phase 1 Layout | ~3 min | App launch + quadrant snap |
| Phase 2 Operations | ~4 min | 3 parallel operation agents |
| Phase 3 Report | ~1 min | Verification + report generation |
| **Total** | **~20 min** | |

---

## Files

| File | Description |
|:-----|:------------|
| `SKILL.md` | Full Hermes Agent skill — the main workflow definition |
| `snap_quadrant.py` | Win32 SetWindowPos quadrant snap (Python fallback when Win+Arrow fails) |
| `check_quads.py` | Verify window positions via GetWindowRect |
| `extreme-frontend-test-plan.md` | Complete test plan (v3.0) |
| `extreme-quadrant-test-v3-design.md` | Quadrant test design document |
| `hermes-v8-frontend-test-optimization-plan.md` | Optimization plan for V8 frontend tests |
| `v8-extreme-test-report-design.md` | Report template and design |
| `v8-final-signoff.md` | Final signoff document |

---

## Prerequisites

- **Windows 10/11** (tested on 23H2)
- **HERMES V8** framework at `~/hermes-v4/`
- **Hermes Agent** with `delegate_task` capability
- **ffmpeg** (for screen recording)
- Python 3.11+

## How to Use

Load this as a Hermes skill:

```bash
# The skill is auto-discovered by Hermes Agent
# Trigger it by saying:
#   "跑 V8 Extreme Test"
#   "對 V8 進行極致前端操作測試"
```

Or manually follow the phases in `SKILL.md`.

## Known Pitfalls

| # | Pitfall | Solution |
|:-:|:--------|:---------|
| 1 | Snap Assist appears after Win+Up | Press Escape; snap still took effect |
| 2 | Screenshot returns "No windows found" | Use Python GetWindowRect as fallback |
| 3 | vision_analyze fails (no vision model) | Python coordinates + window title matching |
| 4 | Win+Down on floating = minimize | Check GetWindowRect first |
| 5 | Calculator min height 508px | Accept natural minimum |
| 6 | Taskbar button positions shift | Use App(mode="launch") or App(mode="switch") |
| 7 | Extra Chrome/Gemini window overlap | taskkill before restarting |
| 8 | Discord 6+ processes | taskkill /f /im discord.exe |
| 9 | Chrome custom title bar | Use Win+Arrow shortcuts only |
| 10 | App(switch) restores to previous position | Win+Down to float first |

## Architecture

```
┌─────────────────────────────┐
│   Orchestrator (You)        │
│   loads v8-extreme-test     │
│   skill + dispatches team   │
└──────────┬──────────────────┘
           │ delegate_task
    ┌──────┴──────────┐
    │  5 Positions    │
    │  × 3 Agents     │
    │  = 15 Subagents │
    └─────────────────┘
           │
    ┌──────┴──────────┐
    │  Phase 0-3      │
    │  Execute →      │
    │  Verify →       │
    │  Report         │
    └─────────────────┘
```

## V8 Vulnerability Summary

| Severity | Count | Key Issues |
|:---------|:-----:|:-----------|
| 🔴 CRITICAL | 2 | WorldModel class-level state (V-005), Windows fsync (V-010) |
| 🟠 HIGH | 8 | Circular import risk, no concurrent write, in-memory journal, loose bootloader checks, no profile isolation |
| 🟡 MEDIUM | 10 | Journal truncation, no retry, no execution token, capability assumptions |
| ⚪ LOW | 8 | Timestamp precision, incomplete error recovery |

## Related Repos

- [mcp-os-native-automation](https://github.com/a92070888-dev/mcp-os-native-automation) — FEOM Windows GUI automation MCP server
- [Hermes Agent](https://hermes-agent.nousresearch.com) — The autonomous AI agent platform

## License

MIT
