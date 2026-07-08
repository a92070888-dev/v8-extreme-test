# V8 Extreme Test — 報告方案設計書

> 設計日期：2026-07-06
> 設計特工：Reporting Agent #2
> 適用場景：V8 極限壓力測試完整生命週期記錄

---

## 1. 日誌收集機制

### 1.1 各特工職責與產出格式

| 特工角色 | 產出格式 | 檔案名稱 | 內容 | 寫入時機 |
|:---------|:---------|:---------|:-----|:---------|
| **Frontend Operation Agent** | JSON Lines (.jsonl) | `execution-log.jsonl` | 每步操作：動作類型、座標/元素、時間戳、截圖路徑 | 每完成一步立即 append |
| **Verification Agent** | JSON | `verification-per-step.json` | 每個驗證點：比對結果、差異分析、PASS/FAIL | 每次驗證完成後 |
| **V8 Monitor Agent** | JSON | `v8-state-log.json` | 系統狀態快照：記憶體、渲染、GC、FPS | 每30秒或每次操作後 |
| **Recording Agent** | MP4 檔案 + JSON | `recording-{step-n}.mp4` | 螢幕錄影片段，附 metadata JSON | 每步測試前→後 |
| **Orchestrator** | JSON | `test-plan.json` (預先) / `test-results-summary.json` (最終) | 測試計畫定義 + 最終彙整 | 開始前寫 plan，結束後寫結果 |
| **Screenshot Manager** | PNG files | `screenshot-{step-n}-{timestamp}.png` | 每步操作前後的螢幕截圖 | 操作前 captcha 驗證 / 操作後確認 |

### 1.2 日誌目錄結構

```
~/Desktop/v8-extreme-test-<yyyy-mm-dd>/
├── test-plan.json                 # 測試計畫（Orchestrator 預先產出）
├── execution-log.jsonl            # 操作執行日誌（Frontend Op Agent）
├── verification-per-step.json     # 每步驗證結果（Verification Agent）
├── v8-state-log.json              # V8 狀態變化（V8 Monitor Agent）
├── recording-metadata.json        # 錄影檔案清單 + metadata
├── reports/
│   ├── summary-report.md          # Markdown 摘要報告（可讀）
│   ├── summary-report.html        # HTML 圖文報告（可互動瀏覽）
│   └── summary-report.json         # JSON 機器可讀報告（給 CI / 記憶用）
├── screenshots/                   # 截圖檔案
│   ├── step-01-before.png
│   ├── step-01-after.png
│   └── ...
└── recordings/                    # 螢幕錄影
    ├── recording-step-01.mp4
    ├── recording-step-01.json     # metadata: 路徑、時間、長度、解析度
    └── ...
```

### 1.3 JSONL 格式規範（execution-log.jsonl）

每行一個 JSON object，不換行：

```jsonl
{"step":1,"action":"click","element":"button#start","loc":[450,320],"timestamp":"2026-07-06T14:30:01.123Z","screenshot":"screenshots/step-01-after.png","duration_ms":2450,"status":"success"}
{"step":2,"action":"type","element":"input#query","text":"v8 test query","timestamp":"2026-07-06T14:30:03.568Z","screenshot":"screenshots/step-02-after.png","duration_ms":800,"status":"success"}
```

### 1.4 Verification JSON 格式

```json
{
  "test_id": "v8-extreme-20260706",
  "total_steps": 12,
  "verifications": [
    {
      "step": 1,
      "type": "element_exists",
      "expected": "button#start",
      "actual": "found",
      "screenshot_path": "screenshots/step-01-after.png",
      "result": "PASS",
      "notes": ""
    },
    {
      "step": 2,
      "type": "text_match",
      "expected": "Results: OK",
      "actual": "Results: OK",
      "result": "PASS",
      "notes": ""
    }
  ],
  "summary": {
    "total": 12,
    "passed": 11,
    "failed": 1,
    "pass_rate": "91.67%"
  }
}
```

### 1.5 V8 Monitor JSON 格式

```json
[
  {
    "timestamp": "2026-07-06T14:30:01.123Z",
    "step": 1,
    "state": {
      "heap_used_mb": 245.3,
      "heap_total_mb": 512.0,
      "gc_pause_ms": 12.5,
      "fps": 58,
      "render_time_ms": 16.7,
      "memory_delta_mb": 0
    }
  },
  {
    "timestamp": "2026-07-06T14:30:05.456Z",
    "step": 2,
    "state": {
      "heap_used_mb": 267.8,
      "heap_total_mb": 512.0,
      "gc_pause_ms": 45.2,
      "fps": 55,
      "render_time_ms": 18.1,
      "memory_delta_mb": 22.5
    }
  }
]
```

---

## 2. 最終報告結構

### 2.1 測試摘要

- 測試名稱 / ID
- 測試日期時間
- 執行總時長
- 測試範圍（多少步驟、多少頁面/功能）
- 最終結果：✅ 全部通過 / ⚠️ 部分失敗 / ❌ 失敗
- Pass Rate

### 2.2 每步操作結果

| 步驟 | 動作 | 目標元素 | 耗時 | 驗證結果 | 截圖 | 錄影 |
|:----:|:----:|:---------|:----:|:--------:|:----:|:----:|
| 1 | click | button#start | 2.45s | ✅ PASS | 📸 link | 🎬 link |
| 2 | type | input#query | 0.80s | ✅ PASS | 📸 link | 🎬 link |
| ... | ... | ... | ... | ... | ... | ... |

### 2.3 V8 狀態變化

