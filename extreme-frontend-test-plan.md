# 🧪 極致前端操作測試 — 完整測試計畫
> Test Architect #1 | Hermes V8 Framework | Windows 10
> 版本: v1.0 | 日期: 2026-07-06

---

## 1. 測試目標 — 什麼叫「極致」？

### 1.1 極致定義

「極致前端操作測試」是指在 **最低人工干預**、**最大平行度**、**最長操作鏈** 的條件下，驗證 Hermes Agent 的 Windows MCP 操作工具鏈能否可靠、高效、穩定地完成多 APP 聯合操作。

### 1.2 規格矩陣（逐步升級）

| 指標 | L1 入門 | L2 中等 | L3 進階 | L4 極致（目標） |
|:-----|:--------|:--------|:--------|:----------------|
| **同時操作 APP 數** | 4 | 6 | 6 | **8** |
| **並行程度** | 批次 2×2 | 批次 3×2 | 6 同時 | **6~8 同時** |
| **操作步驟總數** | 20 | 50 | 80 | **100** |
| **操作類型覆蓋** | 4 類 | 5 類 | 5 類 | **5 類全覆蓋** |
| **錯誤場景** | 0 | 1 | 2 | **3 類** |
| **預計耗時（分鐘）** | ~3 | ~8 | ~15 | **~20-25** |

**L4 極致定義：**
- **8 個 APP** 同時處於可操作狀態（象限+側邊欄+浮動視窗配置）
- **6~8 個子 AGENT 同時執行**，每批次直接派遣
- **100 步操作** 總和（含前置啟動、佈局、操作、驗證）
- **5 種操作類型** 全覆蓋（Click / Type / Shortcut / Snap / Drag）
- **3 種錯誤場景** 被誘發並成功處理

### 1.3 為什麼是 8 個 APP？

基於現有測試數據（3 AGENT 平行 222.5s、4 象限佈局經驗），8 個 APP 是 Windows 10 螢幕空間和人類管理能力的合理上限：

| 佈局 | APP | 位置策略 |
|:----|:----|:---------|
| 象限 (4) | Chrome, Notepad, Explorer, Obsidian | Win+Arrow 四象限 |
| 側欄 (2) | Discord, LINE | Win+Left/Right 窄側欄 |
| 浮動前景 (2) | Steam, Calculator | 前景切換操作 |

---

## 2. 測試覆蓋維度

### 2.1 APP 類型覆蓋（共 8 個）

| # | APP | 類型 | 啟動方式 | 操作特徵 |
|:-|:----|:-----|:---------|:---------|
| 1 | **Google Chrome** | 瀏覽器 | `terminal("start chrome")` | URL 導航、搜尋、網頁互動 |
| 2 | **Notepad** | 文字編輯 | `terminal("start notepad")` | 文字輸入、剪貼簿、存檔 |
| 3 | **File Explorer** | 檔案管理 | `terminal("start explorer")` | 路徑導航、檔案操作 |
| 4 | **Discord** | 通訊 | 任務列 Click | 聊天輸入、頻道操作 |
| 5 | **Obsidian** | 知識庫 | `terminal("start obsidian")` | 筆記建立、搜尋、連結 |
| 6 | **Steam** | 遊戲平台 | `terminal("start steam")` | 畫面驗證、狀態檢視 |
| 7 | **LINE** | 通訊 | 任務列 Click | 訊息輸入、貼圖驗證 |
| 8 | **Calculator** | 工具 | `terminal("start calc")` | 數學輸入、結果驗證 |

**APP 類型多樣性原理：**
- **瀏覽器類**（Chrome）：最複雜的 UI，自訂標題列，reCAPTCHA 風險
- **原生工具類**（Notepad, Calculator）：最簡單的 Win32 視窗，高穩定性
- **檔案操作類**（Explorer）：需要 Shell 導航和樹狀結構理解
- **Electron 類**（Discord, Obsidian）：非原生渲染，UIA 樹可能不完整
- **遊戲平台類**（Steam）：特殊渲染，大圖形介面
- **通訊類**（LINE）：日系應用，視窗行為可能不同

### 2.2 操作類型覆蓋（5 大類）

#### A. Click（點擊）
- **左鍵點擊**：按鈕、連結、輸入框
- **雙擊**：檔案開啟（Explorer）
- **右鍵**：快捷選單（Notepad 貼上選項）
- **座標模式**：無 UIA 元素時（Discord 自訂元件）
- **標籤模式**：UIA 元素可用時（Notepad 編輯區）

