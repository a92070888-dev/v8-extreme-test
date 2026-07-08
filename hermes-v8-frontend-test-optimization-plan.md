# HERMES V8 極致前端操作測試 — 效率優化方案

> **版本**: v1.0 | **作者**: Frontend Operation Agent #3 | **日期**: 2026-07-06
> **參考**: 3-agent parallel (222s, 94%), 6-agent stress test (PASS), quadrant layout v2.0

---

## 目錄

1. [極致的定義](#1-極致的定義)
2. [基於過往經驗的改進方案](#2-基於過往經驗的改進方案)
3. [Screenshot 強制驗證流程](#3-screenshot-強制驗證流程)
4. [失敗升級路徑](#4-失敗升級路徑)
5. [最終交付物格式](#5-最終交付物格式)
6. [完整腳本](#6-完整腳本)

---

## 1. 極致的定義

### 1.1 核心指標

| 指標 | V2 (當前) | V8 (目標) | 改善倍率 |
|:-----|:---------:|:---------:|:--------:|
| 並行 AGENT 數 | 3 (batch) / 6 (total) | **6 (batch)** / **12 (total)** | 2× |
| 總操作 APP 數 | 4 (Chrome/Notepad/Explorer/Discord) | **8** | 2× |
| 總操作步驟 | ~16 | **~48** | 3× |
| 完成時間 | 222s / 3-agent | **<120s / 6-agent** | 2× |
| 成功率 | 94% | **≥98%** | — |
| 每步驗證 | partial (僅最終) | **100% (每步截圖)** | hard requirement |
| 失敗自動恢復 | manual | **3 層升級路徑** | new |

### 1.2 8-APP 矩陣

```
┌────────────────────────────────────────────────────────┐
│  Quadrant 1 (Q1)          │  Quadrant 2 (Q2)           │
│  左上                     │  右上                      │
│                           │                            │
│  🅰️ Chrome (瀏覽/搜尋)    │  🅱️ Obsidian (筆記/寫作)    │
│  🅲 VS Code (編碼/腳本)    │  🅳 LINE (通訊/歷史)        │
├───────────────────────────┼────────────────────────────┤
│  Quadrant 3 (Q3)          │  Quadrant 4 (Q4)           │
│  左下                     │  右下                      │
│                           │                            │
│  🅴 檔案總管 (文件操作)     │  🅵 Discord (社群/通知)     │
│  🅶 記事本 (文字/測試)     │  🅷 計算機 / Steam (雜項)   │
└────────────────────────────────────────────────────────┘
```

**為什麼這 8 個 APP？**
- 涵蓋 4 大類型：瀏覽器（Chrome）、生產力（Obsidian/VS Code/記事本）、通訊（LINE/Discord）、系統（檔案總管/計算機）
- 每個象限 2 個 APP — 切換測試 + 焦點管理壓力
- 覆蓋已學程式的快捷鍵：Ctrl+L/L/K/N/O/P — 全覆蓋

### 1.3 48 步驟分佈

| 階段 | 步驟數 | 內容 |
|:-----|:------:|:-----|
| **Phase 0**: 前置準備 | 4 | 啟動 8 APP + 象限佈局 + 啟動錄影 |
| **Phase 1**: 6 AGENT 平行 Batch 1 | 16 | 4 AGENT × 4 操作/AGENT |
| **Phase 2**: 6 AGENT 平行 Batch 2 | 16 | 另 4 AGENT × 4 操作/AGENT |
| **Phase 3**: 跨 APP 切換測試 | 8 | 焦點切換 + 跨 APP 資料傳遞 |
| **Phase 4**: 收尾驗證 | 4 | 最終截圖 + 關錄影 + 報告 |
| **總計** | **~48** | — |

### 1.4 時間預算

```
Phase 0 (Launch + Layout):    30s  ← 使用者手動排象限 5s
Phase 1 (Batch 1, 6 agents):  30s  ← 完全平行
Phase 2 (Batch 2, 6 agents):  30s  ← 完全平行
Phase 3 (Cross-app switch):   20s  ← 順序操作
Phase 4 (Verify + Report):    10s
────────────────────────────────────
Total:                       ~120s  ← V8 target
```

---

## 2. 基於過往經驗的改進方案

### 2.1 問題 vs 解法對照表

| # | 過往問題 | 發生率 | V8 改進方案 |
|:--|:---------|:------:|:------------|
| 1 | **CAPTCHA** — Google/Bing/DDG 都擋 browser | 100% | **browser 永不進搜尋引擎**。搜尋用 `web_search` (API-based)，瀏覽器只開已知 URL |
| 2 | **Python GetWindowRect 座標錯誤** | ~30% | **完全禁用 Python 座標判斷**。只認 Screenshot + vision_analyze |
| 3 | **Snapshot 回「No windows」假陰性** | ~20% | 降級到 Screenshot + vision_analyze，不信任純文字輸出 |
| 4 | **App(switch) 需要完整視窗標題** | 每次必用 | 先 `script/list_windows.py` 取得完整標題 → 精確 Switch |
| 5 | **Win+Down 浮動視窗 = 最小化** | 常見 | Snap 流程標準化：先 Win+左/右 → Wait(2) → Win+上/下 |
| 6 | **Chrome 自訂標題列不支援 Snap Layout flyout** | 100% | 只用 Win+Arrow 快捷鍵，不點 Chrome 標題列按鈕 |
| 7 | **Discord 6+ processes → App(switch) 混亂** | 每次 | Discord 用指定 PID 或工作列座標點擊 |
| 8 | **terminal("start X") 不保證前景** | ~40% | 一律加 App(mode="switch") 或 Alt+Tab |
| 9 | **Type 需要 loc/label 參數** | 100% | 全程改用 Clipboard set + Ctrl+V |
| 10 | **多視窗同名（UWP）** | 偶發 | 只選 visible window，或 taskkill 舊執行續重開 |
| 11 | **ffmpeg kill 後檔案損毀** | 每次 | 用 `-t N` 參數結束，不 kill process |
| 12 | **寫入檔案不回傳錯誤但實際失敗** | 異常 | write 後一定 `cat` 或 `ls -la` 確認 |
| 13 | **Hermes 自身視窗擋住桌面** | 每次 | 第一步 Shortcut("win+d") 顯示桌面 |
| 14 | **Subagent 無法用 MCP tools** | 架構限制 | Parent 處理所有桌面操作，subagent 只做 terminal/web/search |
| 15 | **delegate_task max 3 per batch** | 架構限制 | Batch 1 (6 agents) = 2 rounds of delegate_task × 3 agents |
| 16 | **Win+Down on already-snapped window** | 常見 | Snap 前先抓完整標題，用 python list_windows.py 確認狀態 |
| 17 | **Notepad 中文/英文標題不同** | 環境 | 用 Task Manager 名稱「記事本」或「Notepad」雙重確認 |
| 18 | **VS Code 啟動慢或版本混淆** | 偶發 | 先 `where code` 確認路徑，用 `code --new-window` 開新視窗 |

### 2.2 關鍵效能優化點

#### 2.2.1 減少無效等待（-30s）

```
V2 模式: Wait(2) × 16 steps = 32s wasted
V8 模式: WaitFor(condition) 取代固定 Wait — 條件成立即繼續
         Snap 間固定 Wait(1) 無法避免（動畫必須等）
         Total wasted: Wait(2) × 8 snaps = 16s → -50%
```

#### 2.2.2 減少不必要的 Snapshot（-15s）

```
V2: 每步後 Snapshot (2-5s/call) × 16 = 32-80s just on snapshots
V8: Screenshot (1.2s/call) 取代 Snapshot — 純驗證用
    只在需要互動元素時才 Snapshot
    Screenshot × 48 steps × 1.2s = 57.6s (vs Snapshot 240s)
```

#### 2.2.3 平行最大化（-60s）

```
V2: 3 agents per batch, sequential batches
V8: 
  - Batch 1: 6 agents (2 delegate_task calls, 3 each)
  - Batch 2: 6 agents (2 delegate_task calls, 3 each)
  - Actual wall time ~30s per batch = 2× throughput
```

#### 2.2.4 工具選擇（-40% token）

```
優先鏈（低→高費用）：
1. Shortcut            — 0 token, instant
2. WaitFor             — 取代固定 Wait
3. Clipboard+C+V      — 取代 Type(loc)
4. Screenshot無UI tree — 1.2s, 純圖
5. Snapshot含UI tree   — 只在需要時用
6. PowerShell          — 僅 CJK/COM 場景
7. vision_analyze      — 僅 final verification
```

### 2.3 學習曲線 — 每輪測試的自動優化

```
Round 1: Baseline — 執行完整測試，記錄每步耗時
Round 2: 瓶頸調整 — 找出最慢的 3 步，優化工具選擇
Round 3: Parallel tuning — 調整 batch 分配平衡
Round 4: 極限衝刺 — 移除所有冗餘驗證，只留關鍵檢查點
```

---

## 3. Screenshot 強制驗證流程

### 3.1 鐵則：Never Claim, Always Verify

```
❌ V2 錯誤模式:
  Type → 「完成」 → 使用者:「才沒有！」

✅ V8 正確模式:
  Shortcut → Screenshot → vision_analyze → 驗證 → 再下一步
```

### 3.2 每步強制驗證流程圖

```
┌─────────────┐
│  開始操作    │
│  (Shortcut/  │
│   Clipboard) │
└──────┬──────┘
       ▼
┌─────────────┐     ╔═══════════════════════╗
│  執行操作    │────▶║  Step Screenshot      ║
│  (1 action)  │     ║  (強制！每步必須)      ║
└─────────────┘     ╚═══════════════════════╝
                           │
                           ▼
                    ┌──────────────┐
                    │ vision_analyze│
                    │ 「此步結果是？  │
                    │  視窗狀態？   │
                    │  內容正確？   │
                    └──────┬───────┘
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
        ┌──────────┐            ┌──────────────┐
        │ ✅ 正確   │            │ ❌ 錯誤/不明  │
        └────┬─────┘            └──────┬───────┘
             │                         │
             ▼                         ▼
       ┌──────────┐           ┌──────────────────┐
       │ 下一步    │           │ 失敗升級路徑      │
       │ (繼續)    │           │ (見第4章)         │
       └──────────┘           └──────────────────┘
```

### 3.3 驗證檢查點（48 步 × 必截圖）

| 階段 | 檢查點 | 驗證內容 | 通過條件 |
|:-----|:-------|:---------|:---------|
| **Phase 0** | P0-1: Launch 8 apps | 各 APP 已在工作列或焦點 | Snapshot 顯示對應 process |
| | P0-2: Quadrant layout | 4 象限各 2 APP 正確排列 | vision: 左上/右上/左下/右下各有正確 APP |
| | P0-3: Recording started | ffmpeg 運作中 | process 顯示 running |
| | P0-4: Desktop clean | Hermes 未擋住操作區 | vision: 桌面全部可見 |
| **Phase 1** | P1-1 to P1-16: 每步 | 操作結果正確 | vision: 確認特定 UI 元素存在 |
| **Phase 2** | P2-1 to P2-16: 每步 | 同上 | 同上 |
| **Phase 3** | P3-1: Chrome→Obsidian | 焦點切換成功 | vision: Obsidian 在前景 |
| | P3-2: Obsidian 開檔 | Ctrl+O 生效 | vision: 檔案開啟對話框 |
| | P3-3: Chrome 複製→記事本貼上 | 跨 APP 資料傳遞 | vision: 記事本有黏貼內容 |
| | P3-4 to P3-8: 其他切換 | 焦點正確 | vision: 對應 APP 在前景 |
| **Phase 4** | P4-1: 最終 8-APP 全景 | 所有 APP 仍在運作 | vision: 無 crash |
| | P4-2: 測試檔案存在 | 檔案寫入成功 | FileSystem(mode='list') |
| | P4-3: 檔案內容正確 | 內容與預期一致 | read_file |
| | P4-4: 錄影有效 | ffmpeg 正常結束 | ffprobe 確認 |

### 3.4 截圖命名規範

```
screenshots/
├── phase0/
│   ├── 00-launch-apps.png
│   ├── 01-quadrant-layout.png
│   └── 02-recording-started.png
├── phase1/
│   ├── agent1-step01-before.png
│   ├── agent1-step01-after.png   ← 每步 before/after
│   ├── agent1-step02-before.png
│   ├── agent1-step02-after.png
│   └── ...
├── phase2/
│   └── ...
├── phase3/
│   ├── switch-chrome-to-obsidian.png
│   ├── copy-from-chrome-to-notepad.png
│   └── ...
└── final/
    ├── all-apps-running.png
    ├── test-result.png
    └── recording-valid.png
```

---

## 4. 失敗升級路徑

### 4.1 三層升級架構

```
                      ┌─────────────────┐
                      │  操作失敗        │
                      │  (vision_analyze │
                      │   判定錯誤)      │
                      └────────┬────────┘
                               │
                    ┌──────────┴──────────┐
                    ▼                     ▼
           ┌────────────────┐   ┌─────────────────┐
           │  Level 1: Retry │   │  Retry 次數      │
           │  同方案重試 1×  │   │  ≤2 (不含首次)    │
           └───────┬────────┘   └───────────────────┘
                   │ 失敗
                   ▼
           ┌────────────────┐   ┌─────────────────┐
           │  Level 2:      │   │  換方案選項      │
           │  換方案重新執行 │   │  Shortcut→Click │
           └───────┬────────┘   │  →PowerShell     │
                   │ 失敗       └───────────────────┘
                   ▼
           ┌────────────────┐   ┌─────────────────┐
           │  Level 3: Skip │   │  跳過條件        │
           │  記錄失敗跳過  │   │  不影響後續步驟  │
           └───────┬────────┘   └───────────────────┘
                   │
                   ▼
           ┌────────────────┐
           │  寫入 FAILURE   │
           │  日誌 (可追蹤)  │
           └────────────────┘
```

### 4.2 具體決策表

| 失敗類型 | Level 1 (Retry) | Level 2 (換方案) | Level 3 (Skip) |
|:---------|:----------------|:-----------------|:---------------|
| **APP 未啟動** | 再次 `App(launch)` + Wait(3) | 改用 `terminal("start X")` | 跳過該 APP 的所有操作，標記 FAILED |
| **Quadrant snap 失敗** | 再次 Win+Arrow 序列（Wait(2)間隔） | 先 Win+Down 浮動再重新 snap | 跳過象限，標記 FAILED |
| **Ctrl+L 導航無反應** | 先 Click 位址欄再 Ctrl+A → C+V | 改用 Clipboard + 右鍵貼上 | 跳過該步 |
| **Type 內容錯誤** | Clear=True 重新 Type | 改用 Clipboard+C+V | 跳過內容驗證 |
| **Screenshot 模糊/全黑** | 等 1s 重拍（最多 3 次） | 改用 Snapshot(use_ui_tree=false) | 跳過該步驗證（記錄 WARNING） |
| **Delegate_task 超時** | 重送，timeout=60s | 改成 sequential 執行 | 跳過該 AGENT |
| **FileSystem write 失敗** | 先 mkdir -p 再寫 | 改用 PowerShell Out-File | 跳過檔案，用 echo 替代 |
| **Process kill 失敗** | taskkill /F | 改用 Stop-Process -Force | 跳過清理 |
| **ffmpeg 啟動失敗** | 換 codec（h264_nvenc→libx264） | 降解析度（1280x720） | 跳過錄影（WARNING） |
| **vision_analyze 不明確** | 重新截圖再問 | 問更具體的問題 | 人工判定（USER 幫忙看） |

### 4.3 重大失敗 — 中斷條件

如果以下情況發生，**立即中斷測試**，不進 Level 3：

```
1. ❌ 連續 3 個以上不同操作失敗（系統性問題）
2. ❌ Hermes 自身被關閉或無法回應
3. ❌ 磁碟空間 < 500MB（錄影會爆）
4. ❌ 作業系統彈出阻斷對話框（需要使用者介入）
```

### 4.4 失敗日誌格式

每步失敗寫入 `logs/failures.jsonl`：

```json
{"timestamp": "2026-07-06T14:30:00", "step": "P1-03", "agent": "WebAgent", 
 "operation": "Chrome Ctrl+L navigate", "level": 2, "attempts": 3,
 "error": "Ctrl+L無反應，改用Clipboard+C+V後成功",
 "screenshot": "screenshots/phase1/agent1-step03-after.png",
 "resolution": "換方案成功"}
```

---

## 5. 最終交付物格式

### 5.1 測試報告

```
HERMES V8 Extreme Frontend Operation Test Report
================================================
Date: 2026-07-06
Status: PASS / PARTIAL / FAILED

=== Summary ===
Total Steps:     48/48 (100%)
Passed Steps:    47/48 (97.9%)
Failed Steps:    1/48
Skipped Steps:   0/48
Total Duration:  115s

=== By Phase ===
Phase 0 (Setup):        4/4 ✅    28s
Phase 1 (Batch 1):     16/16 ✅   32s
Phase 2 (Batch 2):     15/16 ✅   30s  ← 1 CAPTCHA fallback
Phase 3 (Cross-app):    8/8 ✅    20s
Phase 4 (Verify):       4/4 ✅    5s

=== Screenshot Coverage ===
Total Screenshots: 96 (48 steps × before+after)
PASS Verification: 95/96 (99.0%)
Screenshot Dir:    screenshots/2026-07-06/

=== Failure Detail ===
| Step | Agent   | Op            | Level | Resolution     |
|------|---------|---------------|-------|----------------|
| P2-3 | WebAgent| Google search | 2     | web_search API |

=== Recording ===
File:    test-recording-20260706.mp4
Size:    245 MB
Length:  2m15s
Codec:   H.264, yuv420p
Status:  VALID (ffprobe OK)

=== Performance vs Target ===
Metric        | V2 Baseline | Target V8 | Actual V8 | Δ
--------------|-------------|-----------|-----------|-----
Duration      | 222s        | 120s      | 115s      | -48%
Steps         | 16          | 48        | 48        | +200%
Success Rate  | 94%         | ≥98%      | 97.9%     | -0.1%
Agents        | 3           | 6         | 6         | +100%
Apps          | 4           | 8         | 8         | +100%
Screenshot    | Partial     | 100%      | 100%      | +100%
Auto Recovery | No          | 3-layer   | 3-layer   | +100%
```

### 5.2 交付檔案結構

```
C:\Users\PP\Desktop\hermes-v8-test-YYYY-MM-DD\
├── test-recording-YYYYMMDD.mp4     ← 螢幕錄影
├── hermes-v8-frontend-test-optimization-plan.md  ← 本方案（重複提供方便取用）
├── TEST-REPORT-YYYY-MM-DD.md        ← 最終報告
├── screenshots/                     ← 96+ 截圖
│   ├── phase0/                     (4 張)
│   ├── phase1/                     (32 張)
│   ├── phase2/                     (32 張)
│   ├── phase3/                     (16 張)
│   └── final/                      (8 張)
├── logs/
│   ├── failures.jsonl               ← 失敗記錄
│   └── timing.jsonl                 ← 每步耗時
└── artifacts/
    ├── test-files/                  ← 測試建立的檔案
    └── cross-app-data.txt           ← 跨 APP 傳遞的資料
```

### 5.3 品質閘門 (Quality Gates)

完成測試前必須檢查：

| Gate | 檢查項 | 最低要求 |
|:-----|:-------|:---------|
| G1 | Screenshot 覆蓋率 | 100%（48/48 步有 before+after） |
| G2 | 成功率 | ≥95% |
| G3 | 錄影有效 | ffprobe 無錯誤 |
| G4 | Phase 0 通過 | 8 APP 全部成功啟動並佈局 |
| G5 | 失敗記錄完整性 | 所有非 PASS 步驟有日誌 |
| G6 | 檔案產出 | artifacts/ 包含所有測試檔案 |

**閘門未過的處理**：未過閘門的報告標記為 `DRAFT`，附缺失原因，不得標記為 `FINAL`。

---

## 6. 完整腳本

### 6.1 主流程

```
HERMES V8 TEST — EXECUTION SEQUENCE

[P0-1] Shortcut("win+d")                              # 顯示桌面
[P0-2] App(launch) × 8                                # 啟動 Chrome, Obsidian, VS Code, LINE,
                                                       #         Explorer, Discord, Notepad, Calculator
[P0-3] WaitFor(condition="element_exists", timeout=20) # 等全部 APP 就緒
[P0-4] USER: 手動排 4 象限（～5秒）                      # 使用者用滑鼠拖曳
[P0-5] Screenshot → vision: layout correct?            # 驗證象限
[P0-6] ffmpeg -f gdigrab ... -t 300 ...                # 開始錄影
[P0-7] cp 本方案到桌面                                  # 本方案文件

[P1-Batch1] delegate_task(tasks=[
  WebAgent:     Chrome navigate + search verify
  DesktopAgent: File structure create + verify
  OfficeAgent:  Notepad multi-line write + verify
  DiscordAgent: Discord process check + screenshot
  LineAgent:    LINE process check
  CalcAgent:    Calculator open + basic calc
])
→ Wait for all 6 to return (parallel, ~30s)

[P1-Screenshots] 每 AGENT 回報後強制 Screenshot 驗證

[P2-Batch2] delegate_task(tasks=[
  ObsidianAgent:  Obsidian open note + content
  CodeAgent:      VS Code create test script
  SwitchAgent:    Chrome→Obsidian focus switch test
  CrossAgent:     Chrome copy → Notepad paste test
  SnapAgent:      Re-snap test (break windows, re-snap)
  StressAgent:    Rapid switch 8 apps in sequence
])
→ Wait for all 6 to return (parallel, ~30s)

[P2-Screenshots] 每 AGENT 回報後強制 Screenshot 驗證

[P3-CrossApp] Sequential cross-app operations:
  P3-1: Switch to Chrome → verify
  P3-2: Switch to Obsidian → verify
  P3-3: Switch to Notepad → verify
  P3-4: Switch to Discord → verify
  P3-5: Switch to Explorer → verify
  P3-6: Switch to LINE → verify
  P3-7: Switch to VS Code → verify
  P3-8: Switch to Calculator → verify

[P4-Finalize]
  P4-1: Screenshot full desktop → all 8 apps running?
  P4-2: FileSystem list → test artifacts exist?
  P4-3: read_file → content correct?
  P4-4: ffprobe recording → valid?
  P4-5: Generate TEST-REPORT.md
  P4-6: Copy all artifacts to C:\Users\PP\Desktop\hermes-v8-test-YYYY-MM-DD\
```

### 6.2 失敗處理 ForEach 步驟

```
FOR EACH STEP:
  1. 截圖 before (screenshots/phase{N}/step{NN}-before.png)
  2. 執行操作
  3. Wait(0.5) 讓 UI 穩定
  4. 截圖 after (screenshots/phase{N}/step{NN}-after.png)
  5. vision_analyze("此操作結果正確嗎？")
  6. IF PASS → 繼續下一步
  7. IF FAIL:
     a. Level 1: 重試 1 次（同方案）
     b. IF 仍 FAIL: Level 2: 換方案（查決策表）
     c. IF 仍 FAIL: Level 3: 跳過，記錄到 failures.jsonl
  8. 記錄 timing 到 timing.jsonl
```

---

## Appendix A: 工具選擇速查表

```
情境                   最優工具                    備註
─────────────────────────────────────────────────────────
啟動 APP               terminal("start X")          PATH 確認
聚焦視窗               App(mode="switch", ...)      完整標題（script 先查）
四象限 Snap            Shortcut("win+arrow")        先半再象限，Wait(1)
位址列導航             Ctrl+L → Clipboard+V → Enter 最穩，無座標依賴
搜尋                  web_search (API)              永不 browser 進搜尋引擎
讀取網頁內容          web_extract                    更快更穩
檔案寫入              FileSystem(mode="write")      事後 cat 確認
螢幕驗證              Screenshot → vision_analyze   唯一真相
條件等待              WaitFor                        取代固定 Wait
大量文字輸入          Clipboard set + Ctrl+V        取代 Type(loc)
鍵盤快捷              Shortcut                        0 token 最穩
關閉視窗              Ctrl+W 或關閉鈕 Click          禁用 Alt+F4
跨 APP 複製貼上      Clipboard set → Ctrl+C → Switch → Ctrl+V
腳本執行              terminal("python script.py")  背景模式 + notify
錄影                  ffmpeg -t N -f gdigrab        禁用 kill，用 -t
```

## Appendix B: V2→V8 改善衡量

```
指標           V2 (2026-07-04)    V8 Target     V8 Actual    Verdict
───────────── ───────────────── ───────────── ──────────── ────────
Duration       222s (3 agent)     <120s         ___s         [PASS/FAIL]
Success Rate   94% (15/16)        ≥98%          __%          [PASS/FAIL]
Steps          16                 48            __/48        [PASS/FAIL]
Parallelism    3                  6             __           [PASS/FAIL]
Apps           4                  8             __/8         [PASS/FAIL]
Screenshot     Partial            100%          __/48×2      [PASS/FAIL]
Auto Recovery  Manual             3-layer       __ levels    [PASS/FAIL]
Failures Log   None               failures.jsonl __ entries   [PASS/FAIL]
Quality Gates  0 gates            6 gates       __/6         [PASS/FAIL]
```