- **圖表化呈現**（若 HTML 報告）：Heap Memory 趨勢圖、GC Pause 分佈、FPS 變化
- **表格呈現**（若 Markdown）：每個檢查點的記憶體/GC/渲染狀態
- **異常標註**：任何超過閾值的狀態變化（如 GC > 100ms、FPS < 30）以 ⚠️ 標記

### 2.4 驗證結果

- 彙整所有驗證點的 PASS/FAIL 計數
- 每項驗證的具體比對：expected vs actual
- 失敗項目的詳細說明與 root cause 推測

### 2.5 錄影與截圖連結

- 每步操作的錄影片段（相對路徑）
- 關鍵時刻的截圖（操作前/後）
- 注意：這些檔案是 local 檔案，在報告中以相對路徑呈現

### 2.6 簽核狀態

由 V8 架構師/QA 負責人簽核：

```
## 簽核記錄

| 角色 | 簽核人 | 簽核日期 | 狀態 | 備註 |
|:----|:------:|:--------:|:----:|:-----|
| Architect | ________ | ________ | ⬜ Pending | |
| QA Lead   | ________ | ________ | ⬜ Pending | |
| Product   | ________ | ________ | ⬜ Pending | |
```

---

## 3. 報告格式

採用三格式並存策略：

### 3.1 Markdown（主要報告）
- 給人類閱讀，包含所有表格 + 連結 + 註解
- 可直接用 Obsidian 或任何 Markdown viewer 開啟
- 檔案：`reports/summary-report.md`

### 3.2 HTML（互動版本）
- 由 `summary-report.json` 自動生成
- 包含 CSS 美化樣式、JavaScript 圖表（Chart.js 嵌入）
- V8 狀態趨勢用 Line Chart 視覺化
- 可折疊的步驟明細、篩選 PASS/FAIL
- 檔案：`reports/summary-report.html`

### 3.3 JSON（機器可讀）
- 給 CI/CD 管線、Hermes 記憶系統、跨報告比較用
- 結構化資料，包含所有欄位
- 檔案：`reports/summary-report.json`

---

## 4. 報告存檔位置

### 4.1 即時路徑

```
~/Desktop/v8-extreme-test-<yyyy-mm-dd>/reports/
```

符合 Context 指定的 save location。測試結束後可移至永久存檔目錄。

### 4.2 永久存檔（選項）

```bash
# 移至永久的 Hermes 測試記錄區
mv ~/Desktop/v8-extreme-test-<yyyy-mm-dd> ~/hermes-v4/test-reports/
```

### 4.3 檔案命名規則

```
v8-extreme-summary-<yyyy-mm-dd>.md
v8-extreme-summary-<yyyy-mm-dd>.html
v8-extreme-summary-<yyyy-mm-dd>.json
v8-extreme-recording-manifest-<yyyy-mm-dd>.json
```

---

## 5. Hermes 記憶保留

### 5.1 記憶儲存策略

使用 Hermes `memory` 系統保留測試結果摘要：

| 記憶類型 | 內容 | 用途 |
|:---------|:-----|:------|
| **測試摘要** | 測試日期、步驟數、Pass Rate、關鍵失敗 | 快速查詢歷史測試結果 |
| **效能基線** | 每個步驟的平均耗時、V8 heap 範圍 | 後續測試的效能比較基線 |
| **失敗模式** | 重複出現的失敗類型、root cause | 預防性 QA、自動修復 |

### 5.2 記憶條目範例

```
記憶 1: "測試摘要 | V8 Extreme Test 2026-07-06: 12步, 91.67% pass, 1 failed (step 7: button#submit not found)"
記憶 2: "效能基線 | V8 Extreme Test 2026-07-06: avg step duration 1.8s, heap range 245-310MB, avg FPS 56"
記憶 3: "失敗模式 | V8 Extreme Test 2026-07-06: step 7 button#submit not found - DOM not fully loaded, need waitForElement"
```

### 5.3 JSON 報告 → Hermes 記憶的對應

當測試結束後，Reporting Agent 會：

1. 讀取 `reports/summary-report.json`
2. 提取摘要資料（日期、pass rate、步驟數、失敗清單）
3. 以 3 筆記憶條目寫入 Hermes `memory`
4. 記憶條目標題使用自然中文分類：「測試摘要 |」、「效能基線 |」、「失敗模式 |」

### 5.4 跨測試趨勢分析

每次新測試完成後，可透過 session_search 查詢歷史測試結果：
- `session_search(query="測試摘要 | V8 Extreme Test")`
- 比對每次的 Pass Rate、平均耗時、heap 使用量
- 發現退化（regression）趨勢

---

## 6. 報告生成自動化流程

```
測試結束
    │
    ▼
[Reporting Agent] 讀取所有日誌檔案
    ├── execution-log.jsonl         → 步驟明細
    ├── verification-per-step.json  → 驗證結果
    ├── v8-state-log.json           → 狀態變化
    ├── recording-metadata.json     → 錄影資訊
    │
    ▼
[Reporting Agent] 產生三格式報告
    ├── reports/summary-report.md   ← 人讀
    ├── reports/summary-report.html ← 互動
    └── reports/summary-report.json ← 機器
    │
    ▼
[Reporting Agent] 寫入 Hermes 記憶
    └── 3 筆記憶條目（摘要、基線、失敗模式）
```

---

## 7. 模板檔案

以下為對應的模板檔案，請參閱：
- `C:\Users\PP\Desktop\v8-extreme-test-report-design\templates\report-template.md` — Markdown 報告模板
- `C:\Users\PP\Desktop\v8-extreme-test-report-design\templates\report-template.html` — HTML 報告模板
- `C:\Users\PP\Desktop\v8-extreme-test-report-design\templates\report-schema.json` — JSON 報告 schema