#### B. Type（鍵入）
- **清除+輸入**：Notepad 編輯、計算機輸入
- **多行輸入**：Clipboard set + Ctrl+V（批次取代逐行 Type）
- **特殊鍵**：Tab 跳格、Enter 提交
- **壓力測試**：大量重複 Type（模擬打字疲勞）

#### C. Shortcut（快捷鍵）
- **應用切換**：Ctrl+L（Chrome 網址列）、Win+Arrow（視窗 Snap）
- **系統快捷**：Alt+Tab（視窗切換）、Win+D（顯示桌面）
- **編輯快捷**：Ctrl+C/V/X/A（剪貼簿操作）
- **儲存**：Ctrl+S（Notepad/Obsidian 存檔）

#### D. Snap（視窗捕捉）
- **Win+Arrow 四象限**：Q1~Q4 標準排列
- **Win+Left/Right 半屏**：側欄配置
- **Win+Up/Down**：最大化/還原（Snap 前恢復浮動狀態）
- **Snap Layout 注意**：Chrome 自訂標題列不支援，只用快捷鍵

#### E. Drag（拖曳）
- **標題列拖曳**：MCP Move(drag=True) 移動視窗
- **檔案拖放**：Explorer 內拖放檔案
- **選取拖曳**：文字選取區域拖曳（Notepad 選擇）
- **已知限制**：Windows 標題列拖曳需要 WM_NCLBUTTONDOWN，MCP drag 可能無效；改用 Win+Arrow 取代

### 2.3 操作分配總表（100 步）

| 操作類型 | 步數 | 佔比 | 分配 |
|:---------|:-----|:-----|:-----|
| Click | 35 | 35% | 每 APP 平均 4-5 次 |
| Type | 25 | 25% | 文字/計算機輸入 |
| Shortcut | 20 | 20% | 導航/切換/Snap |
| Snap | 12 | 12% | 佈局排列 |
| Drag | 8 | 8% | 視窗/檔案 |
| **總計** | **100** | **100%** | |

### 2.4 錯誤場景覆蓋（3 類必測）

#### E1. CAPTCHA / 反爬機制
- **觸發方式**：`browser_navigate` 進 Google/DuckDuckGo 搜尋
- **期望行為**：偵測到 CAPTCHA → 自動降級為 `web_search` API
- **驗證方法**：搜尋仍成功取得結果
- **參考數據**：2026-07-04 測試中 Google 和 DuckDuckGo 均觸發 CAPTCHA

#### E2. Timeout / 操作無響應
- **觸發方式**：
  - 啟動一個不存在/崩潰的 APP（如 `terminal("start nonexistent_app.exe")`）
  - 對無響應視窗發送操作（前景有 modal 對話框）
- **期望行為**：2 次重試後匯報 Timeout，記錄錯誤原因
- **驗證方法**：測試報告中有 Timeout 記錄且不影響後續操作

#### E3. APP 崩潰 / 不正常關閉
- **觸發方式**：用 Process(kill) 強制結束正在操作的 APP
- **期望行為**：AGENT 偵測到 APP 消失 → 重新啟動 → 繼續操作
- **驗證方法**：APP 被重新啟動並完成原本的操作

---

## 3. PASS/FAIL 標準

### 3.1 評分系統（加權）

| 計分項 | 權重 | 滿分 | 說明 |
|:-------|:-----|:-----|:-----|
| 操作成功率 | 40% | 40 分 | 成功步數 / 總步數 × 40 |
| APP 存活率 | 15% | 15 分 | 測試結束時仍在運行的 APP 數 / 8 × 15 |
| 錯誤處理率 | 20% | 20 分 | 成功處理的錯誤場景 / 3 × 20 |
| 耗時效率 | 15% | 15 分 | ≤20min 得 15, ≤25min 得 10, >25min 得 5 |
| 視覺驗證完整 | 10% | 10 分 | 每完成一個 Checkpoint 截圖驗證 |

### 3.2 PASS / FAIL 判定

| 等級 | 總分 | 評語 |
|:-----|:-----|:-----|
| **🏆 EXCELLENT** | ≥95 | 極致操作通過 — 系統達到生產就緒 |
| **✅ PASS** | ≥80 | 通過 — 操作鏈可靠，可考慮上線 |
| **⚠️ MARGINAL** | ≥60 | 邊緣 — 需要改善特定弱項 |
| **❌ FAIL** | <60 | 失敗 — 操作鏈存在致命問題 |

