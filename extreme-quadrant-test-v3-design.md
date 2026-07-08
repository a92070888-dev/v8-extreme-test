# Multi-Agent Quadrant Test v3.0 — 「極致」方案設計書

> 測試架構師 #2 (Test Architect #2) · 基於 v2.0 經驗反饋的改進方案
> 日期：2026-07-06 | 版本：3.0.0（草案）

---

## 目錄

1. [上一輪回顧：v2.0 的成就與缺口](#1-上一輪回顧v20-的成就與缺口)
2. [「極致」的定義：量化目標](#2-極致的定義量化目標)
3. [V8 系統監控層整合](#3-v8-系統監控層整合)
4. [持續運行不卡住：反飢餓機制](#4-持續運行不卡住反飢餓機制)
5. [強制截圖驗證：Evidence Chain](#5-強制截圖驗證evidence-chain)
6. [測試場景矩陣](#6-測試場景矩陣)
7. [執行流程與排程策略](#7-執行流程與排程策略)
8. [成功標準與報告格式](#8-成功標準與報告格式)
9. [陷阱清單（累積版）](#9-陷阱清單累積版)

---

## 1. 上一輪回顧：v2.0 的成就與缺口

### 成就

| 指標 | v2.0 (2026-07-04) |
|:-----|:-----------------:|
| Agents 數 | 6/6 ✅ PASS |
| 測試 APP | Chrome, Notepad, Explorer, Discord (4 種) |
| 測試類別 | 象限佈局 + 平行壓力 + Delegation 鏈 |
| 總操作步數 | ~30 步 |
| 檔案產出 | test.txt + full-test-report.txt (679B) |
| 螢幕錄影 | multi-agent-full-test-20260704.mp4 |

### 缺口分析

| 項目 | v2.0 缺失 | 後果 |
|:-----|:----------|:-----|
| **APP 廣度** | 只測了 4 種基礎 APP | 未涵蓋 Office、Steam、開發工具 |
| **系統監控** | 無任何系統層監控 | 不知道測試期間的 CPU/RAM/磁碟壓力 |
| **卡住處理** | Notepad 卡住多次，無自動恢復 | 依賴使用者手動修正 |
| **截圖驗證** | 無強制每步截圖 | 少數步驟靠推論而非證據 |
| **重複次數** | 單次執行 | 無法確認結果穩定性 |
| **故障注入** | 無 | 無法測試容錯能力 |
| **象限自動化** | 部分手動（使用者拖四向線） | 不夠全自動 |
| **報告深度** | PASS/FAIL 二值 | 無時間/資源消耗/成功率細項 |

### v2.0 記錄的關鍵陷阱（直接沿用）

1. **Google reCAPTCHA** → 所有搜尋引擎觸發反爬，強制使用 web_search API
2. **Win+Arrow Wait 間隔** → 半 snap 後必須 Wait(2) 再 quadrant snap
3. **Screenshot false negatives** → 「No windows found」是假的，vision_analyze 為王
4. **Discord 6+ processes** → App(switch) 難命中，改用 taskbar click
5. **App(switch) 完整標題** → 必須從 Snapshot 取得完整視窗名稱，不能用 Python
6. **Notepad 路徑** → 不在 PATH，用 `start notepad` 或完整路徑
7. **Chrome 焦點被搶** → 測試前 `taskkill /f /im chrome.exe` 再重開
8. **已 snap 的視窗** → 先 Win+Down 浮動再重新 snap，否則 Win+Left 無效
9. **Chrome 自訂標題列不支援 Snap Layout flyout** → 一定要用鍵盤快捷鍵
10. **cc-switch 假陽性** → 用「檔案總管」而非「desktop」做關鍵字

---

## 2. 「極致」的定義：量化目標

### 覆蓋度提升

| 維度 | v2.0 | v3.0 極致目標 | 提升倍數 |
|:-----|:----:|:-------------:|:--------:|
| APP 數量 | 4 | **12** | **3x** |
| Agent 數量 | 6 | **12** (4×3) | **2x** |
| 測試回合 | 1 | **3** (連續) | **3x** |
| 操作步數 | ~30 | ~120 | **4x** |
| 截圖驗證 | 選用 | **強制每步** | ∞ |
| 系統監控 | 無 | **即時** | ∞ |
| 自動恢復 | 無 | **有** | ∞ |

### APP 擴增矩陣（12 個 APP）

| 象限 | APP | 啟動方式 | 測試重點 |
|:----:|:----|:---------|:---------|
| **Q1** | Chrome | `terminal('start chrome')` | 瀏覽器導航、CAPTCHA 規避 |
| **Q1** | Notepad | `terminal('start notepad')` | 文字編輯、中文輸入 |
| **Q1** | File Explorer | `terminal('start explorer')` | 檔案操作、導航路徑 |
| **Q2** | Discord | taskbar click | 通訊、多 process 切換 |
| **Q2** | Steam | `terminal('start steam')` | 遊戲平台、長啟動 |
| **Q2** | PowerShell ISE | `terminal('start powershell_ise.exe')` | 開發工具、腳本執行 |
| **Q3** | Obsidian | `terminal('start obsidian')` | 筆記應用、知識庫搜尋 |
| **Q3** | Calculator | `App(launch, 'calculator')` | 基礎 UWP APP |
| **Q3** | FxSound | `App(launch, 'fxsound')` | 音效工具、後台常駐 |
| **Q4** | Task Manager | `Shortcut('ctrl+shift+esc')` | 系統工具、行程管理 |
| **Q4** | Spotify | `terminal('start spotify')` | 多媒體、串流 |
| **Q4** | Settings | `Shortcut('win+i')` | 系統設定、搜尋測試 |

### 象限佈局（1920×1080）

```
┌──────────────────────────────────────────────┐
│  Q1 (x:0-960, y:0-540)   │  Q2 (x:960-1920, y:0-540) │
│  Chrome                    │  Discord                   │
│  Notepad                   │  Steam                     │
│  File Explorer             │  PowerShell ISE            │
├────────────────────────────┼────────────────────────────┤
│  Q3 (x:0-960, y:540-1080) │  Q4 (x:960-1920, y:540-1080)│
│  Obsidian                  │  Task Manager              │
│  Calculator                │  Spotify                   │
│  FxSound                   │  Settings                  │
└──────────────────────────────────────────────┘
```

策略：輪流將 3 個 APP 放入同一象限（每個 APP 測試 1 分鐘，輪換），而非同時放 12 個。

---

## 3. V8 系統監控層整合

### 架構

```
┌──────────────────────────────────────────────┐
│  Multi-Agent Test Orchestrator (v3.0)         │
├──────────────────────────────────────────────┤
│  ┌─────────────┐  ┌────────────────────────┐ │
│  │ Agent Pool   │  │ V8 System Monitor     │ │
│  │ (12 agents)  │  │ (background thread)   │ │
│  └──────┬──────┘  └───────────┬────────────┘ │
│         │                     │               │
│         ▼                     ▼               │
│  ┌─────────────────────────────────────────┐  │
│  │  Evidence Chain (per-step screenshots)  │  │
│  └─────────────────────────────────────────┘  │
└──────────────────────────────────────────────┘
```

### V8 Monitor 實作

執行於背景 process（`terminal(background=true, notify_on_complete=false)`），每 30 秒收集一次系統指標：

```bash
# v8_system_monitor.sh — 每 30 秒記錄一次系統狀態
while true; do
  TIMESTAMP=$(date '+%H:%M:%S')
  
  # CPU 使用率
  CPU=$(powershell -NoProfile -Command \
    "Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average | Select -ExpandProperty Average")
  
  # 記憶體
  MEM=$(powershell -NoProfile -Command \
    "$os=Get-CimInstance Win32_OperatingSystem; \
     $total=[math]::Round($os.TotalVisibleMemorySize/1024/1024,1); \
     $free=[math]::Round($os.FreePhysicalMemory/1024/1024,1); \
     Write-Host \"$free/$total\"")
  
  # 磁碟（C: 可用空間 GB）
  DISK=$(powershell -NoProfile -Command \
    "Get-CimInstance Win32_LogicalDisk -Filter 'DeviceID=\"C:\"' | \
     Select -ExpandProperty FreeSpace | ForEach-Object {[math]::Round($_/1GB,1)}")
  
  # Top 5 行程（記憶體）
  TOP5=$(powershell -NoProfile -Command \
    "Get-Process | Sort-Object WorkingSet64 -Desc | \
     Select -First 5 Name,@{N='MB';E={[math]::Round(\$_.WorkingSet64/1MB,1)}} | \
     Format-Table -HideTableHeaders | Out-String")
  
  # 寫入日誌（CSV 格式，後續可用 Excel 分析）
  echo "$TIMESTAMP,CPU=$CPU,MEM=$MEM,DISK=${DISK}GB"
  
  sleep 30
done
```

### 監控指標

| 指標 | 觸發閾值 | 動作 |
|:-----|:---------|:-----|
| CPU > 90% | 持續 2 分鐘 | 暫停非必要 agent，等 CPU 降回 < 70% |
| 記憶體可用 < 2GB | 持續 1 分鐘 | 關閉閒置 APP，釋放記憶體 |
| 磁碟 < 5GB | 即時 | 停止測試（避免系統不穩） |
| 單一行程記憶體 > 2GB | 即時 | 記錄異常行程資訊 |

### 整合方式

1. **啟動測試時** → `terminal(background=true, command="bash v8_system_monitor.sh")`
2. **每 5 步** → 讀取 monitor 日誌，確認系統健康
3. **異常觸發** → 自動調整測試步伐（暫停→降載→恢復）
4. **測試結束** → 收集完整監控日誌作爲報告附件

### Cronjob 健康度對照

V8 Monitor 即時監控與 `hermes-system-cron` 的「Windows 系統健康度」每日 08:00 排程不衝突：
- V8 Monitor → 測試期間即時、高頻 (30s)
- Cron 健康度 → 日常一次性、低頻 (24h)
- 兩者使用相同的 `collect_health_metrics.py` 腳本核心

---

## 4. 持續運行不卡住：反飢餓機制

### 問題回顧

v2.0 Notepad 卡住多次的原因：
1. Notepad 無對應進程（`terminal('start notepad')` 失敗）
2. App(switch) 找不到「記事本」因為標題含中文
3. 卡住後無 timeout 機制
4. 無自動恢復路徑

### v3.0 反飢餓策略

#### 4.1 全局 Timeout（傘式保護）

每個操作步驟設「硬上限」：
```
browser_navigate       → 15s timeout
browser_click         → 10s timeout
App(switch)           → 8s timeout
Shortcut              → 5s timeout (快捷鍵很穩)
FileSystem(mode=...)  → 10s timeout
terminal(command)     → 30s timeout (對啟動慢的 APP)
```

實作方式：MCP 工具調用前先 `timeout` 包裝不可行（MCP 不在 shell 中），改爲在 Python wrapper 中用 `asyncio.wait_for()` 實現：

```python
import asyncio

async def mcp_call_with_timeout(tool_func, timeout=15, **kwargs):
    """包裝 MCP 調用，超時自動拋出"""
    try:
        return await asyncio.wait_for(
            tool_func(**kwargs), timeout=timeout
        )
    except asyncio.TimeoutError:
        return {"status": "TIMEOUT", "tool": tool_func.__name__, "args": kwargs}
```

#### 4.2 Agent 級 Timeout（次級傘）

每個 delegate_task 設 **120 秒硬上限**：
- 超過 120 秒 → 強制終止該 agent
- 記錄 partial 結果（已經完成的步驟還是有效）
- 不影響其他 agent

#### 4.3 自動恢復路徑

| 卡住情境 | 偵測方式 | 恢復動作 |
|:---------|:---------|:---------|
| Notepad 未啟動 | FileSystem 寫入後 read_file 無內容 | `terminal('start notepad')` → Wait(3) → 重試 |
| Chrome 被 CAPTCHA 擋 | browser_snapshot 含 "unusual traffic" | 跳過 browser，改用 web_search API |
| Discord 無法切換 | Screenshot 無 Discord 視窗 | Click(taskbar, discord icon) |
| 某 APP 進程消失 | process(list) 找不到 | 重新 launch → Wait(3) |
| Screenshot 回傳 empty | 輸出無 image_path | Wait(1) → 重試 Screenshot（最多 3 次） |

#### 4.4 批次節奏控制

v2.0 卡住的根本原因：所有操作連續發出，沒有節奏控制。

v3.0 強制每步間隔：
```
每步後 → 強制 Wait(1) → 強制 Screenshot（證據） → 分析結果 → 下一步
```

操作密集區（如 Win+Arrow 序列）：用 `Wait(2)` 替代 `Wait(1)`。

#### 4.5 最大重試次數（防止無限循環）

| 層級 | 最大重試 | 超過後 |
|:-----|:--------:|:-------|
| 單步驟 | 3 次 | 跳過該步驟，記錄 FAIL |
| 單 Agent | 5 次 | 該 Agent 標 FAIL，不影響其他人 |
| 整體 | 10 次 | 終止整個測試 |

---

## 5. 強制截圖驗證：Evidence Chain

### 設計原則

**每個操作步驟都必須有 Screenshot 證據。** 不接受任何文字推論或工具回傳值作爲操作完成的唯一證據。

### Evidence Chain 結構

```
Step N:
  ├── Action: 執行的工具調用 + 參數
  ├── Result: 工具回傳值（文字）
  ├── Screenshot: 操作後的桌面截圖 (image_path)
  ├── Vision Analysis: 截圖中實際發生的狀況
  ├── Verdict: PASS / FAIL / PARTIAL
  └── Timestamp: HH:MM:SS
```

### 強制流程（Agent 層級）

每個 Agent 的任務 prompt 開頭必須包含：

```
=== 強制操作規則 ===
你必須嚴格遵守以下規則：

1. 每完成一個操作（browser_navigate/click/type/App/Screenshot/Shortcut），
   立即用 Screenshot() 截圖。
   
2. 用 vision_analyze() 確認截圖內容：
   - 確認你預期的畫面是否出現
   - 如果截圖與預期不符，回答 FAIL 並嘗試修正
   - 如果 Screenshot 回傳 empty（No windows），Wait(1) 後重試
   - Screenshot 最多重試 3 次，仍空就回答 FAIL

3. 不接受以下說法作為操作成功證據：
   - ❌ "工具回傳 success"
   - ❌ "GetWindowRect 顯示座標是..."
   - ❌ "我已經完成了"
   ✅ Screenshot 上實際看得到的內容才是證據

4. 操作節奏：每步間強制 Wait(1)。
   Win+Arrow 序列：每步間強制 Wait(2)。
=====================
```

### 報告中的截圖管理

所有截圖集中存放到 `C:\Users\PP\Desktop\extreme-test-20260706\screenshots\`：

```
screenshots/
├── step-001-snap-Q1-chrome.png
├── step-002-snap-Q2-discord.png
├── step-003-browser-navigate-google.png
├── step-004-notepad-typing.png
└── ...
```

檔案命名規則：`step-{編號}-{動作}-{說明}.png`

### 驗證等級

| 等級 | 定義 | 要求 |
|:----|:-----|:-----|
| **VERIFIED** | 有截圖 + 截圖內容與預期一致 | Screenshot + vision_analyze 雙確認 |
| **PARTIAL** | 有截圖但內容部分不符 | Screenshot 存在，但預期畫面未完全出現 |
| **FAILED** | 無截圖 或 操作後無任何變化 | Screenshot 不存在或截圖內容完全錯誤 |
| **SKIPPED** | 依 recovery 策略跳過 | 記錄跳過原因和恢復動作 |

### 證據鏈自動化腳本

```python
# generate_evidence_report.py
# 讀取所有 screenshots/*.png，自動產生證據報告

import os, json
from datetime import datetime

SCREENSHOTS_DIR = "C:/Users/PP/Desktop/extreme-test-20260706/screenshots"
REPORT_FILE = "C:/Users/PP/Desktop/extreme-test-20260706/evidence-chain.json"

evidence = []
for f in sorted(os.listdir(SCREENSHOTS_DIR)):
    if f.endswith('.png'):
        # 從檔名解析步驟
        parts = f.replace('.png','').split('-')
        step_num = parts[1]
        action = '-'.join(parts[2:-1])
        desc = parts[-1]
        
        evidence.append({
            "step": int(step_num),
            "file": f,
            "action": action,
            "description": desc,
            "timestamp": datetime.fromtimestamp(
                os.path.getmtime(os.path.join(SCREENSHOTS_DIR, f))
            ).strftime('%H:%M:%S'),
            "filesize": os.path.getsize(os.path.join(SCREENSHOTS_DIR, f))
        })

with open(REPORT_FILE, 'w', encoding='utf-8') as f:
    json.dump({"total_screenshots": len(evidence), "steps": evidence}, 
              f, ensure_ascii=False, indent=2)

print(f"Generated evidence report: {REPORT_FILE}")
print(f"Total screenshots: {len(evidence)}")
```

---

## 6. 測試場景矩陣

### 批次 1：基礎操作驗證（6 Agents）

| Agent | 角色 | 操作 APP | 測試項目 | 成功條件 |
|:------|:-----|:---------|:---------|:---------|
| WebAgent | 瀏覽器操作 | Chrome | 導航到 github.com/nousresearch/hermes → 截取頁面標題 | browser_snapshot 頁面含 "Hermes" |
| NoteAgent | 文字編輯 | Notepad | 貼入 3 行中文測試報告 → Ctrl+S 存成 test-report.txt | read_file 驗證內容正確 |
| FileAgent | 檔案管理 | Explorer | 建立 5 層巢狀目錄 → 複製檔案 → 驗證存在 | FileSystem(list) 目錄結構完整 |
| CalcAgent | 計算機操作 | Calculator | 輸入 1024×768 → 截圖結果 | Screenshot 顯示計算結果 |
| SysAgent | 系統工具 | Task Manager | 打開 → 截圖行程清單 | Screenshot 顯示 Process list |
| DiscAgent | 通訊測試 | Discord | 打開 → 截圖 Discord 介面 | Screenshot 顯示 Discord UI |

### 批次 2：壓力與進階操作（6 Agents）

| Agent | 角色 | 操作 APP | 測試項目 | 成功條件 |
|:------|:-----|:---------|:---------|:---------|
| SteamAgent | 遊戲平台 | Steam | 啟動 → 等待登入畫面 → 截圖 | Screenshot 顯示 Steam UI |
| ObsidianAgent | 筆記測試 | Obsidian | 打開 → 搜尋筆記 → 截圖 | Screenshot 顯示 Obsidian 介面 |
| PowerAgent | 開發工具 | PowerShell ISE | 打開 → 編輯 Hello.ps1 → 執行 → 截圖 | Screenshot 顯示執行結果 |
| FxAgent | 音效 | FxSound | 啟動 → 確認常駐 → 截圖托盤圖示 | Screenshot 顯示 FxSound 主視窗 |
| MusicAgent | 多媒體 | Spotify | 啟動 → 等待載入 → 截圖 | Screenshot 顯示登入或主畫面 |
| ConfigAgent | 系統設定 | Settings | 打開 → 搜尋 "Bluetooth" → 截圖 | Screenshot 顯示設定視窗 |

### 批次 3：多輪一致性（3 輪 repeats）

將批次 1 和 2 合併，作為 1 輪完整測試，然後連續執行 3 輪：

```
Round 1: 批次 1 → 批次 2 → 清理
Round 2: 批次 1 → 批次 2 → 清理
Round 3: 批次 1 → 批次 2 → 清理
```

每輪結束後比對 Screenshot 數量、操作成功率、平均操作時間。

---

## 7. 執行流程與排程策略

### 總流程

```
Phase 0: 準備
  1. taskkill /f /im chrome.exe (清理舊 Chrome)
  2. terminal('start chrome')
  3. terminal('start notepad')
  4. terminal('start explorer')
  5. terminal('start discord')
  6. terminal('start steam')
  7. terminal('start obsidian')
  8. terminal('start spotify')
  9. App(launch, calculator)
  10. Wait(5) → 等所有 APP 載入
  11. 啟動 V8 System Monitor (background)

Phase 1: 象限佈局
  使用者手動拖 4 象限（5 秒）或自行設定的自動 snap 腳本
  → Screenshot 驗證佈局 ✓

Phase 2: 批次 1 — 6 Agents 平行
  delegate_task(tasks=[6 agents])

Phase 3: 批次 2 — 6 Agents 平行  
  delegate_task(tasks=[6 agents])

Phase 4: V8 Monitor 收尾 + 證據收集
  - 終止 monitor
  - 收集所有 Screenshots
  - 產生 evidence-chain.json
  - 產生測試報告

Phase 5: Round 2 (如果設定多輪)
  - 清理 Screenshots（或歸檔到 round2/ 子目錄）
  - 回到 Phase 0

Phase 6: 最終報告
  - 合併多輪數據
  - 產出對比分析
  - 更新 test.txt 為最新 PASS/FAIL
```

### 時間估算

| Phase | 預估時間 | 備註 |
|:------|:--------:|:-----|
| Phase 0: 準備 | ~60s | 啟動 12 APP + 監控 |
| Phase 1: 象限佈局 | ~15s | 使用者手動約 5s + 驗證 10s |
| Phase 2: 批次 1 | ~120s | 6 Agents 平行，最慢的操作決定總時間 |
| Phase 3: 批次 2 | ~120s | 同上 |
| Phase 4: 收尾 | ~30s | 證據收集 + 報告產生 |
| **1 輪總計** | **~345s (5.75min)** | |
| **3 輪總計** | **~1035s (17min)** | 不含清理時間 |

### 排程衝突避免

| 檢查點 | 動作 |
|:-------|:-----|
| 測試啟動前 | `hermes cron list` 確認沒有排程在未來 30 分鐘內觸發 |
| 每輪間隔 | 清理資源後 Wait(5) 再啟動下一輪 |
| 與系統排程錯開 | 避開每日 08:00 (健康度)、21:00 (Token 監控)、03:00 (系統優化) |
| 週五避開 10:00 | 避開鍵盤滑鼠優化排程 |

---

## 8. 成功標準與報告格式

### 成功判定矩陣

| 等級 | APP 成功率 | Agent 成功率 | 截圖驗證率 | 卡住次數 |
|:-----|:----------:|:------------:|:----------:|:--------:|
| 🏆 **極致 PASS** | ≥ 80% (10/12) | ≥ 83% (10/12) | 100% | ≤ 3 |
| ✅ PASS | ≥ 67% (8/12) | ≥ 67% (8/12) | ≥ 90% | ≤ 5 |
| ⚠️ PARTIAL | ≥ 50% (6/12) | ≥ 50% (6/12) | ≥ 75% | ≤ 7 |
| ❌ FAIL | < 50% | < 50% | < 75% | > 7 |

### 報告格式

```markdown
# Extreme Multi-Agent Quadrant Test v3.0

## 執行資訊
- 日期: 2026-07-06
- 開始時間: HH:MM:SS
- 結束時間: HH:MM:SS
- 總耗時: XX 分鐘
- 執行輪次: X/3

## 總體結果
- **等級**: 🏆 / ✅ / ⚠️ / ❌
- **APP 成功率**: XX/12 (XX%)
- **Agent 成功率**: XX/12 (XX%)
- **截圖驗證率**: XX/XX (XX%)
- **卡住次數**: X

## 各批次結果

### 批次 1（6 Agents）
| Agent | APP | 操作數 | PASS | FAIL | SKIP | 關鍵失敗原因 |
|:------|:----|:-----:|:----:|:----:|:----:|:-----------|
| WebAgent | Chrome | N | N | N | N | — |
| NoteAgent | Notepad | N | N | N | N | — |
| ... | ... | ... | ... | ... | ... | ... |

### 批次 2（6 Agents）
...

## 系統監控摘要

### V8 Monitor 記錄
| 指標 | 平均值 | 峰值 | 最低值 |
|:-----|:------:|:----:|:-----:|
| CPU | XX% | XX% | XX% |
| 記憶體 | XX/XX GB | — | XX GB |
| 磁碟 C: | XX GB | — | XX GB |

### 異常事件
- [事件 1] CPU > 90% 持續 2 分鐘 (HH:MM:SS)
- [事件 2] 記憶體 < 2GB (HH:MM:SS) → 自動降載
- ...

## 陷阱命中記錄
| # | 陷阱 | 命中? | 處理方式 |
|:-:|:-----|:-----:|:--------|
| 1 | Google reCAPTCHA | ✅ | 切換 web_search API |
| 2 | Discord 6+ processes | ⬜ | — |
| ... | ... | ... | ... |

## 多輪對比（如果執行 3 輪）
| 指標 | Round 1 | Round 2 | Round 3 | 趨勢 |
|:-----|:-------:|:-------:|:-------:|:----:|
| 耗時 | XXs | XXs | XXs | ↑↓→ |
| 成功率 | XX% | XX% | XX% | ↑↓→ |
| 截圖數 | N | N | N | ↑↓→ |

## 建議與改進
- 基於本次測試發現的改善點
```

---

## 9. 陷阱清單（累積版）

> 合併 v2.0 已知陷阱 + v3.0 新預測陷阱

| # | 陷阱 | 類別 | 發生概率 | 防禦策略 |
|:-:|:-----|:-----|:--------:|:---------|
| 1 | Google reCAPTCHA | 瀏覽器 | 高 (100%) | 切換 web_search API |
| 2 | Bing Cloudflare | 瀏覽器 | 高 | 同上，預期所有搜尋引擎都會擋 |
| 3 | DuckDuckGo 機器人檢測 | 瀏覽器 | 高 | 同上 |
| 4 | Win+Arrow 動畫未完成 | 象限 | 中 | Wait(2) 半 snap→quadrant 之間 |
| 5 | Screenshot false negatives | 截圖 | 中 | vision_analyze 為王，最多重試 3 次 |
| 6 | Discord 6+ processes | APP | 高 | App(switch) 失敗時改用 taskbar click |
| 7 | Chrome 焦點被搶 | APP | 高 | 測試前 taskkill chrome.exe 再重開 |
| 8 | 已 snap 的視窗 Win+Arrow 失效 | 象限 | 中 | 先 Win+Down 浮動 |
| 9 | Chrome 自訂標題列無 Snap Layout | 象限 | 中 | 強制用鍵盤快捷鍵 |
| 10 | cc-switch 假陽性 | APP | 低 | 用中文名稱而非英文關鍵字 |
| 11 | Notepad 不在 PATH | APP | 中 | 用 `start notepad`（v3.0 新增嚴謹） |
| 12 | Steam 啟動超慢 | APP | 高 | timeout 設 30s + 背景啟動 |
| 13 | Obsidian 啟動後需要載入 vault | APP | 中 | 啟動後 Wait(5) 再操作 |
| 14 | Spotify 需要登入 | APP | 高 | 預期會有登入畫面，截圖確認即可 |
| 15 | Settings/UWP 視窗難切換 | APP | 中 | 用 Shortcut("win+i") 開啟，App(switch) 用英文名 |
| 16 | FxSound 常駐托盤無主視窗 | APP | 高 | 確認 process exists 而非視窗可見 |
| 17 | PowerShell ISE 啟動位置在上方 | APP | 低 | 確認 process exists |
| 18 | Calculator UWP 無標題 | APP | 中 | 用 App(switch) 傳 "Calculator" |
| 19 | Hermes 介面遮擋桌面 | 環境 | 中 | 先 Shortcut("win+d") 顯示桌面 |
| 20 | Screenshot 密集導致隊列 | 截圖 | 中 | 每步之間 Wait(1) |
| 21 | V8 Monitor 腳本本身吃資源 | 監控 | 中 | 改用 PowerShell 排程模式而非 while true |
| 22 | 12 APP 同時啟動可能 OOM | 資源 | 中 | 按批次啟動，非全部同時 |
| 23 | 重試無限循環 | 穩定性 | 中 | 強制 max_retry=3 |
| 24 | 多輪測試結果交叉汙染 | 數據 | 中 | 每輪 Cleanup Screenshots |
| 25 | delegate_task 超過 max 3 | 平台 | 中 | 6 Agents 分 2 批發送 |

---

## 附錄 A：與 v2.0 skill 的相容性

v3.0 不取代 v2.0，而是建立平行版本 `multi-agent-quadrant-test-v3`。v2.0 保留作爲快速測試選項。

## 附錄 B：啟動腳本範本

```bash
# start-extreme-test.sh
# 放在 ~/Desktop/extreme-test-20260706/

# === Phase 0: 清理舊 Chrome ===
taskkill /f /im chrome.exe 2>/dev/null

# === 啟動 APP（分三批避免同時載入 OOM）===
# 批次 A：核心 4 APP
start chrome
start notepad
start explorer
start discord

# 等待核心 APP 載入
powershell -Command "Start-Sleep -Seconds 5"

# 批次 B：開發/遊戲
start obsidian
start steam
start spotify
start powershell_ise.exe

# 批次 C：系統工具
start ms-calculator:  # Calculator UWP URI scheme
start ms-settings:    # Settings UWP URI scheme
# FxSound 已在常駐

# === Phase 0: 建立 Screenshots 目錄 ===
mkdir -p screenshots

echo "All apps launched. Ready for quadrant layout."
```
