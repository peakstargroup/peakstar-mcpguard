<div align="center">

# MCPGuard

### 你的 AI Agent 接上公司系統前，先掃一次有沒有資安破口

**MCP / Agent 安全掃描 ｜ 零相依 ｜ 靜態、本機執行、零外送 ｜ 一頁 board-ready 報告**

[繁體中文](README.md) ｜ [English](README.en.md)

`Python 3.11+` ｜ `MIT License` ｜ `0 dependencies` ｜ by [Peakstar 品得網絡數位](https://www.peakstargroup.com)

</div>

> 狀態：**骨架（skeleton，對應規格 M0）**。設定解析 + 規則引擎 + 5 維評分 + 報告
> 可端到端離線跑；CVE 對照為內建小樣本快照，`--update-cve` feed 與受監管產業
> pro 規則庫為擴充點。

---

## 為什麼現在要掃

Agent 採用很快，治理很慢。當你的 Agent 接上 ERP、會計、客戶資料的那一刻，
風險才真正開始：提示注入、工具投毒、未驗證端點、過寬權限、成本失控。2026 年
已有 30 多個 MCP 相關 CVE，其中 CVE-2025-6514（CVSS 9.6）影響數十萬個環境。

中小企業多半缺資安人力，**看不見自己有多曝險**。MCPGuard 就是來把這件事變可見的。

```bash
mcpguard scan
```

打開 `report.html`，你會拿到：

- **一個 0 到 100 的 Agent 資安總分**，配紅 / 黃 / 綠燈（安全工具採較嚴門檻）
- **五大資安維度計分卡**：驗證與存取、提示注入 / 工具投毒抗性、供應鏈與來源、動作風險 / 人為核可、成本與稽核
- **高危發現清單**，每項說明現象、為什麼危險、對照真實事件或 CVE

任一重大項（critical）命中，總分直接壓到紅燈並置頂。

---

## 用法

```bash
mcpguard scan [PATH] [選項]      # 省略 PATH 則自動探測常見設定位置
mcpguard list-rules              # 列出啟用規則
```

| 選項 | 說明 | 預設 |
|------|------|------|
| `--out <dir>` | 報告輸出目錄 | `./mcpguard-report` |
| `--lang zh\|en` | 報告語言 | `zh` |
| `--severity-min low\|med\|high` | 報告顯示的最低嚴重度 | low |
| `--fail-on high\|critical` | 命中即非零退出碼（給 CI 用） | 關 |
| `--open` | 完成後自動開啟報告 | 關 |

範例（離線，用內附樣本）：

```bash
mcpguard scan examples/dangerous --open      # 危險設定，會是紅燈
mcpguard scan examples/safe                  # 安全設定，會是綠燈
```

---

## 責任邊界（請先讀）

- 本工具是**靜態掃描的診斷輔助，不是完整資安稽核**，不構成安全保證。
- 報告只**揭露風險與「為什麼危險」，不提供可直接利用的攻擊手法 / payload**。
- 安全工具誤報傷信任、漏報更危險，因此措辭保守、每項附「為什麼」與佐證。
- CVE 對照為內建快照，報告會標示快照日期；未知設定格式標「未解析」而非報錯。

---

## 它做什麼，以及它刻意不做什麼

**MCPGuard 會做：** 對你的 MCP / Agent 設定做靜態掃描，產出資安計分卡與高危清單。

**它刻意不做（屬顧問工程）：** 不修改設定、不自動修復、不做動態 / 滲透測試，不代建最小權限架構、OAuth、稽核 / 沙箱或法遵架構。

診斷可以自動化，治療不行。針對金融、醫療、公共關係、政府等受監管產業的進階法遵規則庫與架構落地，由 Peakstar 於合作專案中提供，不在本開源倉庫內。

---

## 開發與測試

零相依，測試只用標準函式庫的 `unittest`：

```bash
py -m unittest discover -s tests -t .
```

共用的報告外觀來自 [peakstar-oss-common](https://github.com/peakstargroup/peakstar-oss-common)，以 vendoring 方式置於 `peakstar_mcpguard/_vendor/`，故本工具本身仍零相依。更新共用底座後執行 `py scripts/sync_common.py`。

---

## 授權

MIT License。見 [LICENSE](LICENSE)。

## 關於 Peakstar

Peakstar（品得網絡數位）是一家專注台灣與日本中小企業的 AI 顧問與工程交付公司。商業價值優先、誠實重於承諾。
[www.peakstargroup.com](https://www.peakstargroup.com)