### 3.3 關鍵 PASS 條件（硬性門檻）

**以下任一條件不滿足即直接 FAIL，不看總分：**

1. **操作成功率 < 70%** — 超過 30 步失敗
2. **連續操作失敗 > 3** — 同一操作類型連續失敗
3. **所有 CAPTCHA 場景皆失敗** — 無法處理任何搜尋引擎
4. **APP 喪失 > 4 個** — 超過一半 APP 崩潰或無法重啟
5. **未記錄測試結果** — 沒有 Screenshot 或報告檔案

### 3.4 各操作類型最低成功率

| 操作類型 | 最低成功率 | 連續失敗上限 |
|:---------|:-----------|:-------------|
| Click | 85% | 3 |
| Type | 90% | 2 |
| Shortcut | 95% | 1 |
| Snap | 90% | 2 |
| Drag | 70% | 3 |

---

## 4. 測試執行流程

### Phase 0: 前置準備（~2 min）

```
1. 確認 MCP Windows tools 可用
2. 清理桌面（Close all non-essential apps）
3. 設置測試目錄
   mkdir -p ~/Desktop/test-extreme/{web,desktop,office,comm,games,reports}
4. 準備測試資料（文字樣本、URL 清單、數學算式）
5. 啟動 ffmpeg 螢幕錄影（-t 900 = 15 min capture）
```

### Phase 1: APP 啟動與佈局（~3 min）

```
1. Launch 8 apps（順序啟動，避免資源競用）
2. Win+Arrow 排列 4 象限 + 側欄
3. 視覺驗證佈局（Screenshot + vision_analyze）
```

### Phase 2: 主操作鏈（~12 min）

```
批次 1（3 AGENT）：Chrome + Notepad + Calculator
批次 2（3 AGENT）：Explorer + Obsidian + Discord
批次 3（2 AGENT）：LINE + Steam（+ 錯誤場景注入）
```

### Phase 3: 錯誤場景注入（~3 min）

```
E1: CAPTCHA — 在 Phase 2 中 Natural 觸發
E2: Timeout — 在批次 3 中故意觸發
E3: App Crash — Process(kill) 目標 APP → 驗證重啟
```

### Phase 4: 驗證與報告（~3 min）

```
1. 檢查所有檔案產出
2. 檢查每 APP 存活狀態
3. 檢查螢幕錄影完整性
4. 生成測試報告
5. 計算 PASS/FAIL 分數
```

---

## 5. 測試交付物

### 5.1 必須交付

| # | 交付物 | 格式 | 說明 |
|:-|:-------|:-----|:-----|
| 1 | **測試執行報告** | Markdown | `test-extreme-report-YYYY-MM-DD.md`，含完整分數計算 |
| 2 | **操作日誌** | JSON | `operation-log.json`，含每步時間戳、操作、結果 |
| 3 | **螢幕錄影** | MP4 | `test-recording-YYYY-MM-DD.mp4`，完整測試過程 |
| 4 | **錯誤場景記錄** | Markdown | `error-scenarios.md`，含觸發方式、處理方式、結果 |
| 5 | **Checkpoint 截圖** | PNG | 最少 5 張關鍵階段截圖（佈局完成 × 1、操作中 × 2、錯誤處理 × 1、最終 × 1） |

### 5.2 建議交付

| # | 交付物 | 說明 |
|:-|:-------|:-----|
| 6 | **測試腳本** | 可重複執行的 shell/Python 測試驅動腳本 |
| 7 | **效能分析** | 每操作類型耗時統計、瓶頸分析 |
| 8 | **比較對照** | 與 L1~L3 層級的效能對比 |

### 5.3 報告模板

```markdown
# 極致前端操作測試報告
**日期**：YYYY-MM-DD
**測試環境**：Windows 10, Hermes V8, DeepSeek-Chat

## 1. 測試設定
- 目標層級：L4 極致
- APP 數量：8
- 並行程度：6~8 同時
- 操作總步數：100
- 操作類型：Click / Type / Shortcut / Snap / Drag
- 錯誤場景：CAPTCHA / Timeout / App Crash

## 2. 結果摘要
| 指標 | 數值 |
|:-----|:-----|
| 操作成功率 | XX/100 (XX%) |
| APP 存活率 | X/8 (XX%) |
| 錯誤處理率 | X/3 (XX%) |
| 總耗時 | XX 分鐘 |
| 最終分數 | XX/100 |
| 評級 | ✅ PASS / ❌ FAIL |

## 3. 操作成功率明細
| 操作類型 | 成功/總數 | 成功率 | 連續失敗 |
|:---------|:----------|:-------|:---------|
| Click | X/Y | XX% | X |
| Type | X/Y | XX% | X |
| Shortcut | X/Y | XX% | X |
| Snap | X/Y | XX% | X |
| Drag | X/Y | XX% | X |

## 4. 錯誤場景處理
| 錯誤 | 觸發方式 | 處理結果 | 處理耗時 |
|:-----|:---------|:---------|:---------|
| CAPTCHA | browser_navigate → Google | ✅ 降級 web_search | Xs |
| Timeout | 無響應 APP × 1 | ✅ 重試 2 次後跳過 | Xs |
| App Crash | Process(kill) Obsidian | ✅ 重新啟動並繼續 | Xs |

## 5. APP 狀態
| APP | 初始 | 最終 | 狀態 |
|:----|:-----|:-----|:-----|
| Chrome | ✅ | ✅ | 存活 |
| ... | ... | ... | ... |

## 6. 瓶頸分析
- 最慢操作類型：XX (平均 Xs/步)
- 最多重試操作：XX (X 次重試)
- 主要失敗原因：XXX

## 7. 改進建議
- ... 
```

---

## 6. 已知風險與緩解

| 風險 | 影響 | 緩解方案 |
|:-----|:-----|:---------|
| Discord 6+ 處理程序 | Snap/切換失敗 | 改用任務列 Click，不用 App(switch) |
| Google reCAPTCHA | 瀏覽操作中斷 | 自動降級 web_search API |
| Notepad 多執行個體 | Windows 找不到正確視窗 | 統一用 taskkill 清除舊實例 |
| Chrome 自訂標題列 | Snap Layout flyout 不支援 | 只用 Win+Arrow 快捷鍵 |
| Win+Arrow 錯視窗 | Snap 到錯誤 APP | App(switch) 用完整標題 + Wait(1) 確認 |
| ffmpeg 錄影損壞 | 錄影無法播放 | `-t 900` 設定結束時間，不強制 kill |
| Hermes max_spawn_depth=1 | 巢狀委派不可用 | 腳本模擬取代巢狀 delegate_task |

---

## 7. 版本歷史

| 版本 | 日期 | 變更 |
|:-----|:-----|:-----|
| v1.0 | 2026-07-06 | 初始版本 — 完整測試計畫架構 |

---

## 附錄 A：操作步驟範本（前 10 步）

```
Step 001 | Phase 1 | Launch Chrome     | terminal("start chrome")
Step 002 | Phase 1 | Launch Notepad     | terminal("start notepad")
Step 003 | Phase 1 | Launch Explorer    | terminal("start explorer")
Step 004 | Phase 1 | Launch Discord     | 任務列 Click
Step 005 | Phase 1 | Snap Chrome → Q1   | Switch("Chrome") → Win+Left → Win+Up
Step 006 | Phase 1 | Snap Notepad → Q2  | Switch("Notepad") → Win+Right → Win+Up
Step 007 | Phase 1 | Snap Explorer → Q3 | Switch("Explorer") → Win+Left → Win+Down
Step 008 | Phase 1 | Snap Discord → Q4  | Switch("Discord") → Win+Right → Win+Down
Step 009 | Phase 1 | Visual verify      | Screenshot + vision_analyze
Step 010 | Phase 2 | Chrome: URL nav    | Ctrl+L → Clipboard → Ctrl+V → Enter
...
```

## 附錄 B：錯誤場景誘發指南

### E1 CAPTCHA 誘發
```python
# browser_navigate 進入 Google 搜尋
browser_navigate("https://www.google.com/search?q=hermes+agent+test")
# 預期被 reCAPTCHA 擋住 → 自動降級 web_search
```

### E2 Timeout 誘發
```python
# 對一個關閉的 Notepad 發送操作 → Timeout
WaitFor(text="notexist.txt", timeout=3)  # 超時
```

### E3 App Crash 誘發
```python
# 對正在操作的 Obsidian 執行 kill
Process(kill, name="obsidian.exe")
# 驗證測試 AGENT 是否能偵測並重啟
```
